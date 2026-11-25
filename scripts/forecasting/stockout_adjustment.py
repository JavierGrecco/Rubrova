#!/usr/bin/env python3
"""Conservative availability adjustment for censored retail demand.

This module is an evaluation aid, not a production forecasting model. It assumes
that demand on stocked opening days is representative of the days lost to a
stockout. It deliberately suppresses estimates when availability is too low.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


def _non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} debe ser un entero no negativo.")
    return value


def adjust_observation(
    observation: dict[str, Any],
    *,
    min_available_days: int = 10,
    min_availability_ratio: float = 0.50,
) -> dict[str, Any]:
    """Estimate demand for a month after discounting days without stock.

    A result is withheld when there are too few stocked days or availability
    falls below the configured threshold. The latent-demand field, when present
    in a synthetic fixture, is intentionally ignored by this function.
    """
    if isinstance(min_available_days, bool) or not isinstance(min_available_days, int) or min_available_days < 1:
        raise ValueError("min_available_days debe ser un entero positivo.")
    if (
        isinstance(min_availability_ratio, bool)
        or not isinstance(min_availability_ratio, (int, float))
        or not math.isfinite(float(min_availability_ratio))
        or not 0 < min_availability_ratio <= 1
    ):
        raise ValueError("min_availability_ratio debe ser un número finito entre 0 y 1.")

    units = _non_negative_int(observation.get("units"), "units")
    open_days = _non_negative_int(observation.get("openDays"), "openDays")
    stockout_days = _non_negative_int(observation.get("stockoutDays"), "stockoutDays")
    if stockout_days > open_days:
        raise ValueError("stockoutDays no puede superar openDays.")

    if open_days == 0:
        return {
            "observedUnits": units,
            "estimatedDemandUnits": None,
            "openDays": open_days,
            "stockoutDays": stockout_days,
            "availableDays": 0,
            "availabilityRatio": None,
            "status": "suppressed",
            "reason": "NO_OPEN_DAYS",
        }

    available_days = open_days - stockout_days
    ratio = available_days / open_days
    if available_days == 0:
        reason = "NO_AVAILABLE_DAYS"
    elif available_days < min_available_days:
        reason = "TOO_FEW_AVAILABLE_DAYS"
    elif ratio < min_availability_ratio:
        reason = "LOW_AVAILABILITY"
    else:
        reason = None

    if reason:
        return {
            "observedUnits": units,
            "estimatedDemandUnits": None,
            "openDays": open_days,
            "stockoutDays": stockout_days,
            "availableDays": available_days,
            "availabilityRatio": round(ratio, 6),
            "status": "suppressed",
            "reason": reason,
        }

    estimate = units / ratio
    return {
        "observedUnits": units,
        "estimatedDemandUnits": round(estimate, 6),
        "openDays": open_days,
        "stockoutDays": stockout_days,
        "availableDays": available_days,
        "availabilityRatio": round(ratio, 6),
        "status": "adjusted" if stockout_days else "observed",
        "reason": None,
    }


def _score(actual: list[int], predicted: list[float]) -> dict[str, float | int]:
    if not actual or len(actual) != len(predicted):
        raise ValueError("Se requieren vectores no vacíos de igual longitud.")
    errors = [prediction - value for value, prediction in zip(actual, predicted)]
    denominator = sum(actual)
    return {
        "observations": len(actual),
        "MAE": round(sum(abs(error) for error in errors) / len(errors), 6),
        "WAPE": round(sum(abs(error) for error in errors) / denominator, 6) if denominator else 0.0,
        "bias": round(sum(errors) / denominator, 6) if denominator else 0.0,
    }


def load_stockout_fixture(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("frequency") != "MS":
        raise ValueError("Versión o frecuencia del fixture de quiebres no soportada.")
    observations = data.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("El fixture debe contener observaciones.")
    seen: set[str] = set()
    previous: date | None = None
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError("Cada observación debe ser un objeto.")
        month = row.get("month")
        if not isinstance(month, str) or len(month) != 10:
            raise ValueError("Cada observación debe tener month en formato YYYY-MM-DD.")
        parsed = date.fromisoformat(month)
        if parsed.day != 1 or month in seen or (previous and parsed <= previous):
            raise ValueError("Los meses deben ser únicos, ordenados y comenzar el día 1.")
        if previous:
            next_month = 1 if previous.month == 12 else previous.month + 1
            next_year = previous.year + (1 if previous.month == 12 else 0)
            if parsed != date(next_year, next_month, 1):
                raise ValueError("La serie mensual contiene meses faltantes.")
        seen.add(month)
        previous = parsed
        adjust_observation(row)
        _non_negative_int(row.get("latentDemandUnits"), "latentDemandUnits")
        if row["latentDemandUnits"] < row["units"]:
            raise ValueError("latentDemandUnits no puede ser menor que units en este fixture.")
    return data


def build_stockout_adjustment_report(
    data: dict[str, Any],
    *,
    min_available_days: int = 10,
    min_availability_ratio: float = 0.50,
) -> dict[str, Any]:
    """Compare observed sales with the availability-adjusted estimate.

    latentDemandUnits is used only as synthetic scoring truth after adjustment.
    It is never supplied to adjust_observation().
    """
    rows: list[dict[str, Any]] = []
    eligible_actual: list[int] = []
    observed_predictions: list[float] = []
    adjusted_predictions: list[float] = []
    exclusions: dict[str, int] = {}

    for observation in data["observations"]:
        result = adjust_observation(
            observation,
            min_available_days=min_available_days,
            min_availability_ratio=min_availability_ratio,
        )
        row = {"month": observation["month"], **result}
        rows.append(row)
        if result["estimatedDemandUnits"] is None:
            reason = str(result["reason"])
            exclusions[reason] = exclusions.get(reason, 0) + 1
            continue
        eligible_actual.append(observation["latentDemandUnits"])
        observed_predictions.append(float(observation["units"]))
        adjusted_predictions.append(float(result["estimatedDemandUnits"]))

    eligible_count = len(eligible_actual)
    if not eligible_count:
        raise ValueError("No hay períodos con disponibilidad suficiente para evaluar.")
    return {
        "method": "stocked-days-rate-adjustment",
        "assumptions": [
            "La demanda por día de apertura es aproximadamente uniforme dentro del período.",
            "Los días sin stock están registrados correctamente por producto y ubicación.",
            "La corrección estima demanda no observada; no crea ventas, ingresos ni movimientos de inventario.",
        ],
        "thresholds": {
            "minAvailableDays": min_available_days,
            "minAvailabilityRatio": min_availability_ratio,
        },
        "periods": len(rows),
        "eligiblePeriods": eligible_count,
        "coverage": round(eligible_count / len(rows), 6),
        "excludedByReason": dict(sorted(exclusions.items())),
        "sameEligiblePeriods": {
            "observedSalesVsSyntheticTruth": _score(eligible_actual, observed_predictions),
            "availabilityAdjustedVsSyntheticTruth": _score(eligible_actual, adjusted_predictions),
        },
        "observations": rows,
        "limitations": [
            "Fixture 100% sintético; no representa ventas ni precisión de una tienda real.",
            "La tasa de demanda de los días disponibles puede diferir de la de los días agotados.",
            "La regla no modela sustitución, promociones, precio, clima, calendario ni demanda perdida observada.",
            "Los períodos con baja disponibilidad se excluyen; no se extrapolan.",
            "Este ajuste no sustituye un modelo temporal ni autoriza compras automáticas.",
        ],
    }
