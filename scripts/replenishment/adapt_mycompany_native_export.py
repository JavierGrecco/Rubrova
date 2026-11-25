#!/usr/bin/env python3
"""Convert the native, read-only MyCompany export into the planner snapshot contract.

This bridge is deliberately strict: it refuses to plan when native reservations
or expected receipts cannot be explained by the exported sales lines and receipt
lines. It never connects to MyCompany and never writes to the ERP.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from import_mycompany_snapshot import SOURCE_SEMANTICS, adapt_snapshot


NATIVE_SOURCE_SEMANTICS = {
    "inventoryOnHand": "Inventory.onHand(Location, Product), ubicación exacta",
    "inventoryAvailable": "Inventory.available(Location, Product), valor nativo MyCompany",
    "inventoryPlannedNet": "Inventory.planned(Location, Product), reservas firmadas que participan en available",
    "inventoryExpectedCoverage": "all negative ResLedger reservations for exact product/location; not limited to confirmed purchase receipts",
    "emptyAggregatePolicy": "raw *Native fields preserve NULL; effective numeric fields use OVERRIDE fallback 0",
    "outgoingIdentity": "Sales.number(Order) + Sales.index(OrderLine)",
    "outgoingOpenQuantity": "Sales.toShip(OrderLine_confirmed)",
    "outgoingScheduledDateTime": "Sales.scheduledDateTime(Order)",
    "outgoingEffectiveReservation": "SUM(ShipmentResLedger.lineReserved by Sales.OrderLine)",
    "incomingIdentity": "Receipt.number + ReceiptLine.index",
    "incomingExpectedQuantity": "0 - ReceiptResLedger.reserved; signed reservation remains negative",
    "incomingScheduledDateTime": "Receipt.scheduledDateTime",
    "incomingEligibility": "Receipt.ready AND NOT Receipt.done AND NOT Receipt.canceled AND Purchase.Order.confirmed",
    "incomingAvailabilityPolicy": "ReceiptType.increaseAvailableStock; skipAvailable is its inverse"
}
NATIVE_HEADER = {
    "schemaVersion": 1,
    "snapshotType": "mycompany-replenishment-source-export",
    "sourceSystem": "MyCompany",
    "sourceVersion": "6.2",
    "quantityUnit": "product-uom",
    "quantityPrecision": 3,
    "readOnly": True,
}


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


def _iso_date(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} debe usar YYYY-MM-DD.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} debe usar YYYY-MM-DD.") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{field} debe usar exactamente YYYY-MM-DD.")
    return value


def _iso_datetime(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} debe ser una fecha y hora ISO.")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} debe ser una fecha y hora ISO válida.") from exc
    return value


def _decimal(value: Any, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise ValueError(f"{field} debe ser una cantidad numérica.")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} debe ser una cantidad numérica.") from exc
    if not result.is_finite():
        raise ValueError(f"{field} debe ser un número finito.")
    return result


def _milli(value: Any, field: str) -> int:
    quantity = _decimal(value, field)
    scaled = quantity * 1000
    integral = scaled.to_integral_value()
    if scaled != integral:
        raise ValueError(
            f"{field} tiene más de tres decimales; no se redondeará una cantidad de MyCompany."
        )
    return int(integral)


def _optional_native_milli(row: dict[str, Any], field: str, effective: int, label: str) -> None:
    value = row.get(field)
    if value is not None and _milli(value, f"{label}.{field}") != effective:
        raise ValueError(f"{label}.{field} no coincide con su valor efectivo.")


def _key(row: dict[str, Any], label: str) -> tuple[str, str]:
    return (
        _text(row.get("productId"), f"{label}.productId"),
        _text(row.get("locationId"), f"{label}.locationId"),
    )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer {label}: {exc}") from exc
    return _object(payload, label)


def _validate_native_source(source: dict[str, Any]) -> None:
    for field, expected in NATIVE_HEADER.items():
        if source.get(field) != expected:
            raise ValueError(
                f"El export nativo no cumple {field}: se esperaba {expected!r}."
            )
    _iso_date(str(source.get("asOf", "")), "asOf")
    _iso_datetime(source.get("asOfDateTime"), "asOfDateTime")
    if source.get("sourceSemantics") != NATIVE_SOURCE_SEMANTICS:
        raise ValueError("sourceSemantics no coincide con el contrato nativo MyCompany 6.2.")


def _planning_policy(policy: dict[str, Any], inventory_keys: set[tuple[str, str]]) -> list[dict[str, Any]]:
    if policy.get("schemaVersion") != 1:
        raise ValueError("schemaVersion de la política debe ser 1.")
    rows = _rows(policy.get("policies"), "policies")
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(rows):
        prefix = f"policies[{index}]"
        key = _key(row, prefix)
        if key in seen:
            raise ValueError(f"policies contiene una clave producto/ubicación duplicada: {key[0]}/{key[1]}.")
        seen.add(key)
        if key not in inventory_keys:
            raise ValueError(f"{prefix} no tiene una fila de inventario nativa para {key[0]}/{key[1]}.")
        planning = {
            "productId": key[0],
            "locationId": key[1],
            "sku": _text(row.get("sku"), f"{prefix}.sku"),
            "locationName": _text(row.get("locationName"), f"{prefix}.locationName"),
        }
        integer_fields = (
            "dailyDemandMilli",
            "forecastEligiblePeriods",
            "forecastTotalPeriods",
            "supplierLeadTimeDays",
            "reviewPeriodDays",
            "safetyStockMilli",
            "minimumOrderQuantityMilli",
            "orderMultipleMilli",
        )
        for field in integer_fields:
            value = row.get(field)
            minimum = 1 if field in {"supplierLeadTimeDays", "reviewPeriodDays", "orderMultipleMilli"} else 0
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                qualifier = "positivo" if minimum else "no negativo"
                raise ValueError(f"{prefix}.{field} debe ser un entero {qualifier}.")
            planning[field] = value
        if planning["forecastEligiblePeriods"] > planning["forecastTotalPeriods"]:
            raise ValueError(f"{prefix}.forecastEligiblePeriods no puede superar forecastTotalPeriods.")
        native_order = row.get("nativeAutoOrderQtyMilli")
        if native_order is not None:
            if isinstance(native_order, bool) or not isinstance(native_order, int) or native_order < 0:
                raise ValueError(f"{prefix}.nativeAutoOrderQtyMilli debe ser un entero no negativo.")
            planning["nativeAutoOrderQtyMilli"] = native_order
        result.append(planning)

    missing = sorted(inventory_keys - seen)
    if missing:
        rendered = ", ".join(f"{product}/{location}" for product, location in missing[:8])
        suffix = "..." if len(missing) > 8 else ""
        raise ValueError(
            "Falta una política de planificación explícita para producto/ubicación: "
            + rendered + suffix
        )
    return result


def build_normalized_snapshot(
    source: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Convert native MyCompany quantities to the importer's integer milli-unit contract."""
    source = _object(source, "source")
    policy = _object(policy, "policy")
    _validate_native_source(source)

    inventory_rows = _rows(source.get("inventory"), "inventory")
    outgoing_rows = _rows(source.get("outgoingCommitments"), "outgoingCommitments")
    receipt_rows = _rows(source.get("receipts"), "receipts")

    inventory: list[dict[str, Any]] = []
    balances: dict[tuple[str, str], dict[str, int]] = {}
    for index, row in enumerate(inventory_rows):
        label = f"inventory[{index}]"
        key = _key(row, label)
        if key in balances:
            raise ValueError(f"inventory contiene producto/ubicación duplicado: {key[0]}/{key[1]}.")
        on_hand = _milli(row.get("onHand"), f"{label}.onHand")
        available = _milli(row.get("available"), f"{label}.available")
        planned = _milli(row.get("plannedNetReservation"), f"{label}.plannedNetReservation")
        gross_reserved = _milli(row.get("grossReserved"), f"{label}.grossReserved")
        expected_inbound = _milli(row.get("expectedInbound"), f"{label}.expectedInbound")
        if on_hand < 0:
            raise ValueError(f"{label}.onHand es negativo; el planificador actual no acepta stock físico negativo.")
        if gross_reserved < 0 or expected_inbound < 0:
            raise ValueError(f"{label} contiene reservas brutas o recepciones previstas negativas.")
        if available != on_hand - planned:
            raise ValueError(
                f"Disponible nativo no concilia para {key[0]}/{key[1]}: "
                f"onHand={on_hand}, planned={planned}, available={available} (milésimas)."
            )
        _optional_native_milli(row, "onHandNative", on_hand, label)
        _optional_native_milli(row, "availableNative", available, label)
        _optional_native_milli(row, "plannedNetReservationNative", planned, label)
        _optional_native_milli(row, "physicalIncomingNative", _milli(row.get("physicalIncoming"), f"{label}.physicalIncoming"), label)
        _optional_native_milli(row, "physicalOutgoingNative", _milli(row.get("physicalOutgoing"), f"{label}.physicalOutgoing"), label)
        balances[key] = {
            "onHandMilli": on_hand,
            "availableMilli": available,
            "plannedNetReservationMilli": planned,
            "grossReservedMilli": gross_reserved,
            "expectedInboundMilli": expected_inbound,
        }
        inventory.append({
            "productId": key[0],
            "locationId": key[1],
            "onHandMilli": on_hand,
            "availableMilli": available,
            "plannedNetReservationMilli": planned,
            "grossReservedMilli": gross_reserved,
            "expectedInboundMilli": expected_inbound,
        })

    if not balances:
        raise ValueError("inventory nativo no puede estar vacío.")

    outgoing: list[dict[str, Any]] = []
    outgoing_reservations: dict[tuple[str, str], int] = {}
    seen_outgoing: set[str] = set()
    for index, row in enumerate(outgoing_rows):
        label = f"outgoingCommitments[{index}]"
        line_id = _text(row.get("sourceLineId"), f"{label}.sourceLineId")
        if line_id in seen_outgoing:
            raise ValueError(f"outgoingCommitments contiene sourceLineId duplicado: {line_id}.")
        seen_outgoing.add(line_id)
        key = _key(row, label)
        if key not in balances:
            raise ValueError(f"{label} no tiene inventario para {key[0]}/{key[1]}.")
        if row.get("status") != "confirmed":
            raise ValueError(f"{label}.status no es confirmed; la API debe exportar sólo pedidos confirmados.")
        open_quantity = _milli(row.get("openQuantity"), f"{label}.openQuantity")
        reserved = _milli(row.get("effectiveReserved"), f"{label}.effectiveReserved")
        if open_quantity <= 0 or reserved < 0 or reserved > open_quantity:
            raise ValueError(f"{label} tiene remanente o reserva efectiva fuera de rango.")
        related_shipments = row.get("relatedShipmentCount")
        if related_shipments is not None and (
            isinstance(related_shipments, bool)
            or not isinstance(related_shipments, int)
            or related_shipments < 0
        ):
            raise ValueError(f"{label}.relatedShipmentCount debe ser un entero no negativo.")
        outgoing_reservations[key] = outgoing_reservations.get(key, 0) + reserved
        normalized_outgoing = {
            "sourceLineId": line_id,
            "sourceDocumentId": _text(row.get("sourceDocumentId"), f"{label}.sourceDocumentId"),
            "productId": key[0],
            "locationId": key[1],
            "status": "confirmed",
            "scheduledDate": _iso_date(row.get("scheduledDate"), f"{label}.scheduledDate"),
            "openQuantityMilli": open_quantity,
            "lineReservedMilli": reserved,
        }
        if related_shipments is not None:
            normalized_outgoing["relatedShipmentCount"] = related_shipments
        outgoing.append(normalized_outgoing)

    receipts: list[dict[str, Any]] = []
    receipt_quantities: dict[tuple[str, str], int] = {}
    seen_receipts: set[str] = set()
    seen_po_lines: set[str] = set()
    for index, row in enumerate(receipt_rows):
        label = f"receipts[{index}]"
        line_id = _text(row.get("lineId"), f"{label}.lineId")
        if line_id in seen_receipts:
            raise ValueError(f"receipts contiene lineId duplicado: {line_id}.")
        seen_receipts.add(line_id)
        key = _key(row, label)
        if key not in balances:
            raise ValueError(f"{label} no tiene inventario para {key[0]}/{key[1]}.")
        if row.get("status") != "ready" or row.get("purchaseOrderStatus") != "confirmed":
            raise ValueError(f"{label} no es una recepción ready de una orden confirmada.")
        signed = _milli(row.get("expectedReservationSigned"), f"{label}.expectedReservationSigned")
        expected = _milli(row.get("expectedQuantity"), f"{label}.expectedQuantity")
        if signed >= 0 or expected <= 0 or expected != -signed:
            raise ValueError(f"{label} no conserva el signo y la magnitud de ReceiptResLedger.reserved.")
        increase_available = row.get("increaseAvailableStock")
        if not isinstance(increase_available, bool):
            raise ValueError(f"{label}.increaseAvailableStock debe ser booleano.")
        if increase_available:
            raise ValueError(
                f"{label} usa increaseAvailableStock=true; el planificador todavía no reproduce esa política."
            )
        po_line = _text(row.get("purchaseOrderLineId"), f"{label}.purchaseOrderLineId")
        if po_line in seen_po_lines:
            raise ValueError(f"receipts contiene más de una recepción pendiente para {po_line}.")
        seen_po_lines.add(po_line)
        receipt_quantities[key] = receipt_quantities.get(key, 0) + expected
        receipts.append({
            "lineId": line_id,
            "receiptId": _text(row.get("receiptId"), f"{label}.receiptId"),
            "purchaseOrderId": _text(row.get("purchaseOrderId"), f"{label}.purchaseOrderId"),
            "purchaseOrderLineId": po_line,
            "productId": key[0],
            "locationId": key[1],
            "status": "ready",
            "purchaseOrderStatus": "confirmed",
            "scheduledDate": _iso_date(row.get("scheduledDate"), f"{label}.scheduledDate"),
            "expectedQuantityMilli": expected,
            "increaseAvailableStock": False,
        })

    for key, balance in balances.items():
        exported_outgoing = outgoing_reservations.get(key, 0)
        if balance["plannedNetReservationMilli"] != exported_outgoing:
            raise ValueError(
                f"Hay reservas que el planificador no modela para {key[0]}/{key[1]}: "
                f"plannedNetReservation={balance['plannedNetReservationMilli']} milésimas, "
                f"compromisos de venta={exported_outgoing} milésimas. No se generará una sugerencia."
            )
        exported_incoming = receipt_quantities.get(key, 0)
        if balance["expectedInboundMilli"] != exported_incoming:
            raise ValueError(
                f"Hay recepciones previstas no representadas por órdenes confirmadas para {key[0]}/{key[1]}: "
                f"expectedInbound={balance['expectedInboundMilli']} milésimas, "
                f"recepciones exportadas={exported_incoming} milésimas. No se generará una sugerencia."
            )

    planning_inputs = _planning_policy(policy, set(balances))
    snapshot = {
        "schemaVersion": 1,
        "snapshotType": "read-only-replenishment-snapshot",
        "sourceSystem": "MyCompany",
        "sourceVersion": "6.2",
        "asOf": _iso_date(source.get("asOf"), "asOf"),
        "sourceSemantics": SOURCE_SEMANTICS,
        "inventory": inventory,
        "outgoingCommitments": outgoing,
        "receipts": receipts,
        "planningInputs": planning_inputs,
    }
    # Run the existing adapter once before writing anything: the converter must
    # only emit a snapshot that the real planner contract accepts.
    adapt_snapshot(snapshot)
    return snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convierte la exportación nativa MyCompany 6.2 en un snapshot de reposición validado."
    )
    parser.add_argument("--source", type=Path, required=True, help="JSON exportado por la acción @@api de MyCompany.")
    parser.add_argument("--policy", type=Path, required=True, help="Política explícita de pronóstico y proveedor.")
    parser.add_argument("--output", type=Path, required=True, help="Snapshot normalizado que consumirá el planificador.")
    args = parser.parse_args()

    source = _read_json(args.source, "export nativo")
    policy = _read_json(args.policy, "política de planificación")
    snapshot = build_normalized_snapshot(source, policy)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "SNAPSHOT_NORMALIZED=true "
        f"inventory={len(snapshot['inventory'])} "
        f"outgoing={len(snapshot['outgoingCommitments'])} "
        f"receipts={len(snapshot['receipts'])} "
        f"planningInputs={len(snapshot['planningInputs'])}"
    )
    print(f"SNAPSHOT_OUTPUT={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
