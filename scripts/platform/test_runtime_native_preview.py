#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import subprocess
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("run-local-native-preview.py")
SPEC = importlib.util.spec_from_file_location("rubrova_native_preview", SCRIPT)
assert SPEC and SPEC.loader
native = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(native)


class FakeProcess:
    returncode = None

    def poll(self):
        return self.returncode


class NativePreviewTests(unittest.TestCase):
    def test_server_readiness_requires_rmi_and_onstarted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            log_dir = Path(temporary)
            (log_dir / "start.log").write_text(
                "Server has successfully started in 120 ms\n"
                "Executing onStarted action finished\n",
                encoding="utf-8",
            )
            with patch.object(native, "port_is_open", return_value=True):
                native.wait_for_server_ready(FakeProcess(), log_dir, 17652, timeout=1)

    def test_server_readiness_does_not_accept_early_start_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            log_dir = Path(temporary)
            (log_dir / "start.log").write_text(
                "Server has successfully started in 120 ms\n",
                encoding="utf-8",
            )
            with (
                patch.object(native, "port_is_open", return_value=True),
                patch.object(native.time, "monotonic", side_effect=[0.0, 0.0, 2.0]),
                patch.object(native.time, "sleep", return_value=None),
            ):
                with self.assertRaisesRegex(native.RuntimeErrorRubrova, "onStarted"):
                    native.wait_for_server_ready(FakeProcess(), log_dir, 17652, timeout=1)

    def test_server_exit_during_startup_reports_exit_code(self) -> None:
        process = FakeProcess()
        process.returncode = 17
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(native.RuntimeErrorRubrova, "código 17"):
                native.wait_for_server_ready(process, Path(temporary), 7652, timeout=5)

    def test_configured_tomcat_home_is_used_and_version_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tomcat_home = root / "configured-tomcat"
            (tomcat_home / "bin").mkdir(parents=True)
            (tomcat_home / "lib").mkdir(parents=True)
            (tomcat_home / "bin" / "catalina.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            with zipfile.ZipFile(tomcat_home / "lib" / "catalina.jar", "w") as archive:
                archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\nImplementation-Version: 9.0.124\n")
            selected = native.download_tomcat(
                root / "empty-cache",
                allow_download=False,
                configured_home=str(tomcat_home),
            )
            self.assertEqual(selected, tomcat_home.resolve())

    def test_configured_tomcat_with_wrong_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tomcat_home = root / "wrong-tomcat"
            (tomcat_home / "bin").mkdir(parents=True)
            (tomcat_home / "lib").mkdir(parents=True)
            (tomcat_home / "bin" / "catalina.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            with zipfile.ZipFile(tomcat_home / "lib" / "catalina.jar", "w") as archive:
                archive.writestr("META-INF/MANIFEST.MF", "Manifest-Version: 1.0\nImplementation-Version: 10.1.0\n")
            with self.assertRaisesRegex(native.RuntimeErrorRubrova, "requiere Apache Tomcat 9.0.124"):
                native.download_tomcat(
                    root / "empty-cache",
                    allow_download=False,
                    configured_home=str(tomcat_home),
                )

    def test_ci_sales_fixture_is_added_to_a_temporary_runtime_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            logics_dir = Path(temporary)
            entrypoint = logics_dir / "RubrovaCustom.lsf"
            entrypoint.write_text(
                "MODULE RubrovaCustom;\\n"
                "REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaIntegrationResilience, RubrovaPaymentTerminals;\\n",
                encoding="utf-8",
            )
            previous_port = native.os.environ.get("RUBROVA_CI_MOCK_PROVIDER_PORT")
            native.os.environ["RUBROVA_CI_MOCK_PROVIDER_PORT"] = "18766"
            try:
                native.ensure_ci_sales_fixture(logics_dir)
                native.ensure_ci_sales_fixture(logics_dir)
            finally:
                if previous_port is None:
                    native.os.environ.pop("RUBROVA_CI_MOCK_PROVIDER_PORT", None)
                else:
                    native.os.environ["RUBROVA_CI_MOCK_PROVIDER_PORT"] = previous_port

            updated_entrypoint = entrypoint.read_text(encoding="utf-8")
            self.assertEqual(updated_entrypoint.count("RubrovaCISalesFixture"), 1)
            self.assertIn("RubrovaCIRetailFixture", updated_entrypoint)
            self.assertIn("RubrovaCIIntegrationFixture", updated_entrypoint)
            sales_fixture = (logics_dir / "RubrovaCISalesFixture.lsf").read_text(encoding="utf-8")
            retail_fixture = (logics_dir / "RubrovaCIRetailFixture.lsf").read_text(encoding="utf-8")
            integration_fixture = (logics_dir / "RubrovaCIIntegrationFixture.lsf").read_text(encoding="utf-8")
            self.assertIn("REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaCIRetailFixture;", sales_fixture)
            self.assertIn("rubrovaTestSalesReconciliationApi", sales_fixture)
            self.assertIn("rubrovaTestSessionCloseApi", sales_fixture)
            self.assertIn("Caja de prueba Rubrova", retail_fixture)
            self.assertIn("http://127.0.0.1:18766/slow?delay=5", integration_fixture)

    def test_ci_sales_fixture_rejects_invalid_mock_provider_port(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            logics_dir = Path(temporary)
            (logics_dir / "RubrovaCustom.lsf").write_text(
                "MODULE RubrovaCustom;\\n"
                "REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaIntegrationResilience, RubrovaPaymentTerminals;\\n",
                encoding="utf-8",
            )
            previous_port = native.os.environ.get("RUBROVA_CI_MOCK_PROVIDER_PORT")
            native.os.environ["RUBROVA_CI_MOCK_PROVIDER_PORT"] = "80"
            try:
                with self.assertRaisesRegex(native.RuntimeErrorRubrova, "entre 1024 y 65535"):
                    native.ensure_ci_sales_fixture(logics_dir)
            finally:
                if previous_port is None:
                    native.os.environ.pop("RUBROVA_CI_MOCK_PROVIDER_PORT", None)
                else:
                    native.os.environ["RUBROVA_CI_MOCK_PROVIDER_PORT"] = previous_port

    def test_local_demo_fixture_is_added_to_temporary_runtime_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            logics_dir = Path(temporary)
            entrypoint = logics_dir / "RubrovaCustom.lsf"
            entrypoint.write_text(
                "MODULE RubrovaCustom;\\n"
                "REQUIRE MyCompany, RubrovaPOSLocalization, RubrovaIntegrationResilience, RubrovaPaymentTerminals;\\n",
                encoding="utf-8",
            )

            native.ensure_local_demo_fixture(logics_dir)
            native.ensure_local_demo_fixture(logics_dir)

            updated_entrypoint = entrypoint.read_text(encoding="utf-8")
            self.assertEqual(updated_entrypoint.count("RubrovaLocalDemoRetail"), 1)
            self.assertEqual(updated_entrypoint.count("RubrovaLocalDemoInventory"), 1)
            retail_fixture = (logics_dir / "RubrovaLocalDemoRetail.lsf").read_text(encoding="utf-8")
            inventory_fixture = (logics_dir / "RubrovaLocalDemoInventory.lsf").read_text(encoding="utf-8")
            self.assertIn("Caja de demostración Rubrova", retail_fixture)
            self.assertIn("Producto de demostración Rubrova", retail_fixture)
            self.assertIn("rubrova-demo", retail_fixture)
            self.assertIn("Inventory.realQuantity(adjustmentLineDemo) <- 10", inventory_fixture)
            self.assertIn("rubrova-demo-location", inventory_fixture)
            self.assertNotIn("@@api", retail_fixture + inventory_fixture)
            self.assertNotIn("rubrovaTest", retail_fixture + inventory_fixture)
            self.assertNotIn("mock-provider", retail_fixture + inventory_fixture)

    def test_demo_config_uses_an_isolated_database_and_distinct_ports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_path = root / "demo-runtime-config.json"
            with patch.object(native, "user_data_root", return_value=root):
                config = native.runtime_config.default_config()
                config["local_runtime"]["java_home"] = "/example/jdk-21"
                native.runtime_config.write_config(config_path, config)

                native.initialize_demo_config(config_path)
                result = native.load_config(config_path)

            self.assertEqual(result["execution"]["target"], "native-local")
            self.assertEqual(result["local_runtime"]["data_directory"], str(root / "demo-preview"))
            self.assertEqual(result["local_runtime"]["ports"], {"postgres": 55433, "rmi": 17653, "web": 8081})
            self.assertEqual(result["local_runtime"]["java_home"], "/example/jdk-21")

    def test_demo_config_refuses_to_modify_the_normal_runtime_config(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch.object(native, "user_data_root", return_value=root):
                with self.assertRaisesRegex(native.RuntimeErrorRubrova, "demo-runtime-config.json separado"):
                    native.initialize_demo_config(root / "runtime-config.json")

    def test_demo_ui_smoke_uses_the_register_seeded_by_its_fixture(self) -> None:
        inspector = Path(__file__).with_name("inspect-mycompany-ui.py").read_text(encoding="utf-8")
        smoke = Path(__file__).with_name("test-runtime-native-smoke.sh").read_text(encoding="utf-8")
        fixture = Path(__file__).with_name("fixtures") / "RubrovaLocalDemoRetail.lsf"
        fixture_text = fixture.read_text(encoding="utf-8")

        self.assertIn('register_name: str = "Caja de prueba Rubrova"', inspector)
        self.assertIn("register_name=pos_register_name", inspector)
        self.assertIn('RUBROVA_UI_POS_REGISTER_NAME="Caja de demostración Rubrova"', smoke)
        self.assertIn("name(cashRegisterDemo) <- 'Caja de demostración Rubrova'", fixture_text)

    def test_preexisting_postgres_is_never_stopped_by_preview_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data_dir = Path(temporary) / "postgres-data"
            data_dir.mkdir()
            (data_dir / "PG_VERSION").write_text("18\n", encoding="utf-8")
            with patch.object(native.subprocess, "run") as run:
                native.stop_postgres(Path(temporary) / "bin", data_dir, started_by_this_process=False)
                run.assert_not_called()

    def test_postgres_cluster_status_is_scoped_to_rubrova_data_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            data_dir = Path(temporary) / "postgres-data"
            data_dir.mkdir()
            (data_dir / "PG_VERSION").write_text("18\n", encoding="utf-8")
            completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="server is running\n")
            with patch.object(native.subprocess, "run", return_value=completed) as run:
                self.assertTrue(native.postgres_cluster_is_running(Path(temporary) / "bin" / "pg_ctl", data_dir))
                self.assertIn(str(data_dir), run.call_args.args[0])

    def test_tomcat_web_xml_and_connector_are_bound_to_loopback_and_configured_ports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tomcat_home = root / "tomcat"
            (tomcat_home / "conf").mkdir(parents=True)
            (tomcat_home / "conf" / "server.xml").write_text(
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<Server><Service><Connector port="8080" protocol="HTTP/1.1"/></Service></Server>',
                encoding="utf-8",
            )
            war = root / "client.war"
            web_xml = """<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://java.sun.com/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_2_5.xsd"
         version="2.5">
  <context-param><param-name>host</param-name><param-value>localhost</param-value></context-param>
  <context-param><param-name>port</param-name><param-value>7652</param-value></context-param>
  <context-param><param-name>exportName</param-name><param-value>default</param-value></context-param>
  <servlet>
    <servlet-name>LSFWeb</servlet-name>
    <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
    <load-on-startup>1</load-on-startup>
  </servlet>
  <servlet-mapping>
    <servlet-name>LSFWeb</servlet-name>
    <url-pattern>/login</url-pattern>
    <url-pattern>/main</url-pattern>
  </servlet-mapping>
  <welcome-file-list><welcome-file>main</welcome-file></welcome-file-list>
</web-app>
"""
            with zipfile.ZipFile(war, "w") as archive:
                archive.writestr("WEB-INF/web.xml", web_xml)
                archive.writestr("index.html", "ok")
            base = root / "tomcat-base"
            native.prepare_tomcat_base(
                tomcat_home,
                base,
                war,
                {"postgres": 55432, "rmi": 17652, "web": 18080},
            )

            deployed_xml = base / "webapps" / "ROOT" / "WEB-INF" / "web.xml"
            deployed_text = deployed_xml.read_text(encoding="utf-8")
            self.assertIn('xmlns="http://java.sun.com/xml/ns/javaee"', deployed_text)
            self.assertNotIn("<ns0:web-app", deployed_text)
            deployed_root = ET.parse(deployed_xml).getroot()
            namespace = deployed_root.tag.split("}", 1)[0] + "}" if deployed_root.tag.startswith("{") else ""
            servlet_classes = {}
            for servlet in deployed_root.findall(f"{namespace}servlet"):
                name = servlet.find(f"{namespace}servlet-name")
                servlet_class = servlet.find(f"{namespace}servlet-class")
                if name is not None and name.text:
                    servlet_classes[name.text] = servlet_class.text.strip() if servlet_class is not None and servlet_class.text else ""
            mappings = {}
            for mapping in deployed_root.findall(f"{namespace}servlet-mapping"):
                name = mapping.find(f"{namespace}servlet-name")
                patterns = [
                    pattern.text.strip()
                    for pattern in mapping.findall(f"{namespace}url-pattern")
                    if pattern.text and pattern.text.strip()
                ]
                if name is not None and name.text:
                    mappings[name.text] = patterns
            self.assertEqual(servlet_classes.get("LSFWeb"), "org.springframework.web.servlet.DispatcherServlet")
            self.assertIn("/login", mappings.get("LSFWeb", []))
            self.assertIn("/main", mappings.get("LSFWeb", []))
            params = {}
            for item in deployed_root.findall(f"{namespace}context-param"):
                name = item.find(f"{namespace}param-name")
                value = item.find(f"{namespace}param-value")
                if name is not None and value is not None:
                    params[name.text or ""] = value.text
            self.assertEqual(params.get("host"), "127.0.0.1")
            self.assertEqual(params.get("port"), "17652")

            server_xml = ET.parse(base / "conf" / "server.xml").getroot()
            connector = server_xml.find(".//Connector")
            self.assertIsNotNone(connector)
            self.assertEqual(connector.get("port"), "18080")
            self.assertEqual(connector.get("address"), "127.0.0.1")

    def test_missing_rmi_parameters_in_client_war_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tomcat_home = root / "tomcat"
            (tomcat_home / "conf").mkdir(parents=True)
            (tomcat_home / "conf" / "server.xml").write_text(
                '<Server><Service><Connector port="8080"/></Service></Server>',
                encoding="utf-8",
            )
            war = root / "client.war"
            with zipfile.ZipFile(war, "w") as archive:
                archive.writestr("WEB-INF/web.xml", "<web-app/>")
            with self.assertRaisesRegex(native.RuntimeErrorRubrova, "parámetros RMI requeridos"):
                native.prepare_tomcat_base(
                    tomcat_home,
                    root / "tomcat-base",
                    war,
                    {"postgres": 55432, "rmi": 7652, "web": 8080},
                )

    def test_invalid_war_path_is_rejected_before_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tomcat_home = root / "tomcat"
            (tomcat_home / "conf").mkdir(parents=True)
            (tomcat_home / "conf" / "server.xml").write_text(
                '<Server><Service><Connector port="8080"/></Service></Server>',
                encoding="utf-8",
            )
            war = root / "unsafe.war"
            with zipfile.ZipFile(war, "w") as archive:
                archive.writestr("../outside.txt", "not allowed")
                archive.writestr(
                    "WEB-INF/web.xml",
                    '<web-app><context-param><param-name>host</param-name><param-value>localhost</param-value></context-param><context-param><param-name>port</param-name><param-value>7652</param-value></context-param></web-app>',
                )
            with self.assertRaisesRegex(native.RuntimeErrorRubrova, "ruta no segura"):
                native.prepare_tomcat_base(
                    tomcat_home,
                    root / "tomcat-base",
                    war,
                    {"postgres": 55432, "rmi": 7652, "web": 8080},
                )


    def test_tomcat_404_fails_fast_and_includes_deployment_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            logs = root / "logs"
            logs.mkdir()
            (logs / "rubrova-console.log").write_text(
                "SEVERE: One or more listeners failed to start; password=never-print-this\n",
                encoding="utf-8",
            )
            (logs / "localhost.2026-11-24.log").write_text(
                "Context startup failed due to previous errors\n",
                encoding="utf-8",
            )
            web_xml = root / "webapps" / "ROOT" / "WEB-INF" / "web.xml"
            web_xml.parent.mkdir(parents=True)
            web_xml.write_text(
                '<web-app><welcome-file-list><welcome-file>main</welcome-file></welcome-file-list></web-app>',
                encoding="utf-8",
            )
            error = native.urllib.error.HTTPError(
                "http://127.0.0.1:18080/",
                404,
                "Not Found",
                {},
                io.BytesIO(b"<html>Not Found</html>"),
            )
            with (
                patch.object(native.urllib.request, "urlopen", side_effect=error),
                self.assertRaises(native.RuntimeErrorRubrova) as captured,
            ):
                native.wait_for_web(
                    "http://127.0.0.1:18080/",
                    FakeProcess(),
                    tomcat_base=root,
                    timeout=30,
                    not_found_grace_seconds=0,
                )

            message = str(captured.exception)
            self.assertIn("HTTP 404", message)
            self.assertIn("One or more listeners failed to start", message)
            self.assertIn("Página de bienvenida configurada: main", message)
            self.assertIn("[redactado]", message)
            self.assertNotIn("never-print-this", message)

    def test_tomcat_web_startup_accepts_a_successful_response(self) -> None:
        class SuccessfulResponse:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

        with patch.object(native.urllib.request, "urlopen", return_value=SuccessfulResponse()):
            self.assertIsNone(
                native.wait_for_web(
                    "http://127.0.0.1:18080/",
                    FakeProcess(),
                    timeout=5,
                )
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
