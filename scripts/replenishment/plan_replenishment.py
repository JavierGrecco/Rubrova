#!/usr/bin/env python3
"""Read-only, time-phased replenishment planning experiment.

Quantities use integer milli-units (the same 3-decimal precision used by
MyCompany's inventory ledgers). This module never creates purchase orders or
changes inventory. It consumes normalized open commitments and confirmed
supplier receipts supplied by an adapter in a future integration.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


MIN_FORECAST_PERIODS = 12
MIN_FORECAST_COVERAGE = 0.50
MAX_LEAD_OR_REVIEW_DAYS = 365

INCOMING_STATUSES = {"confirmed", "in_transit", "draft", "sent", "cancelled", "received"}
COUNTED_INCOMING_STATUSES = {"confirmed", "in_transit"}
OUTGOING_STATUSES = {"waiting", "ready", "confirmed", "draft", "cancelled", "done"}
COUNTED_OUTGOING_STATUSES = {"waiting", "ready", "confirmed"}


def _integer(value: Any, field: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        qualifier = "positivo" if minimum == 1 else "no negativo"
        raise ValueError(f"{field} debe ser un entero {qualifier}.")
    return value


def _label(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} debe ser texto no vacío.")
    return value.strip()


def _iso_date(value: Any, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} debe ser una fecha ISO YYYY-MM-DD.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} debe ser una fecha ISO YYYY-MM-DD.") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{field} debe usar exactamente el formato YYYY-MM-DD.")
    return parsed


def _events(
    rows: Any,
    field: str,
    *,
    allowed_statuses: set[str],
    quantity_field: str = "quantityMilli",
    has_reserved: bool = False,
) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError(f"{field} debe ser una lista.")
    result: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"{field}[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{prefix} debe ser un objeto.")
        event_id = _label(row.get("id"), f"{prefix}.id")
        if event_id in seen_ids:
            raise ValueError(f"{field} contiene id duplicado: {event_id}.")
        seen_ids.add(event_id)

        status = _label(row.get("status"), f"{prefix}.status").lower()
        if status not in allowed_statuses:
            raise ValueError(f"{prefix}.status no soportado: {status}.")
        quantity = _integer(row.get(quantity_field), f"{prefix}.{quantity_field}", minimum=1)
        due = _iso_date(row.get("dueDate"), f"{prefix}.dueDate")
        event: dict[str, Any] = {
            "id": event_id,
            "status": status,
            "quantity": quantity,
            "due_date": due,
        }
        if has_reserved:
            reserved = _integer(row.get("reservedMilli"), f"{prefix}.reservedMilli")
            if reserved > quantity:
                raise ValueError(f"{prefix}.reservedMilli no puede superar quantityMilli.")
            event["reserved"] = reserved
        result.append(event)
    return result


def _round_order_quantity(gap: int, minimum: int, multiple: int) -> int:
    if gap <= 0:
        return 0
    target = max(gap, minimum)
    return ((target + multiple - 1) // multiple) * multiple


def plan_replenishment(item: dict[str, Any]) -> dict[str, Any]:
    """Calculate a deterministic replenishment suggestion without side effects.

    Contract:
    - outgoing quantity is the still-open commitment, net of already shipped units;
    - reservedMilli is a subset of that same outgoing quantity, never an extra
      demand line; it reduces free stock now but is deducted only once in the
      time-phased projection;
    - dailyDemandMilli is uncommitted forecast demand and must exclude the
      outgoing commitments above;
    - only confirmed/in-transit receipts due within the planning horizon count
      as incoming supply; draft, merely sent, received, cancelled and overdue
      records are excluded;
    - same-day outgoing/forecast demand is applied before incoming receipts,
      a conservative ordering when intraday timestamps are unavailable.
    """
    if not isinstance(item, dict):
        raise ValueError("La fila de planificación debe ser un objeto.")

    sku = _label(item.get("sku"), "sku")
    location = _label(item.get("location"), "location")
    as_of = _iso_date(item.get("asOf"), "asOf")

    on_hand = _integer(item.get("onHandMilli"), "onHandMilli")
    daily_demand = _integer(item.get("dailyDemandMilli"), "dailyDemandMilli")
    eligible_periods = _integer(item.get("forecastEligiblePeriods"), "forecastEligiblePeriods")
    total_periods = _integer(item.get("forecastTotalPeriods"), "forecastTotalPeriods")
    if eligible_periods > total_periods:
        raise ValueError("forecastEligiblePeriods no puede superar forecastTotalPeriods.")

    lead_days = _integer(item.get("supplierLeadTimeDays"), "supplierLeadTimeDays", minimum=1)
    review_days = _integer(item.get("reviewPeriodDays"), "reviewPeriodDays", minimum=1)
    if lead_days > MAX_LEAD_OR_REVIEW_DAYS or review_days > MAX_LEAD_OR_REVIEW_DAYS:
        raise ValueError(f"lead time y período de revisión no pueden superar {MAX_LEAD_OR_REVIEW_DAYS} días.")
    horizon_days = lead_days + review_days
    horizon_end = as_of + timedelta(days=horizon_days)

    safety_stock = _integer(item.get("safetyStockMilli"), "safetyStockMilli")
    minimum_order = _integer(item.get("minimumOrderQuantityMilli"), "minimumOrderQuantityMilli")
    order_multiple = _integer(item.get("orderMultipleMilli"), "orderMultipleMilli", minimum=1)

    incoming = _events(
        item.get("incoming", []),
        "incoming",
        allowed_statuses=INCOMING_STATUSES,
    )
    outgoing = _events(
        item.get("outgoing", []),
        "outgoing",
        allowed_statuses=OUTGOING_STATUSES,
        has_reserved=True,
    )

    # Open reservations are part of outgoing commitments. Count them once for
    # free-to-promise, but do not subtract them again from the projected ledger.
    active_outgoing = [row for row in outgoing if row["status"] in COUNTED_OUTGOING_STATUSES]
    reserved_total = sum(row["reserved"] for row in active_outgoing)
    available_now = on_hand - reserved_total

    forecast_coverage = eligible_periods / total_periods if total_periods else 0.0
    base = {
        "sku": sku,
        "location": location,
        "asOf": as_of.isoformat(),
        "status": None,
        "reason": None,
        "forecastEligiblePeriods": eligible_periods,
        "forecastTotalPeriods": total_periods,
        "forecastCoverage": round(forecast_coverage, 6),
        "coverageDays": horizon_days,
        "supplierLeadTimeDays": lead_days,
        "reviewPeriodDays": review_days,
        "onHandMilli": on_hand,
        "reservedMilli": reserved_total,
        "availableNowMilli": available_now,
        "dailyUncommittedForecastMilli": daily_demand,
        "safetyStockMilli": safety_stock,
        "minimumOrderQuantityMilli": minimum_order,
        "orderMultipleMilli": order_multiple,
        "firmOutgoingInHorizonMilli": 0,
        "confirmedIncomingInHorizonMilli": 0,
        "includedOutgoingCount": 0,
        "includedIncomingCount": 0,
        "excludedOutgoingByReason": {},
        "excludedIncomingByReason": {},
        "projectedEndBeforeOrderMilli": None,
        "projectedEndAfterRecommendedOrderMilli": None,
        "minimumProjectedStockBeforeReceiptsMilli": None,
        "minimumProjectedStockDate": None,
        "stockoutBeforeReplenishment": None,
        "reorderGapMilli": None,
        "recommendedOrderQtyMilli": None,
        "assumptions": [
            "La demanda diaria es un pronóstico no comprometido; no incluye pedidos de salida listados.",
            "Las reservas son una parte de los compromisos de salida y no se descuentan dos veces.",
            "Sólo se cuenta suministro de proveedor confirmado o en tránsito, no vencido y dentro del horizonte.",
            "Se descuenta demanda y salida antes de sumar recepciones del mismo día.",
            "El pedido sugerido llegaría al final del lead time; no corrige faltantes anteriores a esa fecha.",
        ],
    }

    if reserved_total > on_hand:
        base["status"] = "DATA_REVIEW"
        base["reason"] = "RESERVATIONS_EXCEED_ON_HAND"
        return base

    if (
        eligible_periods < MIN_FORECAST_PERIODS
        or total_periods == 0
        or forecast_coverage < MIN_FORECAST_COVERAGE
    ):
        base["status"] = "SUPPRESSED"
        base["reason"] = "INSUFFICIENT_FORECAST_HISTORY_OR_COVERAGE"
        return base

    incoming_by_day: dict[int, int] = {}
    outgoing_by_day: dict[int, int] = {}
    excluded_incoming: dict[str, int] = {}
    excluded_outgoing: dict[str, int] = {}
    incoming_in_horizon = 0
    outgoing_in_horizon = 0
    included_incoming_count = 0
    included_outgoing_count = 0

    def add_reason(bucket: dict[str, int], reason: str) -> None:
        bucket[reason] = bucket.get(reason, 0) + 1

    for row in incoming:
        status = row["status"]
        if status == "cancelled":
            add_reason(excluded_incoming, "CANCELLED")
            continue
        if status == "received":
            add_reason(excluded_incoming, "ALREADY_RECEIVED")
            continue
        if status not in COUNTED_INCOMING_STATUSES:
            add_reason(excluded_incoming, "NOT_CONFIRMED")
            continue
        if row["due_date"] < as_of:
            add_reason(excluded_incoming, "PAST_DUE")
            continue
        day = (row["due_date"] - as_of).days
        if day > horizon_days:
            add_reason(excluded_incoming, "AFTER_COVERAGE")
            continue
        incoming_by_day[day] = incoming_by_day.get(day, 0) + row["quantity"]
        incoming_in_horizon += row["quantity"]
        included_incoming_count += 1

    for row in outgoing:
        status = row["status"]
        if status == "cancelled":
            add_reason(excluded_outgoing, "CANCELLED")
            continue
        if status == "done":
            add_reason(excluded_outgoing, "ALREADY_SHIPPED")
            continue
        if status not in COUNTED_OUTGOING_STATUSES:
            add_reason(excluded_outgoing, "NOT_FIRM")
            continue
        if row["due_date"] > horizon_end:
            add_reason(excluded_outgoing, "AFTER_COVERAGE")
            continue
        day = max(0, (row["due_date"] - as_of).days)
        outgoing_by_day[day] = outgoing_by_day.get(day, 0) + row["quantity"]
        outgoing_in_horizon += row["quantity"]
        included_outgoing_count += 1

    # Apply overdue/current-day open shipments before the first forecast day.
    stock = on_hand - outgoing_by_day.get(0, 0)
    min_stock = stock
    min_stock_date = as_of
    min_before_receipts = stock
    min_before_receipts_date = as_of
    stockout_before_replenishment = stock < 0
    stock += incoming_by_day.get(0, 0)
    if stock < min_stock:
        min_stock = stock
        min_stock_date = as_of

    for day in range(1, horizon_days + 1):
        current_date = as_of + timedelta(days=day)
        stock -= daily_demand + outgoing_by_day.get(day, 0)
        if stock < min_before_receipts:
            min_before_receipts = stock
            min_before_receipts_date = current_date
        if day <= lead_days and stock < 0:
            stockout_before_replenishment = True

        stock += incoming_by_day.get(day, 0)
        if stock < min_stock:
            min_stock = stock
            min_stock_date = current_date

    gap = max(safety_stock - stock, 0)
    recommended = _round_order_quantity(gap, minimum_order, order_multiple)
    status = (
        "EXPEDITE_REQUIRED"
        if stockout_before_replenishment
        else "ORDER_RECOMMENDED"
        if recommended > 0
        else "NO_ORDER_NEEDED"
    )
    reason = (
        "PROJECTED_SHORTAGE_BEFORE_NEW_SUPPLY"
        if stockout_before_replenishment
        else "PROJECTED_BELOW_SAFETY_STOCK"
        if recommended > 0
        else None
    )

    base.update({
        "status": status,
        "reason": reason,
        "firmOutgoingInHorizonMilli": outgoing_in_horizon,
        "confirmedIncomingInHorizonMilli": incoming_in_horizon,
        "includedOutgoingCount": included_outgoing_count,
        "includedIncomingCount": included_incoming_count,
        "excludedOutgoingByReason": dict(sorted(excluded_outgoing.items())),
        "excludedIncomingByReason": dict(sorted(excluded_incoming.items())),
        "projectedEndBeforeOrderMilli": stock,
        "projectedEndAfterRecommendedOrderMilli": stock + recommended,
        "minimumProjectedStockBeforeReceiptsMilli": min_before_receipts,
        "minimumProjectedStockDate": min_before_receipts_date.isoformat(),
        "minimumProjectedEndOfDayMilli": min_stock,
        "minimumProjectedEndOfDayDate": min_stock_date.isoformat(),
        "stockoutBeforeReplenishment": stockout_before_replenishment,
        "reorderGapMilli": gap,
        "recommendedOrderQtyMilli": recommended,
    })
    return base


def load_fixture(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer el fixture: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schemaVersion") != 1:
        raise ValueError("schemaVersion del fixture de reposición debe ser 1.")
    if payload.get("purpose") != "synthetic-read-only-replenishment-planning":
        raise ValueError("El propósito del fixture no está soportado.")
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("El fixture debe contener escenarios.")
    seen: set[str] = set()
    for index, scenario in enumerate(scenarios):
        if not isinstance(scenario, dict):
            raise ValueError(f"scenarios[{index}] debe ser un objeto.")
        scenario_id = _label(scenario.get("id"), f"scenarios[{index}].id")
        if scenario_id in seen:
            raise ValueError(f"El fixture contiene escenario duplicado: {scenario_id}.")
        seen.add(scenario_id)
        plan_replenishment(scenario.get("item"))
    return payload


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    results = []
    counts: dict[str, int] = {}
    for scenario in payload["scenarios"]:
        result = plan_replenishment(scenario["item"])
        expected_status = scenario.get("expectedStatus")
        expected_quantity = scenario.get("expectedOrderQtyMilli")
        if result["status"] != expected_status:
            raise ValueError(
                f"{scenario['id']}: status esperado {expected_status}, obtenido {result['status']}."
            )
        if result["recommendedOrderQtyMilli"] != expected_quantity:
            raise ValueError(
                f"{scenario['id']}: cantidad esperada {expected_quantity}, "
                f"obtenida {result['recommendedOrderQtyMilli']}."
            )
        counts[result["status"]] = counts.get(result["status"], 0) + 1
        results.append({"scenarioId": scenario["id"], **result})
    return {
        "plannerVersion": 1,
        "purpose": payload["purpose"],
        "syntheticOnly": True,
        "readOnly": True,
        "scenarioCount": len(results),
        "statusCounts": dict(sorted(counts.items())),
        "scenarios": results,
        "limitations": [
            "Fixture 100% sintético; no prueba exactitud sobre datos de un comercio real.",
            "La demanda diaria se supone uniforme; aún no modela calendario, promociones, precios ni sustitución.",
            "Los pedidos firmes deben llegar netos de cantidades ya despachadas.",
            "Las recepciones sólo cuentan cuando están confirmadas/en tránsito, no vencidas y dentro del horizonte.",
            "No calcula presupuesto, costo financiero, selección de proveedor ni restricciones de capacidad.",
            "No crea, confirma ni modifica órdenes de compra, reservas, ventas o inventario.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evalúa un planificador sintético y de solo lectura de reposición.")
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    report = build_report(load_fixture(args.fixture))
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
