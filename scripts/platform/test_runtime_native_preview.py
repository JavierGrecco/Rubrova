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
<web-app xmlns="http://java.sun.com/xml/ns/javaee" version="2.5">
  <context-param><param-name>host</param-name><param-value>localhost</param-value></context-param>
  <context-param><param-name>port</param-name><param-value>7652</param-value></context-param>
  <context-param><param-name>exportName</param-name><param-value>default</param-value></context-param>
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
            deployed_root = ET.parse(deployed_xml).getroot()
            namespace = deployed_root.tag.split("}", 1)[0] + "}" if deployed_root.tag.startswith("{") else ""
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
