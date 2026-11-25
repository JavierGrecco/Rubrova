from __future__ import annotations

import copy
import unittest
from pathlib import Path

from plan_replenishment import build_report, load_fixture, plan_replenishment


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "docs" / "fixtures" / "replenishment-planning.json"


class ReplenishmentPlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = load_fixture(FIXTURE_PATH)
        cls.scenarios = {row["id"]: row["item"] for row in cls.fixture["scenarios"]}

    def test_synthetic_fixture_matches_all_expected_decisions(self) -> None:
        report = build_report(self.fixture)
        self.assertEqual(report["scenarioCount"], 6)
        self.assertTrue(report["syntheticOnly"])
        self.assertTrue(report["readOnly"])
        self.assertEqual(report["statusCounts"]["ORDER_RECOMMENDED"], 1)
        self.assertEqual(report["statusCounts"]["NO_ORDER_NEEDED"], 2)
        self.assertEqual(report["statusCounts"]["EXPEDITE_REQUIRED"], 1)
        self.assertEqual(report["statusCounts"]["SUPPRESSED"], 1)
        self.assertEqual(report["statusCounts"]["DATA_REVIEW"], 1)

    def test_reservations_are_subset_of_outgoing_commitments_not_extra_demand(self) -> None:
        result = plan_replenishment(
            self.scenarios["reponer-con-compromiso-y-recepcion-confirmada"]
        )
        self.assertEqual(result["reservedMilli"], 2500)
        self.assertEqual(result["availableNowMilli"], 9500)
        self.assertEqual(result["firmOutgoingInHorizonMilli"], 4000)
        self.assertEqual(result["projectedEndBeforeOrderMilli"], -300)
        self.assertEqual(result["recommendedOrderQtyMilli"], 6000)

    def test_order_quantity_respects_minimum_and_supplier_multiple(self) -> None:
        result = plan_replenishment(
            self.scenarios["reponer-con-compromiso-y-recepcion-confirmada"]
        )
        # Raw gap is 3,300 milli-units; MOQ is 5,000 and packs are 2,000.
        self.assertEqual(result["reorderGapMilli"], 3300)
        self.assertEqual(result["recommendedOrderQtyMilli"], 6000)
        self.assertEqual(result["projectedEndAfterRecommendedOrderMilli"], 5700)

    def test_unconfirmed_cancelled_received_and_overdue_inbound_are_excluded(self) -> None:
        result = plan_replenishment(
            self.scenarios["se-excluyen-recepciones-no-confirmadas-o-vencidas"]
        )
        self.assertEqual(result["includedIncomingCount"], 2)
        self.assertEqual(result["confirmedIncomingInHorizonMilli"], 2500)
        self.assertEqual(result["excludedIncomingByReason"], {
            "CANCELLED": 1,
            "NOT_CONFIRMED": 2,
            "PAST_DUE": 1,
        })
        self.assertEqual(result["status"], "NO_ORDER_NEEDED")

    def test_shortage_before_new_supplier_delivery_requires_expedite(self) -> None:
        result = plan_replenishment(
            self.scenarios["riesgo-de-quiebre-antes-de-la-nueva-entrega"]
        )
        self.assertEqual(result["status"], "EXPEDITE_REQUIRED")
        self.assertEqual(result["reason"], "PROJECTED_SHORTAGE_BEFORE_NEW_SUPPLY")
        self.assertTrue(result["stockoutBeforeReplenishment"])
        self.assertEqual(result["minimumProjectedStockBeforeReceiptsMilli"], -1000)
        self.assertEqual(result["recommendedOrderQtyMilli"], 8000)

    def test_forecast_history_below_minimum_suppresses_purchase_suggestion(self) -> None:
        result = plan_replenishment(self.scenarios["pronostico-insuficiente"])
        self.assertEqual(result["status"], "SUPPRESSED")
        self.assertEqual(result["reason"], "INSUFFICIENT_FORECAST_HISTORY_OR_COVERAGE")
        self.assertIsNone(result["recommendedOrderQtyMilli"])
        self.assertIsNone(result["projectedEndBeforeOrderMilli"])

    def test_exact_minimum_forecast_history_and_coverage_is_eligible(self) -> None:
        item = copy.deepcopy(self.scenarios["pronostico-insuficiente"])
        item["forecastEligiblePeriods"] = 12
        result = plan_replenishment(item)
        self.assertNotEqual(result["status"], "SUPPRESSED")
        self.assertEqual(result["forecastCoverage"], 0.5)

    def test_reservations_exceeding_physical_stock_trigger_data_review(self) -> None:
        result = plan_replenishment(self.scenarios["reservas-superan-existencia"])
        self.assertEqual(result["status"], "DATA_REVIEW")
        self.assertEqual(result["reason"], "RESERVATIONS_EXCEED_ON_HAND")
        self.assertEqual(result["availableNowMilli"], -500)
        self.assertIsNone(result["recommendedOrderQtyMilli"])

    def test_future_commitment_reduces_free_to_promise_without_distorting_horizon(self) -> None:
        item = {
            "sku": "SKU-FUTURE",
            "location": "LOCAL-01",
            "asOf": "2026-11-25",
            "onHandMilli": 10000,
            "dailyDemandMilli": 500,
            "forecastEligiblePeriods": 24,
            "forecastTotalPeriods": 36,
            "supplierLeadTimeDays": 5,
            "reviewPeriodDays": 5,
            "safetyStockMilli": 1000,
            "minimumOrderQuantityMilli": 0,
            "orderMultipleMilli": 500,
            "outgoing": [
                {
                    "id": "commitment-after-horizon",
                    "status": "ready",
                    "dueDate": "2026-12-20",
                    "quantityMilli": 2000,
                    "reservedMilli": 1500,
                }
            ],
            "incoming": [],
        }
        result = plan_replenishment(item)
        self.assertEqual(result["availableNowMilli"], 8500)
        self.assertEqual(result["firmOutgoingInHorizonMilli"], 0)
        self.assertEqual(result["excludedOutgoingByReason"], {"AFTER_COVERAGE": 1})
        self.assertEqual(result["projectedEndBeforeOrderMilli"], 5000)
        self.assertEqual(result["recommendedOrderQtyMilli"], 0)

    def test_duplicate_incoming_ids_are_rejected_to_prevent_double_counting(self) -> None:
        item = copy.deepcopy(self.scenarios["sin-reposicion-necesaria"])
        item["incoming"].append(copy.deepcopy(item["incoming"][0]))
        with self.assertRaisesRegex(ValueError, "id duplicado"):
            plan_replenishment(item)

    def test_duplicate_outgoing_ids_are_rejected_to_prevent_double_counting(self) -> None:
        item = copy.deepcopy(self.scenarios["sin-reposicion-necesaria"])
        item["outgoing"].append(copy.deepcopy(item["outgoing"][0]))
        with self.assertRaisesRegex(ValueError, "id duplicado"):
            plan_replenishment(item)

    def test_reservation_cannot_exceed_its_open_outgoing_line(self) -> None:
        item = copy.deepcopy(self.scenarios["sin-reposicion-necesaria"])
        item["outgoing"][0]["reservedMilli"] = item["outgoing"][0]["quantityMilli"] + 1
        with self.assertRaisesRegex(ValueError, "no puede superar"):
            plan_replenishment(item)

    def test_boolean_fractional_and_negative_quantities_are_rejected(self) -> None:
        base = copy.deepcopy(self.scenarios["sin-reposicion-necesaria"])
        for value in (True, 1.5, -1, "1000"):
            with self.subTest(value=value):
                item = copy.deepcopy(base)
                item["onHandMilli"] = value
                with self.assertRaisesRegex(ValueError, "entero"):
                    plan_replenishment(item)

    def test_unknown_incoming_status_is_rejected(self) -> None:
        item = copy.deepcopy(self.scenarios["sin-reposicion-necesaria"])
        item["incoming"][0]["status"] = "maybe"
        with self.assertRaisesRegex(ValueError, "status no soportado"):
            plan_replenishment(item)

    def test_zero_forecast_is_valid_when_history_is_sufficient(self) -> None:
        item = copy.deepcopy(self.scenarios["sin-reposicion-necesaria"])
        item["dailyDemandMilli"] = 0
        result = plan_replenishment(item)
        self.assertEqual(result["status"], "NO_ORDER_NEEDED")
        self.assertEqual(result["dailyUncommittedForecastMilli"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
