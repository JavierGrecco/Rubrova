"""Regression tests for native runtime endpoint URL construction."""

from __future__ import annotations

import unittest

from native_runtime_url import application_endpoint_url


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
