#!/usr/bin/env python3
"""Create, verify and safely restore database-only Rubrova PostgreSQL backups.

The bundle is a portable logical dump of rubrova_dev. It deliberately does not
claim to include attachments, documents, credentials or other filesystem data.
Restore always targets a brand-new database and never overwrites an existing one.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_SCRIPT = SCRIPT_DIR / "runtime-config.py"
SPEC = importlib.util.spec_from_file_location("rubrova_runtime_config_for_backup", CONFIG_SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"No se pudo cargar la configuración de Rubrova: {CONFIG_SCRIPT}")
runtime_config = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime_config)

FORMAT_NAME = "rubrova-native-postgres-backup"
FORMAT_VERSION = 1
DATABASE_NAME = "rubrova_dev"
DUMP_NAME = "database.dump"
MANIFEST_NAME = "manifest.json"
MANIFEST_CHECKSUM_NAME = "manifest.sha256"
EXPECTED_ENTRIES = {DUMP_NAME, MANIFEST_NAME, MANIFEST_CHECKSUM_NAME}
DB_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,62}$")


class BackupError(RuntimeError):
    """An actionable backup/restore failure."""


def user_data_root() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Rubrova"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Rubrova"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "Rubrova"


def load_native_config(config_path: Path) -> dict[str, Any]:
    try:
        config = runtime_config.read_config(config_path.expanduser())
    except (OSError, ValueError) as exc:
        raise BackupError(str(exc)) from exc
    if config["execution"]["target"] != "native-local":
        raise BackupError("El respaldo nativo sólo opera con execution.target=native-local.")
    return config


def native_data_directory(config: dict[str, Any]) -> Path:
    configured = config["local_runtime"].get("data_directory")
    root = Path(configured).expanduser() if configured else user_data_root() / "native-preview"
    return (root / "postgres-data").resolve()


def postgres_candidates(configured: str | None) -> list[Path]:
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured).expanduser())
    env_path = os.environ.get("RUBROVA_POSTGRES_BIN")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    found = shutil.which("pg_dump")
    if found:
        candidates.append(Path(found).resolve().parent)
    if sys.platform == "darwin":
        candidates.extend([
            Path("/Applications/Postgres.app/Contents/Versions/18/bin"),
            Path("/opt/homebrew/opt/postgresql@18/bin"),
            Path("/usr/local/opt/postgresql@18/bin"),
        ])
    elif os.name == "nt":
        candidates.append(Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "PostgreSQL" / "18" / "bin")
    else:
        candidates.extend([Path("/usr/lib/postgresql/18/bin"), Path("/usr/pgsql-18/bin")])

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate.resolve()) if candidate.exists() else str(candidate)
        if key not in seen:
            unique.append(candidate)
            seen.add(key)
    return unique


def find_pg_tools(configured: str | None) -> dict[str, Path]:
    executable_suffix = ".exe" if os.name == "nt" else ""
    names = ("pg_dump", "pg_restore", "psql", "createdb", "dropdb")
    for directory in postgres_candidates(configured):
        tools = {name: directory / f"{name}{executable_suffix}" for name in names}
        if all(path.is_file() for path in tools.values()):
            return {name: path.resolve() for name, path in tools.items()}
    searched = "\n".join(f"  - {path}" for path in postgres_candidates(configured))
    raise BackupError(
        "No se encontraron pg_dump, pg_restore, psql, createdb y dropdb de PostgreSQL 18.\n"
        "Configurá local_runtime.postgres_bin o RUBROVA_POSTGRES_BIN.\n"
        f"Rutas revisadas:\n{searched}"
    )


def run_checked(command: list[str], *, timeout: int = 900) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            env={
                **os.environ,
                "PGCONNECT_TIMEOUT": "5",
                "PGAPPNAME": "RubrovaBackup",
            },
        )
    except FileNotFoundError as exc:
        raise BackupError(f"No se encontró el ejecutable: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise BackupError(f"El comando excedió el límite de {timeout}s: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        output = (exc.stdout or "").strip()
        raise BackupError(
            f"Falló {Path(command[0]).name} (código {exc.returncode}).\n{output[-4000:]}"
        ) from exc


def psql_command(
    tools: dict[str, Path], database: str, port: int, sql: str
) -> list[str]:
    return [
        str(tools["psql"]), "-X", "-v", "ON_ERROR_STOP=1", "-A", "-t",
        "-h", "127.0.0.1", "-p", str(port), "-U", "postgres",
        "-d", database, "-c", sql,
    ]


def inspect_cluster(
    tools: dict[str, Path], config: dict[str, Any], data_directory: Path
) -> dict[str, str]:
    port = config["local_runtime"]["ports"]["postgres"]
    sql = (
        "SELECT current_setting('data_directory') || '|' || "
        "current_setting('port') || '|' || "
        "current_setting('server_version_num') || '|' || "
        "current_setting('server_version')"
    )
    output = run_checked(psql_command(tools, "postgres", port, sql)).stdout.strip()
    fields = output.split("|", 3)
    if len(fields) != 4:
        raise BackupError(f"No se pudo identificar PostgreSQL con seguridad: {output!r}")
    actual_directory, actual_port, version_num, version = fields
    if Path(actual_directory).resolve() != data_directory:
        raise BackupError(
            "El PostgreSQL del puerto configurado no pertenece al directorio privado de Rubrova. "
            "No se realizará ninguna operación."
        )
    if actual_port != str(port):
        raise BackupError(f"El puerto PostgreSQL activo ({actual_port}) no coincide con el configurado ({port}).")
    if not version_num.startswith("18"):
        raise BackupError(f"Se requiere PostgreSQL 18; el servidor activo informa {version}.")
    if not (data_directory / "PG_VERSION").is_file() or (
        data_directory / "PG_VERSION"
    ).read_text(encoding="utf-8").strip() != "18":
        raise BackupError("El directorio de datos no identifica un clúster PostgreSQL 18.")
    return {
        "port": actual_port,
        "serverVersionNum": version_num,
        "serverVersion": version,
    }


def database_exists(tools: dict[str, Path], port: int, database: str) -> bool:
    # database is validated as a conservative SQL identifier before reaching here.
    sql = f"SELECT 1 FROM pg_database WHERE datname = '{database}'"
    return run_checked(psql_command(tools, "postgres", port, sql)).stdout.strip() == "1"


def validate_client_tools(tools: dict[str, Path]) -> None:
    for name in ("pg_dump", "pg_restore"):
        version = run_checked([str(tools[name]), "--version"], timeout=20).stdout
        match = re.search(r"PostgreSQL\)\s+(\d+)", version)
        if not match or int(match.group(1)) != 18:
            raise BackupError(f"Se requiere {name} de PostgreSQL 18; se encontró: {version.strip()}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bundle_entries(archive: zipfile.ZipFile) -> None:
    names = archive.namelist()
    if len(names) != len(EXPECTED_ENTRIES) or set(names) != EXPECTED_ENTRIES:
        raise BackupError(
            "El paquete debe contener únicamente manifest.json, manifest.sha256 y database.dump."
        )
    for info in archive.infolist():
        if info.is_dir() or info.filename.startswith(("/", "\\")) or ".." in Path(info.filename).parts:
            raise BackupError(f"Entrada no permitida en el paquete: {info.filename!r}")


def extract_and_validate_bundle(
    bundle_path: Path, destination: Path, pg_restore: Path
) -> tuple[dict[str, Any], Path]:
    bundle_path = bundle_path.expanduser().resolve()
    if not bundle_path.is_file():
        raise BackupError(f"No existe el paquete de respaldo: {bundle_path}")
    try:
        with zipfile.ZipFile(bundle_path, "r") as archive:
            _bundle_entries(archive)
            bad_entry = archive.testzip()
            if bad_entry:
                raise BackupError(f"El ZIP está dañado en la entrada {bad_entry!r}.")
            manifest_bytes = archive.read(MANIFEST_NAME)
            checksum_text = archive.read(MANIFEST_CHECKSUM_NAME).decode("ascii").strip()
            actual_manifest_checksum = hashlib.sha256(manifest_bytes).hexdigest()
            if checksum_text != actual_manifest_checksum:
                raise BackupError("El checksum SHA-256 del manifiesto no coincide.")
            try:
                manifest = json.loads(manifest_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise BackupError(f"El manifiesto no es JSON UTF-8 válido: {exc}") from exc

            if not isinstance(manifest, dict):
                raise BackupError("El manifiesto debe ser un objeto JSON.")
            if manifest.get("format") != FORMAT_NAME or manifest.get("formatVersion") != FORMAT_VERSION:
                raise BackupError("El formato o la versión del paquete no son compatibles.")
            if manifest.get("scope") != "postgresql-database-only":
                raise BackupError("El alcance declarado por el paquete no es compatible.")
            database = manifest.get("database")
            dump_meta = manifest.get("dump")
            if not isinstance(database, dict) or database.get("name") != DATABASE_NAME:
                raise BackupError("El paquete no contiene la base de datos Rubrova esperada.")
            if not isinstance(dump_meta, dict) or dump_meta.get("file") != DUMP_NAME:
                raise BackupError("Faltan los metadatos del volcado PostgreSQL.")
            expected_size = dump_meta.get("sizeBytes")
            expected_hash = dump_meta.get("sha256")
            if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size <= 0:
                raise BackupError("El tamaño del volcado declarado en el manifiesto no es válido.")
            if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
                raise BackupError("El SHA-256 del volcado declarado en el manifiesto no es válido.")

            dump_path = destination / DUMP_NAME
            digest = hashlib.sha256()
            byte_count = 0
            with archive.open(DUMP_NAME, "r") as source, dump_path.open("xb") as target:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
                    byte_count += len(chunk)
                    target.write(chunk)
            if byte_count != expected_size or digest.hexdigest() != expected_hash:
                raise BackupError("El tamaño o SHA-256 del volcado PostgreSQL no coincide.")
    except (OSError, zipfile.BadZipFile, KeyError, RuntimeError) as exc:
        if isinstance(exc, BackupError):
            raise
        raise BackupError(f"No se pudo leer el paquete de respaldo: {exc}") from exc

    listing = run_checked([str(pg_restore), "--list", str(dump_path)]).stdout.strip()
    if not listing:
        raise BackupError("pg_restore no pudo enumerar el contenido del volcado.")
    return manifest, dump_path


def publish_without_overwrite(temporary: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(temporary, destination)
        return
    except FileExistsError:
        raise BackupError(f"No se sobrescribirá un respaldo existente: {destination}")
    except (AttributeError, OSError):
        pass

    # Portable exclusive-create fallback. A partial file is never reported as a
    # successful backup; a subsequent verify rejects it.
    descriptor: int | None = None
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as target, temporary.open("rb") as source:
            descriptor = None
            shutil.copyfileobj(source, target, length=1024 * 1024)
            target.flush()
            os.fsync(target.fileno())
    except FileExistsError as exc:
        raise BackupError(f"No se sobrescribirá un respaldo existente: {destination}") from exc
    except OSError as exc:
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass
        raise BackupError(f"No se pudo publicar el respaldo: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def create_backup(
    config_path: Path, output_path: Path | None = None, revision: str | None = None
) -> Path:
    config = load_native_config(config_path)
    data_directory = native_data_directory(config)
    tools = find_pg_tools(config["local_runtime"].get("postgres_bin"))
    validate_client_tools(tools)
    cluster = inspect_cluster(tools, config, data_directory)
    port = config["local_runtime"]["ports"]["postgres"]
    if not database_exists(tools, port, DATABASE_NAME):
        raise BackupError(f"No existe la base {DATABASE_NAME}; no hay datos para respaldar.")

    timestamp = datetime.now(timezone.utc)
    if output_path is None:
        filename = f"rubrova-db-{timestamp.strftime('%Y%m%dT%H%M%SZ')}.rubrova-db-backup"
        output_path = user_data_root() / "backups" / filename
    output_path = output_path.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise BackupError(f"No se sobrescribirá un respaldo existente: {output_path}")

    with tempfile.TemporaryDirectory(prefix="rubrova-db-backup-") as temporary_directory:
        work = Path(temporary_directory)
        dump_path = work / DUMP_NAME
        command = [
            str(tools["pg_dump"]), "--format=custom", "--no-acl",
            "--host", "127.0.0.1", "--port", str(port),
            "--username", "postgres", "--dbname", DATABASE_NAME,
            "--file", str(dump_path),
        ]
        run_checked(command, timeout=3600)
        if not dump_path.is_file() or dump_path.stat().st_size <= 0:
            raise BackupError("pg_dump terminó sin generar un archivo de respaldo válido.")

        git_revision = revision or os.environ.get("GITHUB_SHA")
        if git_revision and not re.fullmatch(r"[0-9a-fA-F]{7,40}", git_revision):
            git_revision = None
        manifest = {
            "format": FORMAT_NAME,
            "formatVersion": FORMAT_VERSION,
            "createdAtUtc": timestamp.isoformat().replace("+00:00", "Z"),
            "sourceRevision": git_revision,
            "scope": "postgresql-database-only",
            "database": {
                "name": DATABASE_NAME,
                "host": "127.0.0.1",
                "port": int(cluster["port"]),
                "serverVersion": cluster["serverVersion"],
                "serverVersionNum": int(cluster["serverVersionNum"]),
            },
            "dump": {
                "file": DUMP_NAME,
                "format": "postgresql-custom",
                "sizeBytes": dump_path.stat().st_size,
                "sha256": sha256_file(dump_path),
            },
            "consistency": {
                "method": "pg_dump transactional snapshot",
                "applicationWritesPaused": False,
            },
            "notIncluded": [
                "adjuntos, imágenes y documentos almacenados fuera de PostgreSQL",
                "credenciales, tokens, certificados y secretos",
                "instaladores, binarios y dependencias del runtime",
            ],
        }
        manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        temporary_bundle = output_path.parent / f".{output_path.name}.{os.getpid()}.tmp"
        if temporary_bundle.exists():
            raise BackupError(f"Ya existe un archivo temporal inesperado: {temporary_bundle}")
        try:
            with zipfile.ZipFile(temporary_bundle, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.write(dump_path, DUMP_NAME)
                archive.writestr(MANIFEST_NAME, manifest_bytes)
                archive.writestr(MANIFEST_CHECKSUM_NAME, hashlib.sha256(manifest_bytes).hexdigest() + "\n")
            os.chmod(temporary_bundle, 0o600)
            with tempfile.TemporaryDirectory(prefix="rubrova-db-verify-") as verify_directory:
                extract_and_validate_bundle(temporary_bundle, Path(verify_directory), tools["pg_restore"])
            publish_without_overwrite(temporary_bundle, output_path)
        finally:
            temporary_bundle.unlink(missing_ok=True)

    # Reopen the published path: report success only after the final file verifies.
    with tempfile.TemporaryDirectory(prefix="rubrova-db-final-verify-") as verify_directory:
        extract_and_validate_bundle(output_path, Path(verify_directory), tools["pg_restore"])
    return output_path


def verify_backup(bundle_path: Path, config_path: Path) -> dict[str, Any]:
    config = load_native_config(config_path)
    tools = find_pg_tools(config["local_runtime"].get("postgres_bin"))
    validate_client_tools(tools)
    with tempfile.TemporaryDirectory(prefix="rubrova-db-verify-") as temporary_directory:
        manifest, _ = extract_and_validate_bundle(
            bundle_path, Path(temporary_directory), tools["pg_restore"]
        )
    return manifest


def restore_backup(
    bundle_path: Path,
    config_path: Path,
    target_database: str,
    confirm_new_database: bool,
) -> str:
    if not confirm_new_database:
        raise BackupError(
            "La restauración requiere --confirm-new-database. Sólo se permite crear una base nueva."
        )
    if not DB_NAME_PATTERN.fullmatch(target_database):
        raise BackupError("El nombre de la base destino debe ser un identificador SQL simple.")
    if target_database.lower() in {DATABASE_NAME, "postgres", "template0", "template1"}:
        raise BackupError("La restauración debe usar una base nueva distinta de la base activa.")
    config = load_native_config(config_path)
    data_directory = native_data_directory(config)
    tools = find_pg_tools(config["local_runtime"].get("postgres_bin"))
    validate_client_tools(tools)
    cluster = inspect_cluster(tools, config, data_directory)
    port = config["local_runtime"]["ports"]["postgres"]
    if database_exists(tools, port, target_database):
        raise BackupError(
            f"La base destino {target_database} ya existe. No se sobrescribirá ni se eliminará."
        )

    with tempfile.TemporaryDirectory(prefix="rubrova-db-restore-") as temporary_directory:
        manifest, dump_path = extract_and_validate_bundle(
            bundle_path, Path(temporary_directory), tools["pg_restore"]
        )
        source_port = manifest["database"].get("port")
        source_version = manifest["database"].get("serverVersionNum")
        if not isinstance(source_port, int) or not str(source_version).startswith("18"):
            raise BackupError("El manifiesto no identifica un origen PostgreSQL 18 válido.")

        created = False
        try:
            run_checked([
                str(tools["createdb"]), "--host", "127.0.0.1", "--port", str(port),
                "--username", "postgres", "--template", "template0", target_database,
            ])
            created = True
            run_checked([
                str(tools["pg_restore"]), "--exit-on-error", "--no-owner", "--no-privileges",
                "--host", "127.0.0.1", "--port", str(port), "--username", "postgres",
                "--dbname", target_database, str(dump_path),
            ], timeout=3600)
            count_sql = (
                "SELECT COUNT(*) FROM pg_class c "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE c.relkind IN ('r','p') "
                "AND n.nspname NOT IN ('pg_catalog','information_schema')"
            )
            table_count_text = run_checked(
                psql_command(tools, target_database, port, count_sql)
            ).stdout.strip()
            if not table_count_text.isdigit() or int(table_count_text) <= 0:
                raise BackupError("La base restaurada no contiene tablas de negocio verificables.")
        except Exception as exc:
            if created:
                try:
                    run_checked([
                        str(tools["dropdb"]), "--host", "127.0.0.1", "--port", str(port),
                        "--username", "postgres", target_database,
                    ])
                except Exception as cleanup_exc:
                    raise BackupError(
                        f"La restauración falló ({exc}) y no se pudo retirar la base parcial "
                        f"{target_database} ({cleanup_exc}). No la utilices."
                    ) from exc
            if isinstance(exc, BackupError):
                raise
            raise BackupError(f"La restauración no se completó: {exc}") from exc

    return target_database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Respaldos lógicos PostgreSQL de Rubrova (no incluye archivos externos)."
    )
    parser.add_argument("--config", type=Path, default=runtime_config.default_config_path())
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Crear y verificar un paquete de base de datos.")
    create.add_argument("--output", type=Path, help="Ruta del paquete .rubrova-db-backup.")
    create.add_argument("--revision", help="SHA de Git para registrar en el manifiesto.")

    verify = sub.add_parser("verify", help="Verificar estructura, checksums y legibilidad pg_restore.")
    verify.add_argument("bundle", type=Path)

    restore = sub.add_parser("restore", help="Restaurar en una base nueva sin sobrescribir datos.")
    restore.add_argument("bundle", type=Path)
    restore.add_argument("--target-database", required=True)
    restore.add_argument("--confirm-new-database", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            output = create_backup(args.config, args.output, args.revision)
            print(f"RUBROVA_DB_BACKUP_CREATED={output}")
            print("RUBROVA_DB_BACKUP_SCOPE=postgresql-database-only")
            print(f"RUBROVA_DB_BACKUP_SHA256={sha256_file(output)}")
        elif args.command == "verify":
            manifest = verify_backup(args.bundle, args.config)
            print("RUBROVA_DB_BACKUP_VERIFIED=true")
            print(f"RUBROVA_DB_BACKUP_CREATED_AT={manifest['createdAtUtc']}")
            print(f"RUBROVA_DB_BACKUP_DATABASE={manifest['database']['name']}")
        else:
            database = restore_backup(
                args.bundle, args.config, args.target_database, args.confirm_new_database
            )
            print(f"RUBROVA_DB_RESTORE_VERIFIED={database}")
            print("La configuración activa de Rubrova no fue modificada.")
    except (BackupError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
