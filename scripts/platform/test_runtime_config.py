#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("runtime-config.py")
SPEC = importlib.util.spec_from_file_location("rubrova_runtime_config", SCRIPT)
assert SPEC and SPEC.loader
runtime_config = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime_config)


class RuntimeConfigTests(unittest.TestCase):
    def test_default_target_is_native_without_docker(self) -> None:
        config = runtime_config.default_config()
        self.assertEqual(config["execution"]["target"], "native-local")
        self.assertEqual(config["connectivity"]["external_integrations"], "enabled")
        self.assertEqual(runtime_config.validate_config(config), [])

    def test_local_execution_and_external_connectivity_are_independent(self) -> None:
        config = runtime_config.default_config()
        config["connectivity"]["external_integrations"] = "paused"
        self.assertEqual(config["execution"]["target"], "native-local")
        self.assertEqual(runtime_config.validate_config(config), [])

    def test_remote_target_requires_https_endpoint(self) -> None:
        config = runtime_config.default_config()
        with self.assertRaisesRegex(ValueError, "remote_url"):
            runtime_config.set_target(
                config,
                "remote-online",
                acknowledge_data_authority_change=True,
            )

        updated = runtime_config.set_target(
            config,
            "remote-online",
            remote_url="https://pos.example.com",
            acknowledge_data_authority_change=True,
        )
        self.assertEqual(updated["execution"]["target"], "remote-online")

    def test_plain_http_is_only_allowed_for_loopback_development(self) -> None:
        config = runtime_config.default_config()
        config["execution"]["target"] = "remote-online"
        config["execution"]["remote_url"] = "http://192.168.1.20:8080"
        self.assertTrue(any("TLS" in error for error in runtime_config.validate_config(config)))

        config["execution"]["remote_url"] = "http://127.0.0.1:8080"
        self.assertEqual(runtime_config.validate_config(config), [])

    def test_changing_database_authority_requires_explicit_acknowledgement(self) -> None:
        config = runtime_config.default_config()
        with self.assertRaisesRegex(ValueError, "respaldar"):
            runtime_config.set_target(config, "docker-local")
        updated = runtime_config.set_target(
            config,
            "docker-local",
            acknowledge_data_authority_change=True,
        )
        self.assertEqual(updated["execution"]["target"], "docker-local")

    def test_native_and_docker_do_not_need_remote_url(self) -> None:
        config = runtime_config.default_config()
        config["execution"]["target"] = "docker-local"
        self.assertEqual(runtime_config.validate_config(config), [])

    def test_duplicate_or_privileged_ports_are_rejected(self) -> None:
        config = runtime_config.default_config()
        config["local_runtime"]["ports"]["rmi"] = 55432
        self.assertTrue(any("distintos" in error for error in runtime_config.validate_config(config)))
        config["local_runtime"]["ports"]["rmi"] = 7652
        config["local_runtime"]["ports"]["web"] = 80
        self.assertTrue(any("1024" in error for error in runtime_config.validate_config(config)))

    def test_credentials_are_not_accepted_in_config(self) -> None:
        config = runtime_config.default_config()
        config["execution"]["password"] = "not-allowed"
        self.assertTrue(any("secretos" in error for error in runtime_config.validate_config(config)))

    def test_config_is_written_atomically_and_read_back(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "config" / "runtime-config.json"
            config = runtime_config.default_config()
            runtime_config.write_config(path, config)
            loaded = runtime_config.read_config(path)
            self.assertEqual(loaded, config)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), config)
            if os.name != "nt":
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(path.parent.glob(".runtime-config-*.tmp")), [])

    def test_invalid_or_partial_configuration_is_rejected(self) -> None:
        config = runtime_config.default_config()
        del config["local_runtime"]["ports"]
        self.assertTrue(runtime_config.validate_config(config))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "runtime-config.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No se pudo leer"):
                runtime_config.read_config(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
