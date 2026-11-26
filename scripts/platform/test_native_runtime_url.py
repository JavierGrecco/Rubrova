"""Regression tests for native runtime endpoint and export contracts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from native_runtime_url import application_endpoint_url


class NativeReplenishmentExportContractTests(unittest.TestCase):
    def test_ui_smoke_schema_matches_native_exporter_and_adapter(self) -> None:
        repository = Path(__file__).resolve().parents[2]
        inspector = (repository / "scripts/platform/inspect-mycompany-ui.py").read_text(encoding="utf-8")
        adapter = (repository / "scripts/replenishment/adapt_mycompany_native_export.py").read_text(encoding="utf-8")
        exporter = (repository / "extensions/lsfusion/RubrovaReplenishmentExport.lsf").read_text(encoding="utf-8")

        inspector_version = re.search(
            r"^NATIVE_EXPORT_SCHEMA_VERSION\s*=\s*(\d+)\s*$", inspector, re.MULTILINE
        )
        adapter_version = re.search(r'^\s*"schemaVersion":\s*(\d+),$', adapter, re.MULTILINE)
        exporter_version = re.search(r"^\s*schemaVersion\s*=\s*(\d+),$", exporter, re.MULTILINE)

        self.assertIsNotNone(inspector_version, "El inspector debe declarar la versión del contrato nativo.")
        self.assertIsNotNone(adapter_version, "El adaptador debe declarar la versión del contrato nativo.")
        self.assertIsNotNone(exporter_version, "El exportador lsFusion debe declarar la versión del contrato nativo.")
        self.assertIn('"schemaVersion": NATIVE_EXPORT_SCHEMA_VERSION', inspector)

        versions = {
            int(inspector_version.group(1)),
            int(adapter_version.group(1)),
            int(exporter_version.group(1)),
        }
        self.assertEqual(
            len(versions),
            1,
            "El smoke de interfaz, el adaptador y el exportador nativo deben compartir la misma schemaVersion.",
        )


class ApplicationEndpointUrlTests(unittest.TestCase):
    def test_login_route_does_not_become_an_api_path_prefix(self) -> None:
        self.assertEqual(
            application_endpoint_url(
                "http://127.0.0.1:8080/login",
                "exec/Rubrova.rubrovaTestPosConfigurationApi",
            ),
            "http://127.0.0.1:8080/exec/Rubrova.rubrovaTestPosConfigurationApi",
        )

    def test_main_route_does_not_become_an_api_path_prefix(self) -> None:
        self.assertEqual(
            application_endpoint_url(
                "http://127.0.0.1:8080/main",
                "/exec/Sales.rubrovaTestSalesReconciliationApi",
            ),
            "http://127.0.0.1:8080/exec/Sales.rubrovaTestSalesReconciliationApi",
        )

    def test_root_endpoint_directory_keeps_its_trailing_slash(self) -> None:
        self.assertEqual(
            application_endpoint_url("http://localhost:8080/login", "exec/"),
            "http://localhost:8080/exec/",
        )

    def test_query_string_from_page_url_is_not_copied(self) -> None:
        self.assertEqual(
            application_endpoint_url("http://localhost:8080/login?next=home", "exec/Rubrova.test"),
            "http://localhost:8080/exec/Rubrova.test",
        )

    def test_rejects_a_base_without_an_http_host(self) -> None:
        with self.assertRaises(ValueError):
            application_endpoint_url("/login", "exec/Rubrova.test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
