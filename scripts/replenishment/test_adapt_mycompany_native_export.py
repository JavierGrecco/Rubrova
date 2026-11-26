from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from adapt_mycompany_native_export import NATIVE_SOURCE_SEMANTICS, build_normalized_snapshot
from import_mycompany_snapshot import adapt_snapshot


ROOT = Path(__file__).resolve().parents[2]
NATIVE_FIXTURE = ROOT / "docs" / "fixtures" / "mycompany-native-replenishment-export.json"
POLICY_FIXTURE = ROOT / "docs" / "fixtures" / "replenishment-planning-policy.json"


class NativeMyCompanyExportBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.native = json.loads(NATIVE_FIXTURE.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY_FIXTURE.read_text(encoding="utf-8"))

    def _build(self, native: dict | None = None, policy: dict | None = None) -> dict:
        return build_normalized_snapshot(
            copy.deepcopy(self.native if native is None else native),
            copy.deepcopy(self.policy if policy is None else policy),
        )

    def test_native_source_semantics_match_the_fixture_contract(self) -> None:
        self.assertEqual(self.native["sourceSemantics"], NATIVE_SOURCE_SEMANTICS)
        self.assertEqual(
            self.native["sourceSemantics"]["outgoingEffectiveReservation"],
            "SUM(outgoingReservations.lineReserved > 0 where reserveEligible = true, grouped by sourceLineId)",
        )

    def test_native_export_becomes_a_planner_snapshot_without_losing_uom_precision(self) -> None:
        snapshot = self._build()
        self.assertEqual(snapshot["snapshotType"], "read-only-replenishment-snapshot")
        self.assertEqual(snapshot["asOf"], "2026-11-25")
        self.assertEqual(len(snapshot["inventory"]), 3)
        self.assertEqual(len(snapshot["outgoingCommitments"]), 2)
        self.assertEqual(len(snapshot["receipts"]), 1)
        self.assertEqual(snapshot["inventory"][0]["onHandMilli"], 16000)
        self.assertEqual(snapshot["inventory"][0]["availableMilli"], 13500)
        self.assertEqual(snapshot["inventory"][0]["plannedNetReservationMilli"], 2500)
        self.assertEqual(snapshot["outgoingCommitments"][0]["openQuantityMilli"], 4000)
        self.assertEqual(snapshot["outgoingCommitments"][0]["lineReservedMilli"], 2500)
        self.assertEqual(snapshot["receipts"][0]["expectedQuantityMilli"], 6000)

    def test_existing_planner_accepts_the_converted_snapshot_and_keeps_reservations_once(self) -> None:
        report = adapt_snapshot(self._build())
        cola = next(row["result"] for row in report["items"] if row["result"]["sku"] == "COLA-2L")
        self.assertEqual(cola["onHandMilli"], 16000)
        self.assertEqual(cola["reservedMilli"], 2500)
        self.assertEqual(cola["availableNowMilli"], 13500)
        self.assertEqual(cola["firmOutgoingInHorizonMilli"], 4000)
        self.assertEqual(cola["confirmedIncomingInHorizonMilli"], 6000)

    def test_bridge_does_not_invent_underlying_shipment_document_count(self) -> None:
        report = adapt_snapshot(self._build())
        cola = next(row for row in report["items"] if row["result"]["sku"] == "COLA-2L")
        self.assertIsNone(cola["underlyingShipmentDocumentCount"])

    def test_native_available_must_match_on_hand_minus_planned(self) -> None:
        source = copy.deepcopy(self.native)
        source["inventory"][0]["available"] = 13.4
        source["inventory"][0]["availableNative"] = 13.4
        with self.assertRaisesRegex(ValueError, "Disponible nativo no concilia"):
            self._build(source)

    def test_unmodeled_planned_reservations_block_planning_even_when_available_matches(self) -> None:
        source = copy.deepcopy(self.native)
        source["inventory"][0]["plannedNetReservation"] = 2.6
        source["inventory"][0]["plannedNetReservationNative"] = 2.6
        source["inventory"][0]["available"] = 13.4
        source["inventory"][0]["availableNative"] = 13.4
        with self.assertRaisesRegex(ValueError, "reservas que el planificador no modela"):
            self._build(source)

    def test_unrepresented_negative_reservations_block_planning(self) -> None:
        source = copy.deepcopy(self.native)
        source["inventory"][0]["expectedInbound"] = 6.1
        with self.assertRaisesRegex(ValueError, "recepciones previstas no representadas"):
            self._build(source)

    def test_receipt_with_increase_available_stock_true_is_not_silently_imported(self) -> None:
        source = copy.deepcopy(self.native)
        source["receipts"][0]["increaseAvailableStock"] = True
        with self.assertRaisesRegex(ValueError, "increaseAvailableStock=true"):
            self._build(source)

    def test_native_null_increase_available_stock_is_normalized_to_effective_false(self) -> None:
        source = copy.deepcopy(self.native)
        source["receipts"][0]["increaseAvailableStock"] = None

        snapshot = self._build(source)
        self.assertIs(snapshot["receipts"][0]["increaseAvailableStock"], False)
        report = adapt_snapshot(snapshot)
        self.assertTrue(report["items"])

    def test_invalid_non_boolean_increase_available_stock_is_rejected(self) -> None:
        source = copy.deepcopy(self.native)
        source["receipts"][0]["increaseAvailableStock"] = "false"
        with self.assertRaisesRegex(ValueError, "booleano o null"):
            self._build(source)

    def test_receipt_positive_quantity_must_match_native_negative_reservation(self) -> None:
        source = copy.deepcopy(self.native)
        source["receipts"][0]["expectedReservationSigned"] = -5.0
        with self.assertRaisesRegex(ValueError, "no conserva el signo y la magnitud"):
            self._build(source)

    def test_quantities_with_more_than_three_decimals_are_rejected_not_rounded(self) -> None:
        source = copy.deepcopy(self.native)
        source["inventory"][0]["onHand"] = 16.0001
        with self.assertRaisesRegex(ValueError, "más de tres decimales"):
            self._build(source)

    def test_native_raw_null_aggregates_can_use_effective_numeric_fallbacks(self) -> None:
        source = copy.deepcopy(self.native)
        source["inventory"][2]["onHandNative"] = None
        source["inventory"][2]["availableNative"] = None
        source["inventory"][2]["plannedNetReservationNative"] = None
        snapshot = self._build(source)
        oil = next(row for row in snapshot["inventory"] if row["productId"] == "PROD-ACEITE")
        self.assertEqual(oil["onHandMilli"], 5000)
        self.assertEqual(oil["availableMilli"], 5000)

    def test_each_inventory_pair_requires_an_explicit_planning_policy(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["policies"].pop()
        with self.assertRaisesRegex(ValueError, "Falta una política de planificación"):
            self._build(policy=policy)

    def test_duplicate_inventory_keys_are_rejected(self) -> None:
        source = copy.deepcopy(self.native)
        source["inventory"].append(copy.deepcopy(source["inventory"][0]))
        source["inventoryCount"] += 1
        with self.assertRaisesRegex(ValueError, "producto/ubicación duplicado"):
            self._build(source)

    def test_duplicate_outgoing_sales_order_line_is_rejected(self) -> None:
        source = copy.deepcopy(self.native)
        source["outgoingCommitments"].append(copy.deepcopy(source["outgoingCommitments"][0]))
        source["outgoingCommitmentsCount"] += 1
        with self.assertRaisesRegex(ValueError, "sourceLineId duplicado"):
            self._build(source)

    def test_effective_reservation_cannot_exceed_open_quantity(self) -> None:
        source = copy.deepcopy(self.native)
        source["outgoingReservations"][0]["lineReserved"] = 4.1
        with self.assertRaisesRegex(ValueError, "fuera de rango"):
            self._build(source)

    def test_multiple_shipment_lines_are_aggregated_once_by_sales_order_line(self) -> None:
        source = copy.deepcopy(self.native)
        extra_reserved = copy.deepcopy(source["outgoingReservations"][0])
        extra_reserved["shipmentId"] = "SH-COLA-PARTIAL-2"
        extra_reserved["shipmentLineId"] = "SH-COLA-PARTIAL-2#1"
        extra_reserved["lineReserved"] = 1.25
        source["outgoingReservations"].append(extra_reserved)
        ineligible_reserved = copy.deepcopy(extra_reserved)
        ineligible_reserved["shipmentId"] = "SH-COLA-DONE"
        ineligible_reserved["shipmentLineId"] = "SH-COLA-DONE#1"
        ineligible_reserved["lineReserved"] = 0.5
        ineligible_reserved["reserveEligible"] = False
        source["outgoingReservations"].append(ineligible_reserved)
        source["outgoingReservationsCount"] += 2
        source["inventory"][0]["grossReserved"] = 3.75
        source["inventory"][0]["plannedNetReservation"] = 3.75
        source["inventory"][0]["plannedNetReservationNative"] = 3.75
        source["inventory"][0]["available"] = 12.25
        source["inventory"][0]["availableNative"] = 12.25

        snapshot = self._build(source)
        cola = next(row for row in snapshot["outgoingCommitments"] if row["productId"] == "PROD-COLA")
        self.assertEqual(cola["lineReservedMilli"], 3750)

    def test_duplicate_outgoing_shipment_line_is_rejected(self) -> None:
        source = copy.deepcopy(self.native)
        source["outgoingReservations"].append(copy.deepcopy(source["outgoingReservations"][0]))
        source["outgoingReservationsCount"] += 1
        with self.assertRaisesRegex(ValueError, "shipmentLineId duplicado"):
            self._build(source)

    def test_outgoing_reservation_must_reference_an_exported_order_line(self) -> None:
        source = copy.deepcopy(self.native)
        source["outgoingReservations"][0]["sourceLineId"] = "UNKNOWN#1"
        with self.assertRaisesRegex(ValueError, "no referencia una línea de salida exportada"):
            self._build(source)

    def test_outgoing_reservation_eligibility_must_be_boolean(self) -> None:
        source = copy.deepcopy(self.native)
        source["outgoingReservations"][0]["reserveEligible"] = "true"
        with self.assertRaisesRegex(ValueError, "reserveEligible debe ser booleano"):
            self._build(source)

    def test_inventory_without_policy_is_not_silently_dropped(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["policies"].pop(0)
        with self.assertRaisesRegex(ValueError, "Falta una política de planificación"):
            self._build(policy=policy)

    def test_omitted_empty_collections_are_normalized_only_when_native_count_is_zero(self) -> None:
        source = copy.deepcopy(self.native)
        source.pop("outgoingCommitments")
        source["outgoingCommitmentsCount"] = 0
        source.pop("outgoingReservations")
        source["outgoingReservationsCount"] = 0
        source.pop("receipts")
        source["receiptsCount"] = 0
        for row in source["inventory"]:
            row["plannedNetReservation"] = 0
            row["plannedNetReservationNative"] = 0
            row["available"] = row["onHand"]
            row["availableNative"] = row["onHand"]
            row["expectedInbound"] = 0

        snapshot = self._build(source)
        self.assertEqual(snapshot["outgoingCommitments"], [])
        self.assertEqual(snapshot["receipts"], [])

    def test_native_collection_count_mismatch_is_rejected(self) -> None:
        source = copy.deepcopy(self.native)
        source["outgoingCommitmentsCount"] = 1
        with self.assertRaisesRegex(ValueError, "no coincide con la cantidad de filas"):
            self._build(source)

    def test_missing_non_empty_collection_is_rejected(self) -> None:
        source = copy.deepcopy(self.native)
        source.pop("outgoingCommitments")
        with self.assertRaisesRegex(ValueError, "outgoingCommitments debe ser una lista"):
            self._build(source)

    def test_native_contract_version_and_semantics_are_checked(self) -> None:
        source = copy.deepcopy(self.native)
        source["sourceVersion"] = "6.3"
        with self.assertRaisesRegex(ValueError, "sourceVersion"):
            self._build(source)
        source = copy.deepcopy(self.native)
        source["sourceSemantics"]["outgoingIdentity"] = "Sales.OrderLine.id"
        with self.assertRaisesRegex(ValueError, "sourceSemantics"):
            self._build(source)

    def test_policy_cannot_reference_an_unknown_product_location(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["policies"][0]["productId"] = "UNKNOWN"
        with self.assertRaisesRegex(ValueError, "no tiene una fila de inventario nativa"):
            self._build(policy=policy)


if __name__ == "__main__":
    unittest.main(verbosity=2)
