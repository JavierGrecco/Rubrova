#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("native-postgres-backup.py")
SPEC = importlib.util.spec_from_file_location("rubrova_native_postgres_backup", SCRIPT)
assert SPEC and SPEC.loader
backup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backup)


class NativePostgresBackupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.data_root = self.root / "rubrova-data"
        self.pg_data = self.data_root / "postgres-data"
        self.pg_data.mkdir(parents=True)
        (self.pg_data / "PG_VERSION").write_text("18\n", encoding="utf-8")
        self.config_path = self.root / "runtime-config.json"
        self.config = backup.runtime_config.default_config()
        self.config["local_runtime"]["data_directory"] = str(self.data_root)
        self.config["local_runtime"]["postgres_bin"] = "/fake/postgres/bin"
        self.config["local_runtime"]["ports"]["postgres"] = 55432
        backup.runtime_config.write_config(self.config_path, self.config)
        self.tools = {
            name: Path(f"/fake/postgres/bin/{name}")
            for name in ("pg_dump", "pg_restore", "psql", "createdb", "dropdb")
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def fake_run(self, command: list[str], **kwargs):
        name = Path(command[0]).name
        if name == "psql":
            sql = command[command.index("-c") + 1]
            if "current_setting('data_directory')" in sql:
                output = f"{self.pg_data}|55432|180001|18.1"
            elif "FROM pg_database" in sql:
                output = "1"
            elif "FROM pg_class" in sql:
                output = "4"
            else:
                output = ""
            return subprocess.CompletedProcess(command, 0, output)
        if name in ("pg_dump", "pg_restore") and "--version" in command:
            return subprocess.CompletedProcess(command, 0, f"{name} (PostgreSQL) 18.1")
        if name == "pg_dump":
            output_path = Path(command[command.index("--file") + 1])
            output_path.write_bytes(b"synthetic PostgreSQL custom archive")
            return subprocess.CompletedProcess(command, 0, "dump complete")
        if name == "pg_restore" and "--list" in command:
            return subprocess.CompletedProcess(command, 0, "; Archive created at test\n; TOC Entries: 3")
        return subprocess.CompletedProcess(command, 0, "")

    def create_fixture_bundle(self, path: Path) -> None:
        dump = b"synthetic PostgreSQL custom archive"
        manifest = {
            "format": backup.FORMAT_NAME,
            "formatVersion": backup.FORMAT_VERSION,
            "createdAtUtc": "2026-11-26T00:00:00Z",
            "scope": "postgresql-database-only",
            "database": {"name": backup.DATABASE_NAME, "port": 55432, "serverVersionNum": 180001},
            "dump": {
                "file": backup.DUMP_NAME,
                "sizeBytes": len(dump),
                "sha256": __import__("hashlib").sha256(dump).hexdigest(),
            },
        }
        manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr(backup.DUMP_NAME, dump)
            archive.writestr(backup.MANIFEST_NAME, manifest_bytes)
            archive.writestr(
                backup.MANIFEST_CHECKSUM_NAME,
                __import__("hashlib").sha256(manifest_bytes).hexdigest() + "\n",
            )

    def test_create_generates_database_only_bundle_and_reopens_it_for_verification(self) -> None:
        output = self.root / "backups" / "first.rubrova-db-backup"
        with (
            patch.object(backup, "find_pg_tools", return_value=self.tools),
            patch.object(backup, "run_checked", side_effect=self.fake_run),
        ):
            result = backup.create_backup(self.config_path, output, revision="f545c907")
            manifest = backup.verify_backup(result, self.config_path)

        self.assertEqual(result, output)
        self.assertTrue(output.is_file())
        self.assertEqual(manifest["scope"], "postgresql-database-only")
        self.assertEqual(manifest["sourceRevision"], "f545c907")
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(set(archive.namelist()), backup.EXPECTED_ENTRIES)
            self.assertIn(b"synthetic PostgreSQL", archive.read(backup.DUMP_NAME))

    def test_create_refuses_a_postgres_server_from_another_data_directory(self) -> None:
        def wrong_cluster(command, **kwargs):
            if Path(command[0]).name == "psql":
                return subprocess.CompletedProcess(command, 0, "/other/cluster|55432|180001|18.1")
            return self.fake_run(command, **kwargs)

        with (
            patch.object(backup, "find_pg_tools", return_value=self.tools),
            patch.object(backup, "run_checked", side_effect=wrong_cluster),
        ):
            with self.assertRaisesRegex(backup.BackupError, "no pertenece"):
                backup.create_backup(self.config_path, self.root / "unsafe.rubrova-db-backup")

    def test_tampered_dump_is_rejected_before_pg_restore(self) -> None:
        bundle = self.root / "tampered.rubrova-db-backup"
        self.create_fixture_bundle(bundle)
        with zipfile.ZipFile(bundle) as original:
            entries = {name: original.read(name) for name in original.namelist()}
        entries[backup.DUMP_NAME] = b"changed bytes"
        with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_STORED) as changed:
            for name, content in entries.items():
                changed.writestr(name, content)

        with patch.object(backup, "run_checked") as run:
            with tempfile.TemporaryDirectory() as temp:
                with self.assertRaisesRegex(backup.BackupError, "SHA-256"):
                    backup.extract_and_validate_bundle(bundle, Path(temp), self.tools["pg_restore"])
            run.assert_not_called()

    def test_manifest_checksum_is_checked(self) -> None:
        bundle = self.root / "bad-manifest.rubrova-db-backup"
        self.create_fixture_bundle(bundle)
        with zipfile.ZipFile(bundle) as original:
            entries = {name: original.read(name) for name in original.namelist()}
        entries[backup.MANIFEST_NAME] = entries[backup.MANIFEST_NAME] + b" "
        with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_STORED) as changed:
            for name, content in entries.items():
                changed.writestr(name, content)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(backup.BackupError, "manifiesto"):
                backup.extract_and_validate_bundle(bundle, Path(temp), self.tools["pg_restore"])

    def test_bundle_rejects_unexpected_files_and_duplicate_entries(self) -> None:
        bundle = self.root / "extra.rubrova-db-backup"
        self.create_fixture_bundle(bundle)
        with zipfile.ZipFile(bundle, "a") as archive:
            archive.writestr("secrets.txt", "not allowed")
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(backup.BackupError, "únicamente"):
                backup.extract_and_validate_bundle(bundle, Path(temp), self.tools["pg_restore"])

    def test_restore_requires_explicit_confirmation_and_a_new_database_name(self) -> None:
        bundle = self.root / "restore.rubrova-db-backup"
        self.create_fixture_bundle(bundle)
        with self.assertRaisesRegex(backup.BackupError, "confirm-new-database"):
            backup.restore_backup(bundle, self.config_path, "restore_check", False)
        with self.assertRaisesRegex(backup.BackupError, "base nueva"):
            backup.restore_backup(bundle, self.config_path, "rubrova_dev", True)

    def test_restore_refuses_existing_database_without_running_createdb(self) -> None:
        bundle = self.root / "restore-existing.rubrova-db-backup"
        self.create_fixture_bundle(bundle)
        with (
            patch.object(backup, "find_pg_tools", return_value=self.tools),
            patch.object(backup, "inspect_cluster", return_value={
                "port": "55432", "serverVersionNum": "180001", "serverVersion": "18.1"
            }),
            patch.object(backup, "database_exists", return_value=True),
            patch.object(backup, "run_checked", side_effect=self.fake_run) as run,
        ):
            with self.assertRaisesRegex(backup.BackupError, "ya existe"):
                backup.restore_backup(bundle, self.config_path, "restore_check", True)
            self.assertFalse(any(Path(call.args[0][0]).name == "createdb" for call in run.call_args_list))

    def test_failed_restore_removes_only_the_new_partial_database(self) -> None:
        bundle = self.root / "restore-failed.rubrova-db-backup"
        self.create_fixture_bundle(bundle)
        calls: list[list[str]] = []

        def failing_restore(command, **kwargs):
            calls.append(command)
            if Path(command[0]).name == "pg_restore" and "--list" not in command:
                raise backup.BackupError("restore simulated failure")
            return self.fake_run(command, **kwargs)

        with (
            patch.object(backup, "find_pg_tools", return_value=self.tools),
            patch.object(backup, "inspect_cluster", return_value={
                "port": "55432", "serverVersionNum": "180001", "serverVersion": "18.1"
            }),
            patch.object(backup, "database_exists", return_value=False),
            patch.object(backup, "run_checked", side_effect=failing_restore),
        ):
            with self.assertRaisesRegex(backup.BackupError, "restore simulated failure"):
                backup.restore_backup(bundle, self.config_path, "restore_check", True)

        self.assertTrue(any(Path(call[0]).name == "createdb" for call in calls))
        self.assertTrue(any(Path(call[0]).name == "dropdb" for call in calls))

    def test_restore_does_not_change_the_active_runtime_configuration(self) -> None:
        bundle = self.root / "restore-ok.rubrova-db-backup"
        self.create_fixture_bundle(bundle)
        calls: list[list[str]] = []

        def successful_restore(command, **kwargs):
            calls.append(command)
            if Path(command[0]).name in ("pg_dump", "pg_restore") and "--version" in command:
                return subprocess.CompletedProcess(command, 0, f"{Path(command[0]).name} (PostgreSQL) 18.1")
            if Path(command[0]).name == "psql":
                sql = command[command.index("-c") + 1]
                if "current_setting('data_directory')" in sql:
                    return subprocess.CompletedProcess(command, 0, f"{self.pg_data}|55432|180001|18.1")
                if "FROM pg_class" in sql:
                    return subprocess.CompletedProcess(command, 0, "4")
            if Path(command[0]).name == "pg_restore" and "--list" in command:
                return subprocess.CompletedProcess(command, 0, "; Archive listing")
            return subprocess.CompletedProcess(command, 0, "")

        with (
            patch.object(backup, "find_pg_tools", return_value=self.tools),
            patch.object(backup, "run_checked", side_effect=successful_restore),
            patch.object(backup, "database_exists", return_value=False),
        ):
            result = backup.restore_backup(bundle, self.config_path, "rubrova_recovery_test", True)

        self.assertEqual(result, "rubrova_recovery_test")
        self.assertEqual(backup.load_native_config(self.config_path)["local_runtime"]["data_directory"], str(self.data_root))
        self.assertTrue(any(Path(call[0]).name == "createdb" for call in calls))
        self.assertTrue(any(Path(call[0]).name == "pg_restore" and "--exit-on-error" in call for call in calls))


if __name__ == "__main__":
    unittest.main(verbosity=2)
