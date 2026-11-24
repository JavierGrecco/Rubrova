#!/usr/bin/env python3
"""Manage Rubrova's execution target without changing or migrating business data.

This utility only stores non-secret preferences. It does not start services.
The future control panel and native/Docker launchers will consume the same file.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


SCHEMA_VERSION = 1
TARGETS = ("native-local", "docker-local", "remote-online")
INTEGRATION_STATES = ("enabled", "paused")
PORT_NAMES = ("postgres", "rmi", "web")


def default_config_path() -> Path:
    override = os.environ.get("RUBROVA_RUNTIME_CONFIG_PATH")
    if override:
        return Path(override).expanduser()

    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    return base / "Rubrova" / "runtime-config.json"


def default_config() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "execution": {
            "target": "native-local",
            "remote_url": None,
            "compose_file": None,
        },
        "connectivity": {
            "external_integrations": "enabled",
        },
        "local_runtime": {
            "data_directory": None,
            "postgres_bin": None,
            "tomcat_home": None,
            "java_home": None,
            "ports": {
                "postgres": 55432,
                "rmi": 7652,
                "web": 8080,
            },
        },
    }


def _is_loopback_host(hostname: str | None) -> bool:
    return hostname in {"localhost", "127.0.0.1", "::1"}


def _validate_remote_url(url: Any, errors: list[str]) -> None:
    if url is None:
        errors.append("remote_url es obligatorio cuando el destino es remote-online.")
        return
    if not isinstance(url, str):
        errors.append("execution.remote_url debe ser texto.")
        return

    parsed = urlsplit(url)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        errors.append("remote_url debe ser una URL absoluta HTTPS.")
        return
    if parsed.username or parsed.password:
        errors.append("No se permiten credenciales dentro de remote_url.")
    if parsed.query or parsed.fragment:
        errors.append("remote_url no puede incluir query string ni fragmento.")
    if parsed.scheme != "https" and not (
        parsed.scheme == "http" and _is_loopback_host(parsed.hostname)
    ):
        errors.append("HTTP sin TLS sólo se admite para localhost durante desarrollo.")


def validate_config(config: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(config, dict):
        return ["La configuración debe ser un objeto JSON."]

    if config.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version debe ser {SCHEMA_VERSION}.")

    expected_root = {"schema_version", "execution", "connectivity", "local_runtime"}
    unknown_root = set(config) - expected_root
    missing_root = expected_root - set(config)
    if unknown_root:
        errors.append(f"Propiedades raíz desconocidas: {', '.join(sorted(unknown_root))}.")
    if missing_root:
        errors.append(f"Faltan propiedades raíz: {', '.join(sorted(missing_root))}.")

    # Runtime credentials must live in the platform's credential store, not this file.
    forbidden_names = re.compile(r"(password|passwd|token|secret|api[_-]?key|private[_-]?key)", re.I)

    def scan_for_secrets(value: Any, prefix: str = "") -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                path = f"{prefix}.{key}" if prefix else key
                if forbidden_names.search(str(key)):
                    errors.append(f"No guardes credenciales ni secretos en runtime-config.json ({path}).")
                scan_for_secrets(item, path)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                scan_for_secrets(item, f"{prefix}[{index}]")

    scan_for_secrets(config)

    execution = config.get("execution")
    if not isinstance(execution, dict):
        errors.append("execution debe ser un objeto.")
    else:
        required = {"target", "remote_url", "compose_file"}
        if set(execution) != required:
            errors.append("execution debe contener únicamente target, remote_url y compose_file.")
        target = execution.get("target")
        if target not in TARGETS:
            errors.append(f"execution.target debe ser uno de: {', '.join(TARGETS)}.")
        if execution.get("remote_url") is not None and not isinstance(execution.get("remote_url"), str):
            errors.append("execution.remote_url debe ser texto o null.")
        if execution.get("compose_file") is not None and not isinstance(execution.get("compose_file"), str):
            errors.append("execution.compose_file debe ser texto o null.")
        if target == "remote-online":
            _validate_remote_url(execution.get("remote_url"), errors)
        elif execution.get("remote_url") is not None:
            _validate_remote_url(execution.get("remote_url"), errors)

    connectivity = config.get("connectivity")
    if not isinstance(connectivity, dict) or set(connectivity) != {"external_integrations"}:
        errors.append("connectivity debe contener únicamente external_integrations.")
    elif connectivity.get("external_integrations") not in INTEGRATION_STATES:
        errors.append("connectivity.external_integrations debe ser enabled o paused.")

    local = config.get("local_runtime")
    if not isinstance(local, dict):
        errors.append("local_runtime debe ser un objeto.")
    else:
        expected_local = {"data_directory", "postgres_bin", "tomcat_home", "java_home", "ports"}
        if set(local) != expected_local:
            errors.append("local_runtime debe contener data_directory, postgres_bin, tomcat_home, java_home y ports.")
        for key in ("data_directory", "postgres_bin", "tomcat_home", "java_home"):
            value = local.get(key)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                errors.append(f"local_runtime.{key} debe ser una ruta no vacía o null.")

        ports = local.get("ports")
        if not isinstance(ports, dict) or set(ports) != set(PORT_NAMES):
            errors.append("local_runtime.ports debe definir postgres, rmi y web.")
        else:
            values: list[int] = []
            for name in PORT_NAMES:
                value = ports.get(name)
                if isinstance(value, bool) or not isinstance(value, int) or not 1024 <= value <= 65535:
                    errors.append(f"El puerto {name} debe ser un entero entre 1024 y 65535.")
                else:
                    values.append(value)
            if len(values) == len(PORT_NAMES) and len(set(values)) != len(values):
                errors.append("Los puertos PostgreSQL, RMI y web deben ser distintos.")

    return errors


def read_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return default_config()
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer la configuración {path}: {exc}") from exc

    errors = validate_config(config)
    if errors:
        raise ValueError("Configuración inválida:\n- " + "\n- ".join(errors))
    return config


def write_config(path: Path, config: dict[str, Any]) -> None:
    errors = validate_config(config)
    if errors:
        raise ValueError("Configuración inválida:\n- " + "\n- ".join(errors))

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=".runtime-config-", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.chmod(temp_path, 0o600)
        except OSError:
            # Windows ACLs are managed by the installer; chmod is best-effort here.
            pass
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def set_target(
    config: dict[str, Any],
    target: str,
    remote_url: str | None = None,
    compose_file: str | None = None,
    acknowledge_data_authority_change: bool = False,
) -> dict[str, Any]:
    if target not in TARGETS:
        raise ValueError(f"Destino no válido: {target}")
    previous = config["execution"]["target"]
    if previous != target and not acknowledge_data_authority_change:
        raise ValueError(
            "Cambiar de destino puede cambiar la base de datos que utiliza Rubrova. "
            "Primero hay que detener, respaldar y migrar/verificar los datos; el selector "
            "no copia ni fusiona bases. Repetí indicando --acknowledge-data-authority-change "
            "sólo después de haber resuelto ese cambio."
        )

    updated = json.loads(json.dumps(config))
    updated["execution"]["target"] = target
    if remote_url is not None:
        updated["execution"]["remote_url"] = remote_url
    if compose_file is not None:
        updated["execution"]["compose_file"] = compose_file

    errors = validate_config(updated)
    if errors:
        raise ValueError("No se puede guardar el destino:\n- " + "\n- ".join(errors))
    return updated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Configuración de ejecución de Rubrova. No inicia servicios ni migra bases de datos."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config_path(),
        help="Ruta de configuración (por defecto, carpeta de datos del usuario).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Crear la configuración inicial si todavía no existe.")
    sub.add_parser("show", help="Mostrar el destino y las opciones actuales.")
    sub.add_parser("validate", help="Validar la configuración sin modificarla.")

    set_target_parser = sub.add_parser("set-target", help="Guardar el destino previsto.")
    set_target_parser.add_argument("target", choices=TARGETS)
    set_target_parser.add_argument("--remote-url")
    set_target_parser.add_argument("--compose-file")
    set_target_parser.add_argument(
        "--acknowledge-data-authority-change",
        action="store_true",
        help="Reconoce que cambiar el destino requiere una migración/validación de datos independiente.",
    )

    integrations = sub.add_parser("set-integrations", help="Habilitar o pausar adaptadores externos.")
    integrations.add_argument("state", choices=INTEGRATION_STATES)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path: Path = args.config.expanduser()

    try:
        if args.command == "init":
            if path.exists():
                print(f"La configuración ya existe: {path}")
                read_config(path)
                return 0
            config = default_config()
            write_config(path, config)
            print(f"Configuración inicial creada: {path}")
            print("Destino predeterminado: native-local (sin Docker).")
            return 0

        config = read_config(path)
        if args.command == "show":
            print(f"Archivo: {path}")
            print(json.dumps(config, ensure_ascii=False, indent=2))
            print("Aviso: guardar un destino no inicia servicios ni migra datos.")
            return 0

        if args.command == "validate":
            print(f"Configuración válida: {path}")
            return 0

        if args.command == "set-target":
            updated = set_target(
                config,
                args.target,
                remote_url=args.remote_url,
                compose_file=args.compose_file,
                acknowledge_data_authority_change=args.acknowledge_data_authority_change,
            )
            write_config(path, updated)
            print(f"Destino guardado: {args.target}")
            print("El cambio no inicia ni detiene servicios y no copia datos.")
            print("Antes de aplicar el nuevo destino: detener Rubrova, crear backup y verificar la base que utilizará.")
            return 0

        if args.command == "set-integrations":
            config["connectivity"]["external_integrations"] = args.state
            write_config(path, config)
            print(f"Integraciones externas: {args.state}")
            print("Esto no cambia el destino local/remoto del POS ni elimina operaciones pendientes.")
            return 0

        parser.error("Comando no reconocido.")
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
