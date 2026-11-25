from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from import_mycompany_snapshot import adapt_snapshot, load_snapshot
from plan_replenishment import plan_replenishment


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / "docs" / "fixtures" / "mycompany-replenishment-snapshot.json"


class MyCompanySnapshotAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot = load_snapshot(SNAPSHOT_PATH)

    def _adapt(self, snapshot: dict | None = None) -> dict:
        return adapt_snapshot(copy.deepcopy(snapshot or self.snapshot))

    def _result_for(self, report: dict, sku: str) -> dict:
        return next(
            row["result"] for row in report["items"]
            if row["result"]["sku"] == sku
        )

    def test_fixture_imports_all_planning_items_as_read_only_real_source_data(self) -> None:
        report = self._adapt()
        self.assertEqual(report["sourceSystem"], "MyCompany")
        self.assertEqual(report["sourceVersion"], "6.2")
        self.assertEqual(report["itemCount"], 3)
        self.assertTrue(report["snapshotOnly"])
        self.assertTrue(report["readOnly"])
        self.assertFalse(report["syntheticOnly"])
        self.assertEqual(
            set(report["statusCounts"]),
            {"NO_ORDER_NEEDED", "ORDER_RECOMMENDED"},
        )

    def test_reservation_is_subset_of_open_shipment_and_deducted_only_once(self) -> None:
        report = self._adapt()
        result = self._result_for(report, "COLA-2L")
        self.assertEqual(result["onHandMilli"], 16000)
        self.assertEqual(result["reservedMilli"], 2500)
        self.assertEqual(result["availableNowMilli"], 13500)
        self.assertEqual(result["firmOutgoingInHorizonMilli"], 4000)
        self.assertEqual(result["includedOutgoingCount"], 1)

    def test_partial_shipment_residual_is_imported_without_recounting_completed_document(self) -> None:
        report = self._adapt()
        result = self._result_for(report, "COLA-2L")
        # The completed original shipment is excluded; only the separately
        # exported open residual shipment remains in the planning horizon.
        cola = next(row for row in report["items"] if row["result"]["sku"] == "COLA-2L")
        self.assertEqual(result["firmOutgoingInHorizonMilli"], 4000)
        self.assertEqual(cola["sourceSalesOrderLineCount"], 1)
        self.assertEqual(cola["underlyingShipmentDocumentCount"], 2)
        self.assertEqual(report["excludedOutgoingByReason"], {
            "CANCELLED": 1,
            "NOT_FIRM": 1,
        })

    def test_only_ready_receipt_from_confirmed_purchase_order_is_included(self) -> None:
        report = self._adapt()
        result = self._result_for(report, "COLA-2L")
        self.assertEqual(result["includedIncomingCount"], 1)
        self.assertEqual(result["confirmedIncomingInHorizonMilli"], 6000)
        self.assertEqual(report["excludedIncomingByReason"], {
            "ALREADY_RECEIVED": 1,
            "CANCELLED": 1,
            "NOT_CONFIRMED_PURCHASE_ORDER": 2,
            "NOT_READY": 1,
        })

    def test_ready_shipment_reservation_and_projected_commitment_are_not_double_counted(self) -> None:
        report = self._adapt()
        result = self._result_for(report, "PASTA-500G")
        self.assertEqual(result["reservedMilli"], 4500)
        self.assertEqual(result["availableNowMilli"], 3500)
        self.assertEqual(result["firmOutgoingInHorizonMilli"], 4500)
        self.assertEqual(result["recommendedOrderQtyMilli"], 2000)
        self.assertEqual(result["status"], "ORDER_RECOMMENDED")

    def test_native_auto_order_is_compared_as_captured_read_only_value(self) -> None:
        report = self._adapt()
        cola = next(row for row in report["items"] if row["result"]["sku"] == "COLA-2L")
        pasta = next(row for row in report["items"] if row["result"]["sku"] == "PASTA-500G")
        self.assertEqual(cola["nativeComparison"]["nativeAutoOrderQtyMilli"], 3000)
        self.assertEqual(cola["nativeComparison"]["rubrovaSuggestedOrderQtyMilli"], 0)
        self.assertEqual(cola["nativeComparison"]["differenceMilli"], -3000)
        self.assertEqual(pasta["nativeComparison"]["differenceMilli"], 1000)
        self.assertEqual(
            pasta["nativeComparison"]["nativeSource"],
            "PurchaseOrderShipmentAuto.toOrderPeriodic",
        )

    def test_duplicate_physical_balance_for_same_product_location_is_rejected(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["inventory"].append(copy.deepcopy(snapshot["inventory"][0]))
        with self.assertRaisesRegex(ValueError, "producto/ubicación duplicado"):
            adapt_snapshot(snapshot)

    def test_duplicate_sales_order_line_commitment_is_rejected(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["outgoingCommitments"].append(copy.deepcopy(snapshot["outgoingCommitments"][0]))
        with self.assertRaisesRegex(ValueError, "sourceLineId duplicado"):
            adapt_snapshot(snapshot)

    def test_duplicate_active_receipt_for_same_purchase_order_line_is_rejected(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        duplicate = copy.deepcopy(snapshot["receipts"][0])
        duplicate["lineId"] = "RL-COLA-DUPLICATE"
        duplicate["receiptId"] = "RC-COLA-DUPLICATE"
        snapshot["receipts"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "misma purchaseOrderLineId"):
            adapt_snapshot(snapshot)

    def test_receipt_that_increases_native_available_stock_is_rejected_until_modeled(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["receipts"][0]["increaseAvailableStock"] = True
        with self.assertRaisesRegex(ValueError, "increaseAvailableStock=true"):
            adapt_snapshot(snapshot)

    def test_missing_physical_stock_row_is_rejected(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["inventory"] = [
            row for row in snapshot["inventory"]
            if row["productId"] != "PROD-COLA"
        ]
        with self.assertRaisesRegex(ValueError, "no tiene existencia física"):
            adapt_snapshot(snapshot)

    def test_reservation_cannot_exceed_its_open_sales_order_line(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["outgoingCommitments"][0]["lineReservedMilli"] = (
            snapshot["outgoingCommitments"][0]["openQuantityMilli"] + 1
        )
        with self.assertRaisesRegex(ValueError, "no puede superar openQuantityMilli"):
            adapt_snapshot(snapshot)

    def test_zero_open_sales_order_line_is_ignored_as_fully_shipped(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["outgoingCommitments"][0]["openQuantityMilli"] = 0
        report = adapt_snapshot(snapshot)
        cola = next(row for row in report["items"] if row["result"]["sku"] == "COLA-2L")
        self.assertEqual(cola["result"]["firmOutgoingInHorizonMilli"], 0)

    def test_unknown_native_shipment_or_receipt_status_is_rejected(self) -> None:
        shipment = copy.deepcopy(self.snapshot)
        shipment["outgoingCommitments"][0]["status"] = "in_progress"
        with self.assertRaisesRegex(ValueError, "status no soportado"):
            adapt_snapshot(shipment)

        receipt = copy.deepcopy(self.snapshot)
        receipt["receipts"][0]["status"] = "in_transit"
        with self.assertRaisesRegex(ValueError, "status no soportado"):
            adapt_snapshot(receipt)

    def test_mismatched_source_semantics_are_rejected(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["sourceSemantics"]["outgoingReservation"] = "SUM(ShipmentLine.reserved_raw_by_OrderLine)"
        with self.assertRaisesRegex(ValueError, "sourceSemantics"):
            adapt_snapshot(snapshot)

    def test_non_62_source_is_rejected(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["sourceVersion"] = "6.3"
        with self.assertRaisesRegex(ValueError, "MyCompany 6.2"):
            adapt_snapshot(snapshot)

    def test_native_comparator_may_be_omitted_and_does_not_block_planning(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["planningInputs"][0].pop("nativeAutoOrderQtyMilli")
        report = adapt_snapshot(snapshot)
        cola = next(row for row in report["items"] if row["result"]["sku"] == "COLA-2L")
        self.assertIsNone(cola["nativeComparison"])
        self.assertEqual(cola["result"]["status"], "NO_ORDER_NEEDED")

    def test_invalid_boolean_quantity_is_rejected(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        snapshot["inventory"][0]["onHandMilli"] = True
        with self.assertRaisesRegex(ValueError, "entero"):
            adapt_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main(verbosity=2)
