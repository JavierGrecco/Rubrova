from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

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
        low_ratio = adjust_observation({"units": 30, "openDays": 40, "stockoutDays": 22})
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

    def test_invalid_availability_thresholds_are_rejected(self) -> None:
        for threshold in (True, False, 0, -0.1, 1.1, float("nan"), float("inf"), "0.5"):
            with self.subTest(threshold=threshold):
                with self.assertRaises(ValueError):
                    adjust_observation(
                        {"units": 10, "openDays": 20, "stockoutDays": 0},
                        min_availability_ratio=threshold,
                    )

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

    def test_fixture_rejects_missing_months(self) -> None:
        from stockout_adjustment import load_stockout_fixture

        payload = {
            "schemaVersion": 1,
            "frequency": "MS",
            "observations": [
                {"month": "2025-01-01", "units": 10, "openDays": 26, "stockoutDays": 0, "latentDemandUnits": 10},
                {"month": "2025-03-01", "units": 12, "openDays": 26, "stockoutDays": 0, "latentDemandUnits": 12},
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_path = Path(temp_dir) / "fixture.json"
            fixture_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "meses faltantes"):
                load_stockout_fixture(fixture_path)

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


    def test_min_available_days_must_be_a_positive_integer(self) -> None:
        for threshold in (True, False, 0, -1, 10.5, "10"):
            with self.subTest(threshold=threshold):
                with self.assertRaises(ValueError):
                    adjust_observation(
                        {"units": 10, "openDays": 20, "stockoutDays": 0},
                        min_available_days=threshold,
                    )

    def test_synthetic_truth_never_changes_the_demand_estimate(self) -> None:
        low_truth = adjust_observation(
            {"units": 80, "openDays": 25, "stockoutDays": 5, "latentDemandUnits": 80}
        )
        high_truth = adjust_observation(
            {"units": 80, "openDays": 25, "stockoutDays": 5, "latentDemandUnits": 5000}
        )
        self.assertEqual(low_truth["estimatedDemandUnits"], 100.0)
        self.assertEqual(high_truth["estimatedDemandUnits"], 100.0)
        self.assertEqual(low_truth, high_truth)

    def test_report_fails_when_no_period_is_eligible(self) -> None:
        fixture = {
            "observations": [
                {
                    "month": "2025-01-01",
                    "units": 20,
                    "openDays": 25,
                    "stockoutDays": 25,
                    "latentDemandUnits": 30,
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "No hay períodos"):
            build_stockout_adjustment_report(fixture)

    def test_fixture_rejects_non_month_start_and_duplicate_months(self) -> None:
        from stockout_adjustment import load_stockout_fixture

        valid_row = {
            "units": 10,
            "openDays": 26,
            "stockoutDays": 0,
            "latentDemandUnits": 10,
        }
        invalid_observations = (
            [{**valid_row, "month": "2025-01-15"}],
            [{**valid_row, "month": "2025-01-01"}, {**valid_row, "month": "2025-01-01"}],
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_path = Path(temp_dir) / "fixture.json"
            for observations in invalid_observations:
                with self.subTest(observations=observations):
                    payload = {
                        "schemaVersion": 1,
                        "frequency": "MS",
                        "observations": observations,
                    }
                    fixture_path.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "únicos|comenzar"):
                        load_stockout_fixture(fixture_path)


if __name__ == "__main__":
    unittest.main()
