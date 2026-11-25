#!/usr/bin/env python3
"""Reproducible monthly-demand benchmark: baselines versus StatsForecast."""

from __future__ import annotations

import argparse
import json
import math
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoETS, AutoTheta, CrostonSBA

from stockout_adjustment import build_stockout_adjustment_report, load_stockout_fixture


def load_fixture(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("frequency") != "MS":
        raise ValueError("Versión o frecuencia mensual del fixture no soportada.")
    for series in data.get("series", []):
        observations = series.get("observations", [])
        if len(observations) < 36:
            raise ValueError(f"{series.get('id')}: se requieren al menos 36 meses.")
        months = [row.get("month") for row in observations]
        if months != sorted(months) or len(set(months)) != len(months):
            raise ValueError(f"{series.get('id')}: meses duplicados o fuera de orden.")
        expected = pd.date_range(months[0], periods=len(months), freq="MS").strftime("%Y-%m-%d").tolist()
        if months != expected:
            raise ValueError(f"{series.get('id')}: la serie tiene meses faltantes.")
        for row in observations:
            if not isinstance(row.get("units"), int) or row["units"] < 0:
                raise ValueError(f"{series.get('id')}: las unidades deben ser enteros no negativos.")
            if row.get("stockoutDays") != 0:
                raise ValueError(
                    f"{series.get('id')}: este benchmark exige disponibilidad completa; "
                    "los faltantes se evalúan en un escenario censurado separado."
                )
    return data


def baseline_predictions(values: list[int], horizon: int) -> dict[str, list[float]]:
    if len(values) < 12:
        raise ValueError("Se necesitan al menos 12 observaciones para la línea estacional.")
    moving_average_3 = sum(values[-3:]) / 3.0
    moving_average_12 = sum(values[-12:]) / 12.0
    return {
        "NaiveLastValue": [float(values[-1])] * horizon,
        "SeasonalNaive12": [float(value) for value in values[-12:-12 + horizon]],
        "MovingAverage3": [moving_average_3] * horizon,
        "MovingAverage12": [moving_average_12] * horizon,
    }


def statsforecast_prediction(model: Any, series_id: str, observations: list[dict[str, Any]], origin: int, horizon: int) -> list[float]:
    train = observations[:origin]
    frame = pd.DataFrame({
        "unique_id": [series_id] * len(train),
        "ds": pd.to_datetime([row["month"] for row in train]),
        "y": [row["units"] for row in train],
    })
    runner = StatsForecast(models=[model], freq="MS", n_jobs=1)
    result = runner.forecast(df=frame, h=horizon).sort_values("ds")
    model_columns = [column for column in result.columns if column not in {"unique_id", "ds"}]
    if len(model_columns) != 1:
        raise RuntimeError(f"Salida inesperada de StatsForecast: {result.columns.tolist()}")
    predictions = [max(0.0, float(value)) for value in result[model_columns[0]].tolist()]
    if len(predictions) != horizon or not all(math.isfinite(value) for value in predictions):
        raise RuntimeError(f"Predicción no válida para {series_id}.")
    return predictions


def score(actual: list[int], predicted: list[float]) -> dict[str, float | int]:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("Los vectores de observaciones y pronósticos no coinciden.")
    errors = [pred - observed for observed, pred in zip(actual, predicted)]
    absolute = [abs(error) for error in errors]
    denominator = sum(abs(value) for value in actual)
    return {
        "observations": len(actual),
        "MAE": round(sum(absolute) / len(absolute), 6),
        "WAPE": round(sum(absolute) / denominator, 6) if denominator else 0.0,
        "bias": round(sum(errors) / denominator, 6) if denominator else 0.0,
    }


def benchmark_series(series: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    observations = series["observations"]
    values = [row["units"] for row in observations]
    horizon = int(config["horizonMonths"])
    origins = [int(value) for value in config["rollingOriginsMonths"]]
    if not origins or any(origin < 24 or origin + horizon > len(values) for origin in origins):
        raise ValueError(f"Orígenes de backtesting inválidos para {series['id']}.")

    if series["demandType"] == "regular":
        models = [AutoETS(season_length=12), AutoTheta(season_length=12)]
    elif series["demandType"] == "intermittent":
        models = [CrostonSBA()]
    else:
        raise ValueError(f"Tipo de demanda desconocido: {series['demandType']}")

    predictions: dict[str, list[float]] = {}
    actuals: list[int] = []
    folds: list[dict[str, Any]] = []
    for fold_number, origin in enumerate(origins, start=1):
        actual = values[origin:origin + horizon]
        actuals.extend(actual)
        fold_predictions = baseline_predictions(values[:origin], horizon)
        for model in models:
            name = type(model).__name__
            fold_predictions[name] = statsforecast_prediction(model, series["id"], observations, origin, horizon)
        for name, forecast in fold_predictions.items():
            predictions.setdefault(name, []).extend(forecast)
        folds.append({
            "fold": fold_number,
            "trainingMonths": origin,
            "trainingThrough": observations[origin - 1]["month"],
            "testFrom": observations[origin]["month"],
            "testThrough": observations[origin + horizon - 1]["month"],
            "actual": actual,
            "predictions": {name: [round(value, 6) for value in forecast] for name, forecast in sorted(fold_predictions.items())},
        })

    summary = [{"model": name, **score(actuals, forecast)} for name, forecast in predictions.items()]
    summary.sort(key=lambda row: (float(row["WAPE"]), float(row["MAE"]), str(row["model"])))
    return {
        "seriesId": series["id"],
        "demandType": series["demandType"],
        "evaluationOrigins": origins,
        "horizonMonths": horizon,
        "summaryByWAPE": summary,
        "folds": folds,
        "selectionNote": "El primer lugar es sólo el resultado de este fixture sintético; no autoriza elegir un modelo productivo.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path("docs/fixtures/demand-monthly-history.json"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--stockout-fixture", type=Path, default=Path("docs/fixtures/stockout-censored-demand.json"))
    args = parser.parse_args()
    try:
        data = load_fixture(args.fixture)
        stockout_data = load_stockout_fixture(args.stockout_fixture)
        report = {
            "benchmarkVersion": 1,
            "fixturePurpose": data["purpose"],
            "fixtureRange": [data["startMonth"], data["endMonth"]],
            "statsforecastVersion": version("statsforecast"),
            "pandasVersion": version("pandas"),
            "evaluation": data["evaluation"],
            "results": [benchmark_series(series, data["evaluation"]) for series in data["series"]],
            "stockoutAdjustment": build_stockout_adjustment_report(stockout_data),
            "limitations": [
                "Datos 100% sintéticos; no representan una tienda ni precios/ventas reales.",
                "El fixture temporal regular/intermitente no contiene quiebres; el ajuste censurado se evalúa aparte con otro fixture sintético.",
                "El benchmark compara ventanas históricas y horizonte mensual de tres meses; no cubre aún variables exógenas.",
                "Los resultados no seleccionan automáticamente un modelo para producción.",
            ],
        }
        rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (OSError, ValueError, KeyError, PackageNotFoundError, RuntimeError) as exc:
        print(f"Error en el benchmark de demanda: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
