#!/usr/bin/env python3
"""Normalize a read-only MyCompany 6.2 export for the Rubrova planner.

This adapter reads a JSON snapshot only. It has no database driver, network
client, lsFusion session, or write path. The native export that produces the
snapshot is intentionally a separate, later integration step.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from plan_replenishment import plan_replenishment


SOURCE_SEMANTICS = {
    "inventory": "InvLedger.onHand_exact_location",
    "outgoingQuantity": "ShipmentLine.openRemaining",
    "outgoingReservation": "ShipmentResLedger.lineReserved",
    "incomingQuantity": "ReceiptResLedger.expectedRemaining",
    "incomingDate": "Receipt.scheduledDateTime",
    "incomingEligibility": "Receipt.ready_and_PurchaseOrder.confirmed",
}

SHIPMENT_STATUSES = {"draft", "waiting", "ready", "done", "cancelled"}
RECEIPT_STATUSES = {"draft", "ready", "done", "cancelled"}
PURCHASE_ORDER_STATUSES = {"draft", "sent", "confirmed", "cancelled"}


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} debe ser un objeto.")
    return value


def _rows(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field} debe ser una lista.")
    return [_object(row, f"{field}[{index}]") for index, row in enumerate(value)]


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} debe ser texto no vacío.")
    return value.strip()


def _integer(value: Any, field: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        qualifier = "positivo" if minimum == 1 else "no negativo"
        raise ValueError(f"{field} debe ser un entero {qualifier}.")
    return value


def _date(value: Any, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} debe ser una fecha ISO YYYY-MM-DD.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} debe ser una fecha ISO YYYY-MM-DD.") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{field} debe usar exactamente el formato YYYY-MM-DD.")
    return parsed


def _status(value: Any, field: str, allowed: set[str]) -> str:
    status = _text(value, field).lower()
    if status not in allowed:
        raise ValueError(f"{field} no soportado: {status}.")
    return status


def _count(bucket: Counter[str], reason: str) -> None:
    bucket[reason] += 1


def load_snapshot(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer el snapshot MyCompany: {exc}") from exc
    return _validate_snapshot(payload)


def _validate_snapshot(payload: Any) -> dict[str, Any]:
    snapshot = _object(payload, "snapshot")
    if snapshot.get("schemaVersion") != 1:
        raise ValueError("schemaVersion del snapshot MyCompany debe ser 1.")
    if snapshot.get("snapshotType") != "read-only-replenishment-snapshot":
        raise ValueError("snapshotType no corresponde a una extracción de reposición de solo lectura.")
    if snapshot.get("sourceSystem") != "MyCompany" or snapshot.get("sourceVersion") != "6.2":
        raise ValueError("El adaptador sólo acepta snapshots de MyCompany 6.2.")
    _date(snapshot.get("asOf"), "asOf")
    if snapshot.get("sourceSemantics") != SOURCE_SEMANTICS:
        raise ValueError("sourceSemantics no coincide con el contrato MyCompany 6.2 documentado.")
    for name in ("inventory", "shipments", "receipts", "planningInputs"):
        _rows(snapshot.get(name), name)
    if not snapshot["inventory"]:
        raise ValueError("inventory no puede estar vacío.")
    if not snapshot["planningInputs"]:
        raise ValueError("planningInputs no puede estar vacío.")
    return snapshot


def adapt_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Convert a validated MyCompany snapshot into deterministic planner input."""
    snapshot = _validate_snapshot(snapshot)
    as_of = snapshot["asOf"]

    inventory: dict[tuple[str, str], int] = {}
    for index, row in enumerate(snapshot["inventory"]):
        prefix = f"inventory[{index}]"
        product_id = _text(row.get("productId"), f"{prefix}.productId")
        location_id = _text(row.get("locationId"), f"{prefix}.locationId")
        key = (product_id, location_id)
        if key in inventory:
            raise ValueError(f"inventory contiene producto/ubicación duplicado: {product_id}/{location_id}.")
        inventory[key] = _integer(row.get("onHandMilli"), f"{prefix}.onHandMilli")

    items: dict[tuple[str, str], dict[str, Any]] = {}
    native_auto_order: dict[tuple[str, str], int | None] = {}
    for index, row in enumerate(snapshot["planningInputs"]):
        prefix = f"planningInputs[{index}]"
        product_id = _text(row.get("productId"), f"{prefix}.productId")
        location_id = _text(row.get("locationId"), f"{prefix}.locationId")
        key = (product_id, location_id)
        if key in items:
            raise ValueError(f"planningInputs contiene producto/ubicación duplicado: {product_id}/{location_id}.")
        if key not in inventory:
            raise ValueError(f"{prefix} no tiene existencia física en inventory.")
        item = {
            "sku": _text(row.get("sku"), f"{prefix}.sku"),
            "location": _text(row.get("locationName"), f"{prefix}.locationName"),
            "asOf": as_of,
            "onHandMilli": inventory[key],
            "dailyDemandMilli": _integer(row.get("dailyDemandMilli"), f"{prefix}.dailyDemandMilli"),
            "forecastEligiblePeriods": _integer(
                row.get("forecastEligiblePeriods"), f"{prefix}.forecastEligiblePeriods"
            ),
            "forecastTotalPeriods": _integer(
                row.get("forecastTotalPeriods"), f"{prefix}.forecastTotalPeriods"
            ),
            "supplierLeadTimeDays": _integer(
                row.get("supplierLeadTimeDays"), f"{prefix}.supplierLeadTimeDays", minimum=1
            ),
            "reviewPeriodDays": _integer(row.get("reviewPeriodDays"), f"{prefix}.reviewPeriodDays", minimum=1),
            "safetyStockMilli": _integer(row.get("safetyStockMilli"), f"{prefix}.safetyStockMilli"),
            "minimumOrderQuantityMilli": _integer(
                row.get("minimumOrderQuantityMilli"), f"{prefix}.minimumOrderQuantityMilli"
            ),
            "orderMultipleMilli": _integer(
                row.get("orderMultipleMilli"), f"{prefix}.orderMultipleMilli", minimum=1
            ),
            "incoming": [],
            "outgoing": [],
        }
        native = row.get("nativeAutoOrderQtyMilli")
        native_auto_order[key] = (
            None if native is None
            else _integer(native, f"{prefix}.nativeAutoOrderQtyMilli")
        )
        items[key] = item

    seen_shipment_lines: set[str] = set()
    excluded_outgoing: Counter[str] = Counter()
    for index, row in enumerate(snapshot["shipments"]):
        prefix = f"shipments[{index}]"
        line_id = _text(row.get("lineId"), f"{prefix}.lineId")
        if line_id in seen_shipment_lines:
            raise ValueError(f"shipments contiene lineId duplicado: {line_id}.")
        seen_shipment_lines.add(line_id)
        _text(row.get("shipmentId"), f"{prefix}.shipmentId")
        product_id = _text(row.get("productId"), f"{prefix}.productId")
        location_id = _text(row.get("locationId"), f"{prefix}.locationId")
        status = _status(row.get("status"), f"{prefix}.status", SHIPMENT_STATUSES)
        due_date = _date(row.get("scheduledDate"), f"{prefix}.scheduledDate")
        quantity = _integer(row.get("openQuantityMilli"), f"{prefix}.openQuantityMilli")
        reserved = _integer(row.get("lineReservedMilli"), f"{prefix}.lineReservedMilli")
        if status not in {"waiting", "ready"}:
            reason = {
                "draft": "NOT_FIRM",
                "done": "ALREADY_SHIPPED",
                "cancelled": "CANCELLED",
            }[status]
            _count(excluded_outgoing, reason)
            continue
        if quantity == 0:
            raise ValueError(f"{prefix}.openQuantityMilli debe ser positivo para un despacho abierto.")
        if reserved > quantity:
            raise ValueError(f"{prefix}.lineReservedMilli no puede superar openQuantityMilli.")
        key = (product_id, location_id)
        if key not in items:
            raise ValueError(f"{prefix} no tiene planningInputs para {product_id}/{location_id}.")
        items[key]["outgoing"].append({
            "id": f"shipment:{line_id}",
            "status": status,
            "dueDate": due_date.isoformat(),
            "quantityMilli": quantity,
            "reservedMilli": reserved,
        })

    seen_receipt_lines: set[str] = set()
    seen_purchase_order_lines: set[str] = set()
    excluded_incoming: Counter[str] = Counter()
    for index, row in enumerate(snapshot["receipts"]):
        prefix = f"receipts[{index}]"
        line_id = _text(row.get("lineId"), f"{prefix}.lineId")
        if line_id in seen_receipt_lines:
            raise ValueError(f"receipts contiene lineId duplicado: {line_id}.")
        seen_receipt_lines.add(line_id)
        _text(row.get("receiptId"), f"{prefix}.receiptId")
        product_id = _text(row.get("productId"), f"{prefix}.productId")
        location_id = _text(row.get("locationId"), f"{prefix}.locationId")
        status = _status(row.get("status"), f"{prefix}.status", RECEIPT_STATUSES)
        po_status_value = row.get("purchaseOrderStatus")
        po_status = (
            "unlinked"
            if po_status_value is None
            else _status(po_status_value, f"{prefix}.purchaseOrderStatus", PURCHASE_ORDER_STATUSES)
        )
        due_date = _date(row.get("scheduledDate"), f"{prefix}.scheduledDate")
        quantity = _integer(row.get("expectedQuantityMilli"), f"{prefix}.expectedQuantityMilli")
        increase_available = row.get("increaseAvailableStock")
        if not isinstance(increase_available, bool):
            raise ValueError(f"{prefix}.increaseAvailableStock debe ser booleano.")

        if status == "done":
            _count(excluded_incoming, "ALREADY_RECEIVED")
            continue
        if status == "cancelled":
            _count(excluded_incoming, "CANCELLED")
            continue
        if status == "draft":
            _count(excluded_incoming, "NOT_READY")
            continue
        if po_status != "confirmed":
            _count(excluded_incoming, "NOT_CONFIRMED_PURCHASE_ORDER")
            continue
        if increase_available:
            raise ValueError(
                f"{prefix} usa increaseAvailableStock=true; este adaptador aún no modela "
                "esa política de disponibilidad nativa y detiene la importación."
            )
        if quantity == 0:
            raise ValueError(f"{prefix}.expectedQuantityMilli debe ser positivo para una recepción pendiente.")
        _text(row.get("purchaseOrderId"), f"{prefix}.purchaseOrderId")
        purchase_order_line_id = _text(row.get("purchaseOrderLineId"), f"{prefix}.purchaseOrderLineId")
        if purchase_order_line_id in seen_purchase_order_lines:
            raise ValueError(
                "receipts contiene más de una recepción pendiente para la misma purchaseOrderLineId: "
                f"{purchase_order_line_id}."
            )
        seen_purchase_order_lines.add(purchase_order_line_id)
        key = (product_id, location_id)
        if key not in items:
            raise ValueError(f"{prefix} no tiene planningInputs para {product_id}/{location_id}.")
        items[key]["incoming"].append({
            "id": f"receipt:{line_id}",
            "status": "confirmed",
            "dueDate": due_date.isoformat(),
            "quantityMilli": quantity,
        })

    results: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    for key, item in items.items():
        result = plan_replenishment(item)
        status_counts[result["status"]] += 1
        native_quantity = native_auto_order[key]
        comparison = None
        if native_quantity is not None:
            planner_quantity = result["recommendedOrderQtyMilli"]
            comparison = {
                "nativeAutoOrderQtyMilli": native_quantity,
                "rubrovaSuggestedOrderQtyMilli": planner_quantity,
                "differenceMilli": (
                    None if planner_quantity is None else planner_quantity - native_quantity
                ),
                "comparable": planner_quantity is not None,
                "nativeSource": "PurchaseOrderShipmentAuto.toOrderPeriodic",
            }
        results.append({
            "productId": key[0],
            "locationId": key[1],
            "result": result,
            "nativeComparison": comparison,
        })

    return {
        "adapterVersion": 1,
        "sourceSystem": "MyCompany",
        "sourceVersion": "6.2",
        "asOf": as_of,
        "snapshotOnly": True,
        "readOnly": True,
        "syntheticOnly": False,
        "itemCount": len(results),
        "statusCounts": dict(sorted(status_counts.items())),
        "excludedOutgoingByReason": dict(sorted(excluded_outgoing.items())),
        "excludedIncomingByReason": dict(sorted(excluded_incoming.items())),
        "items": results,
        "limitations": [
            "El adaptador sólo lee un JSON exportado; no abre conexiones ni ejecuta consultas contra MyCompany.",
            "openQuantityMilli debe representar el remanente realmente abierto; no se debe copiar sin revisar initialDemand de documentos ya divididos.",
            "lineReservedMilli debe ser ShipmentResLedger.lineReserved, no la reserva bruta ni una segunda demanda.",
            "Sólo se importan recepciones ready vinculadas a órdenes de compra confirmadas y con increaseAvailableStock=false.",
            "Las recepciones manuales, transferencias, devoluciones y órdenes no confirmadas no se incorporan en esta primera versión.",
            "La comparación nativa es una lectura capturada de toOrderPeriodic; no ejecuta fillAuto ni crea órdenes.",
            "El pronóstico y las políticas de proveedor siguen siendo entradas externas al snapshot de inventario.",
        ],
    }


def build_report(snapshot: dict[str, Any]) -> dict[str, Any]:
    return adapt_snapshot(snapshot)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Importa un snapshot MyCompany 6.2 y calcula recomendaciones sin modificar el ERP."
    )
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    report = build_report(load_snapshot(args.snapshot))
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
