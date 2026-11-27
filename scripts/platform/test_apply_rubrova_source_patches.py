#!/usr/bin/env python3
"""Regression tests for the MyCompany POS refund source patch state machine."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
PATCHER_PATH = ROOT / "scripts/platform/apply-rubrova-source-patches.py"
SPEC = importlib.util.spec_from_file_location("rubrova_source_patches", PATCHER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"No se pudo cargar el patcher: {PATCHER_PATH}")
PATCHER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATCHER)


def upstream_dialog_source() -> str:
    """Return the exact upstream anchors expected by a clean MyCompany 6.2 source."""
    return "\n".join(
        (
            "MODULE PosDashboardReturnPayment;",
            PATCHER.RETURN_PAYMENT_REQUIRE_BEFORE,
            PATCHER.RETURN_PAYMENT_INVALID_BEFORE,
            PATCHER.RETURN_PAYMENT_FORM_BEFORE,
            PATCHER.RETURN_PAYMENT_DESIGN_BEFORE,
            PATCHER.RETURN_PAYMENT_APPLY_BEFORE,
            "            " + PATCHER.RETURN_PAYMENT_CLEANUP_BEFORE,
            "        }",
            "",
        )
    )


def legacy_guard_dialog_source() -> str:
    """Return a previous Rubrova build: four guard edits, but old cleanup retained."""
    source = upstream_dialog_source()
    replacements = (
        (PATCHER.RETURN_PAYMENT_REQUIRE_BEFORE, PATCHER.RETURN_PAYMENT_REQUIRE_AFTER),
        (PATCHER.RETURN_PAYMENT_INVALID_BEFORE, PATCHER.RETURN_PAYMENT_INVALID_AFTER),
        (PATCHER.RETURN_PAYMENT_FORM_BEFORE, PATCHER.RETURN_PAYMENT_FORM_AFTER),
        (PATCHER.RETURN_PAYMENT_DESIGN_BEFORE, PATCHER.RETURN_PAYMENT_DESIGN_AFTER),
        (PATCHER.RETURN_PAYMENT_APPLY_BEFORE, PATCHER.RETURN_PAYMENT_APPLY_AFTER),
    )
    for before, after in replacements:
        if source.count(before) != 1:
            raise AssertionError(f"Fixture legacy inválida: falta ancla {before!r}")
        source = source.replace(before, after, 1)
    return source


def broad_cleanup_guard_dialog_source() -> str:
    """Return the broad-cleanup revision so the patcher must narrow its scope."""
    source = legacy_guard_dialog_source()
    if source.count(PATCHER.RETURN_PAYMENT_CLEANUP_BEFORE) != 1:
        raise AssertionError("Fixture legacy inválida: falta la limpieza IncomingPayment")
    return source.replace(
        PATCHER.RETURN_PAYMENT_CLEANUP_BEFORE,
        PATCHER.RETURN_PAYMENT_CLEANUP_LEGACY_BROAD,
        1,
    )


class CumulativeRefundPatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="rubrova-refund-patch-")
        self.target = Path(self.temp_dir.name) / "PosDashboardReturnPayment.lsf"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_source(self, source: str) -> None:
        self.target.write_text(source, encoding="utf-8")

    def apply_patch(self) -> tuple[bool, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.object(PATCHER, "RETURN_PAYMENT_TARGET", self.target):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = PATCHER.apply_cumulative_refund_guard()
        return result, stdout.getvalue(), stderr.getvalue()

    def assert_patched_once(self, source: str) -> None:
        for marker in (
            PATCHER.RETURN_PAYMENT_REQUIRE_AFTER,
            PATCHER.RETURN_PAYMENT_INVALID_AFTER,
            PATCHER.RETURN_PAYMENT_FORM_AFTER,
            PATCHER.RETURN_PAYMENT_DESIGN_AFTER,
            PATCHER.RETURN_PAYMENT_APPLY_AFTER,
            PATCHER.RETURN_PAYMENT_CLEANUP_AFTER,
        ):
            self.assertEqual(source.count(marker), 1, marker)
        for marker in (
            PATCHER.RETURN_PAYMENT_REQUIRE_BEFORE,
            PATCHER.RETURN_PAYMENT_INVALID_BEFORE,
            PATCHER.RETURN_PAYMENT_FORM_BEFORE,
            PATCHER.RETURN_PAYMENT_DESIGN_BEFORE,
            PATCHER.RETURN_PAYMENT_APPLY_BEFORE,
            PATCHER.RETURN_PAYMENT_CLEANUP_BEFORE,
        ):
            self.assertNotIn(marker, source)

    def test_clean_upstream_source_receives_all_refund_guard_changes(self) -> None:
        self.write_source(upstream_dialog_source())

        result, output, error = self.apply_patch()

        self.assertTrue(result, error)
        patched = self.target.read_text(encoding="utf-8")
        self.assert_patched_once(patched)
        self.assertIn("Reintegros POS protegidos", output)

    def test_legacy_four_change_state_upgrades_only_rejected_apply_cleanup(self) -> None:
        legacy = legacy_guard_dialog_source()
        self.write_source(legacy)

        result, output, error = self.apply_patch()

        self.assertTrue(result, error)
        patched = self.target.read_text(encoding="utf-8")
        self.assert_patched_once(patched)
        self.assertIn("Guard acumulado actualizado", output)
        self.assertEqual(
            patched.replace(PATCHER.RETURN_PAYMENT_CLEANUP_AFTER, PATCHER.RETURN_PAYMENT_CLEANUP_BEFORE),
            legacy,
            "La migración debe cambiar únicamente la limpieza del pago rechazado.",
        )

    def test_legacy_broad_cleanup_is_narrowed_to_the_current_refund_bill(self) -> None:
        legacy = broad_cleanup_guard_dialog_source()
        self.write_source(legacy)

        result, output, error = self.apply_patch()

        self.assertTrue(result, error)
        patched = self.target.read_text(encoding="utf-8")
        self.assert_patched_once(patched)
        self.assertIn("Guard acumulado actualizado", output)
        self.assertEqual(
            patched.replace(
                PATCHER.RETURN_PAYMENT_CLEANUP_AFTER,
                PATCHER.RETURN_PAYMENT_CLEANUP_LEGACY_BROAD,
            ),
            legacy,
            "La migración debe acotar únicamente el DELETE de egresos rechazados.",
        )
        self.assertIn("AND paymentMethod(b, p)", PATCHER.RETURN_PAYMENT_CLEANUP_AFTER)

    def test_running_the_patch_twice_is_idempotent(self) -> None:
        self.write_source(upstream_dialog_source())
        first_result, _, first_error = self.apply_patch()
        self.assertTrue(first_result, first_error)
        first_content = self.target.read_text(encoding="utf-8")

        second_result, second_output, second_error = self.apply_patch()

        self.assertTrue(second_result, second_error)
        self.assertEqual(self.target.read_text(encoding="utf-8"), first_content)
        self.assertIn("ya aplicados", second_output)

    def test_partially_applied_guard_fails_without_mutating_source(self) -> None:
        partial = upstream_dialog_source().replace(
            PATCHER.RETURN_PAYMENT_REQUIRE_BEFORE,
            PATCHER.RETURN_PAYMENT_REQUIRE_AFTER,
            1,
        ).replace(
            PATCHER.RETURN_PAYMENT_INVALID_BEFORE,
            PATCHER.RETURN_PAYMENT_INVALID_AFTER,
            1,
        )
        self.write_source(partial)

        result, _, error = self.apply_patch()

        self.assertFalse(result)
        self.assertIn("parcialmente aplicado", error)
        self.assertEqual(self.target.read_text(encoding="utf-8"), partial)

    def test_source_drift_fails_closed_without_writing(self) -> None:
        drifted = upstream_dialog_source().replace(
            PATCHER.RETURN_PAYMENT_DESIGN_BEFORE,
            "PROPERTY(unexpectedLegacyProperty(b, pm)) { fontSize = 24; }",
            1,
        )
        self.write_source(drifted)

        result, _, error = self.apply_patch()

        self.assertFalse(result)
        self.assertIn("exactamente una coincidencia", error)
        self.assertEqual(self.target.read_text(encoding="utf-8"), drifted)

    def test_missing_target_fails_without_creating_a_file(self) -> None:
        result, _, error = self.apply_patch()

        self.assertFalse(result)
        self.assertIn("No se encontró el flujo nativo", error)
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
