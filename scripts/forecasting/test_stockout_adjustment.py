from __future__ import annotations

import unittest

from stockout_adjustment import adjust_observation, build_stockout_adjustment_report


class StockoutAdjustmentTests(unittest.TestCase):
    def test_full_availability_preserves_observed_units(self) -> None:
        result = adjust_observation({"units": 31, "openDays": 26, "stockoutDays": 0})
        self.assertEqual(result["estimatedDemandUnits"], 31.0)
        self.assertEqual(result["status"], "observed")

    def test_adjustment_recovers_controlled_latent_demand(self) -> None:
        result = adjust_observation({"units": 80, "openDays": 25, "stockoutDays": 5})
        self.assertEqual(result["availableDays"], 20)
        self.assertEqual(result["estimatedDemandUnits"], 100.0)
        self.assertEqual(result["status"], "adjusted")

    def test_boundary_thresholds_are_inclusive(self) -> None:
        result = adjust_observation(
            {"units": 40, "openDays": 20, "stockoutDays": 10},
            min_available_days=10,
            min_availability_ratio=0.50,
        )
        self.assertEqual(result["estimatedDemandUnits"], 80.0)

    def test_low_availability_and_too_few_days_are_suppressed(self) -> None:
        low_ratio = adjust_observation({"units": 30, "openDays": 20, "stockoutDays": 11})
        too_few = adjust_observation({"units": 30, "openDays": 20, "stockoutDays": 11}, min_available_days=10)
        self.assertIsNone(low_ratio["estimatedDemandUnits"])
        self.assertEqual(low_ratio["reason"], "LOW_AVAILABILITY")
        self.assertIsNone(too_few["estimatedDemandUnits"])
        self.assertEqual(too_few["reason"], "TOO_FEW_AVAILABLE_DAYS")

    def test_no_open_days_and_no_available_days_are_suppressed(self) -> None:
        no_open = adjust_observation({"units": 0, "openDays": 0, "stockoutDays": 0})
        no_stock = adjust_observation({"units": 0, "openDays": 20, "stockoutDays": 20})
        self.assertEqual(no_open["reason"], "NO_OPEN_DAYS")
        self.assertEqual(no_stock["reason"], "NO_AVAILABLE_DAYS")
        self.assertIsNone(no_open["estimatedDemandUnits"])
        self.assertIsNone(no_stock["estimatedDemandUnits"])

    def test_invalid_counts_are_rejected(self) -> None:
        invalid_rows = [
            {"units": -1, "openDays": 20, "stockoutDays": 0},
            {"units": 1, "openDays": 20, "stockoutDays": 21},
            {"units": True, "openDays": 20, "stockoutDays": 0},
            {"units": 1, "openDays": 20.5, "stockoutDays": 0},
        ]
        for row in invalid_rows:
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    adjust_observation(row)

    def test_report_scores_only_eligible_periods(self) -> None:
        fixture = {
            "observations": [
                {"month": "2025-01-01", "units": 80, "openDays": 25, "stockoutDays": 5, "latentDemandUnits": 100},
                {"month": "2025-02-01", "units": 0, "openDays": 25, "stockoutDays": 25, "latentDemandUnits": 110},
            ]
        }
        report = build_stockout_adjustment_report(fixture)
        self.assertEqual(report["periods"], 2)
        self.assertEqual(report["eligiblePeriods"], 1)
        self.assertEqual(report["coverage"], 0.5)
        self.assertEqual(report["sameEligiblePeriods"]["observedSalesVsSyntheticTruth"]["WAPE"], 0.2)
        self.assertEqual(report["sameEligiblePeriods"]["availabilityAdjustedVsSyntheticTruth"]["WAPE"], 0.0)


if __name__ == "__main__":
    unittest.main()
