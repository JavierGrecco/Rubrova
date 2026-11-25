#!/usr/bin/env python3
"""Run the compiled Rubrova/lsFusion stack directly on the host, without Docker.

This is a development preview. It uses an isolated PostgreSQL cluster under the
user's Rubrova data directory and keeps that data when the processes stop.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


TOMCAT_VERSION = "9.0.124"
TOMCAT_BASE_URL = f"https://downloads.apache.org/tomcat/tomcat-9/v{TOMCAT_VERSION}/bin"
TOMCAT_TAR_SHA512 = "925e4fefe25b2ecccd032acd0b4cb1b506455037ed0f8b0e51824bed839c5e92bf5e58982b990d2fdcbc790bcda1a533db7faffb325f8a7baee939fc8ae871c1"
TOMCAT_WINDOWS_ZIP_SHA512 = "d7d37e9e2da57cd5ce70cba2d5ea620d5703862dc6265391925d859d209451bcec9e9cfb294bef363bb940a545d6317b268075075c0fac6e7253a98468c609fc"
STARTUP_TIMEOUT_SECONDS = 900
WEB_TIMEOUT_SECONDS = 300

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
CONFIG_SCRIPT = SCRIPT_DIR / "runtime-config.py"

SPEC = importlib.util.spec_from_file_location("rubrova_runtime_config", CONFIG_SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"No se pudo cargar el gestor de configuración: {CONFIG_SCRIPT}")
runtime_config = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime_config)


class RuntimeErrorRubrova(RuntimeError):
    pass


def user_data_root() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Rubrova"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Rubrova"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "Rubrova"


def dependency_cache_root() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "Rubrova" / "runtime-deps"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Rubrova" / "runtime-deps"
    return Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "Rubrova" / "runtime-deps"


def load_config(path: Path) -> dict[str, Any]:
    return runtime_config.read_config(path)


def run_checked(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **kwargs,
        )
    except FileNotFoundError as exc:
        raise RuntimeErrorRubrova(f"No se encontró el ejecutable: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        output = (exc.stdout or "").strip()
        raise RuntimeErrorRubrova(
            f"Falló el comando ({exc.returncode}): {' '.join(command)}\n{output[-5000:]}"
        ) from exc


def find_java(java_home: str | None) -> Path:
    candidates: list[Path] = []
    if java_home:
        candidates.append(Path(java_home).expanduser() / "bin" / ("java.exe" if os.name == "nt" else "java"))
    env_java_home = os.environ.get("JAVA_HOME")
    if env_java_home:
        candidates.append(Path(env_java_home) / "bin" / ("java.exe" if os.name == "nt" else "java"))
    found = shutil.which("java")
    if found:
        candidates.append(Path(found))

    for candidate in candidates:
        if candidate.is_file():
            result = run_checked([str(candidate), "-version"])
            output = result.stdout or ""
            match = re.search(r'version "(?:1\.)?(\d+)', output)
            if not match or int(match.group(1)) != 21:
                raise RuntimeErrorRubrova(
                    f"Rubrova usa Java 21. Se encontró una versión incompatible en {candidate}:\n{output.strip()}"
                )
            return candidate.resolve()
    raise RuntimeErrorRubrova(
        "No se encontró Java 21. Configurá JAVA_HOME o local_runtime.java_home en runtime-config.json."
    )


def postgres_candidates(configured: str | None) -> list[Path]:
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured).expanduser())
    env_path = os.environ.get("RUBROVA_POSTGRES_BIN")
    if env_path:
        candidates.append(Path(env_path).expanduser())

    pg_ctl_path = shutil.which("pg_ctl")
    if pg_ctl_path:
        candidates.append(Path(pg_ctl_path).resolve().parent)

    if sys.platform == "darwin":
        candidates.extend(
            [
                Path("/Applications/Postgres.app/Contents/Versions/18/bin"),
                Path("/opt/homebrew/opt/postgresql@18/bin"),
                Path("/usr/local/opt/postgresql@18/bin"),
            ]
        )
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


def find_postgres_bin(configured: str | None) -> Path:
    names = ["initdb", "pg_ctl", "pg_isready", "createdb", "psql"]
    if os.name == "nt":
        names = [name + ".exe" for name in names]
    for directory in postgres_candidates(configured):
        if all((directory / name).is_file() for name in names):
            version = run_checked([str(directory / ("pg_ctl.exe" if os.name == "nt" else "pg_ctl")), "--version"]).stdout
            match = re.search(r"PostgreSQL\)\s+(\d+)", version)
            if not match or int(match.group(1)) != 18:
                raise RuntimeErrorRubrova(
                    f"Se necesita PostgreSQL 18. Se encontró:\n{version.strip()}\nRuta: {directory}"
                )
            return directory.resolve()
    searched = "\n".join(f"  - {path}" for path in postgres_candidates(configured))
    raise RuntimeErrorRubrova(
        "No se encontraron las herramientas de PostgreSQL 18 (initdb, pg_ctl, pg_isready, createdb y psql).\n"
        "En macOS instalá PostgreSQL 18 con Postgres.app o Homebrew; luego volvé a abrir la terminal.\n"
        "También podés indicar el directorio bin mediante RUBROVA_POSTGRES_BIN o local_runtime.postgres_bin.\n"
        f"Rutas revisadas:\n{searched}"
    )


def safe_extract_tar(archive: Path, destination: Path) -> None:
    root = destination.resolve()
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            target = (root / member.name).resolve()
            if target != root and root not in target.parents:
                raise RuntimeErrorRubrova(f"El archivo Tomcat contiene una ruta no segura: {member.name}")
        tar.extractall(destination)


def safe_extract_zip(archive: Path, destination: Path) -> None:
    root = destination.resolve()
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            target = (root / member.filename).resolve()
            if target != root and root not in target.parents:
                raise RuntimeErrorRubrova(f"El ZIP Tomcat contiene una ruta no segura: {member.filename}")
        bundle.extractall(destination)


def validate_tomcat_home(candidate: Path) -> Path:
    executable = "catalina.bat" if os.name == "nt" else "catalina.sh"
    manifest_path = candidate / "lib" / "catalina.jar"
    if not (candidate / "bin" / executable).is_file() or not manifest_path.is_file():
        raise RuntimeErrorRubrova(f"El directorio configurado no contiene una instalación Tomcat válida: {candidate}")
    try:
        with zipfile.ZipFile(manifest_path) as archive:
            manifest = archive.read("META-INF/MANIFEST.MF").decode("utf-8", errors="replace")
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise RuntimeErrorRubrova(f"No se pudo leer la versión de Tomcat en {manifest_path}: {exc}") from exc
    match = re.search(r"(?mi)^Implementation-Version:\s*([^\r\n]+)", manifest)
    version = match.group(1).strip() if match else ""
    if version != TOMCAT_VERSION:
        raise RuntimeErrorRubrova(
            f"Rubrova requiere Apache Tomcat {TOMCAT_VERSION}; se encontró {version or 'versión desconocida'} en {candidate}."
        )
    return candidate.resolve()


def download_tomcat(
    cache_root: Path,
    allow_download: bool,
    configured_home: str | None = None,
) -> Path:
    target = cache_root / f"apache-tomcat-{TOMCAT_VERSION}"
    executable = "catalina.bat" if os.name == "nt" else "catalina.sh"
    candidates = [
        Path(configured_home).expanduser() if configured_home else None,
        Path(os.environ.get("RUBROVA_TOMCAT_HOME", "")).expanduser()
        if os.environ.get("RUBROVA_TOMCAT_HOME")
        else None,
        target,
    ]
    for candidate in candidates:
        if candidate and (candidate / "bin" / executable).is_file():
            return validate_tomcat_home(candidate)

    if not allow_download:
        raise RuntimeErrorRubrova(
            f"No se encontró Tomcat 9. Configurá RUBROVA_TOMCAT_HOME o habilitá la descarga inicial verificada."
        )

    cache_root.mkdir(parents=True, exist_ok=True)
    is_windows = os.name == "nt"
    archive_name = (
        f"apache-tomcat-{TOMCAT_VERSION}-windows-x64.zip"
        if is_windows
        else f"apache-tomcat-{TOMCAT_VERSION}.tar.gz"
    )
    url = f"{TOMCAT_BASE_URL}/{archive_name}"
    expected = TOMCAT_WINDOWS_ZIP_SHA512 if is_windows else TOMCAT_TAR_SHA512
    archive = cache_root / archive_name
    temporary = archive.with_suffix(archive.suffix + ".download")

    print(f"Descargando Tomcat {TOMCAT_VERSION} desde el servidor oficial de Apache...")
    try:
        digest = hashlib.sha512()
        with urllib.request.urlopen(url, timeout=45) as response, temporary.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
                output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        if digest.hexdigest() != expected:
            raise RuntimeErrorRubrova(
                f"SHA-512 de Tomcat incorrecto. Esperado {expected}, recibido {digest.hexdigest()}."
            )
        os.replace(temporary, archive)
    except (OSError, urllib.error.URLError) as exc:
        temporary.unlink(missing_ok=True)
        raise RuntimeErrorRubrova(
            "No se pudo obtener Tomcat. La primera preparación necesita conexión; "
            "una vez descargado y verificado, el runtime puede iniciarse sin Internet."
        ) from exc
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    extraction_root = cache_root / f".extract-{TOMCAT_VERSION}"
    shutil.rmtree(extraction_root, ignore_errors=True)
    extraction_root.mkdir(parents=True)
    if is_windows:
        safe_extract_zip(archive, extraction_root)
    else:
        safe_extract_tar(archive, extraction_root)

    extracted = extraction_root / f"apache-tomcat-{TOMCAT_VERSION}"
    if not (extracted / "bin" / executable).is_file():
        raise RuntimeErrorRubrova("El archivo oficial no contiene la estructura Tomcat esperada.")
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(extracted), str(target))
    shutil.rmtree(extraction_root, ignore_errors=True)
    return validate_tomcat_home(target)


def check_artifacts() -> dict[str, Path]:
    build_artifacts = os.environ.get("RUBROVA_BUILD_ARTIFACTS_DIR")
    if build_artifacts:
        artifact_dir = Path(build_artifacts).expanduser()
        artifacts = {
            "server": artifact_dir / "server.jar",
            "logic": artifact_dir / "logics.jar",
            "client": artifact_dir / "client.war",
        }
    else:
        artifacts = {
            "server": REPO_ROOT / "vendor/platform/server/target/lsfusion-server-6.2.jar",
            "logic": REPO_ROOT / "vendor/mycompany/target/lsfusion-server-6.2.jar",
            "client": REPO_ROOT / "vendor/platform/web-client/target/lsfusion-client-6.2.war",
        }
    missing = [str(path) for path in artifacts.values() if not path.is_file() or path.stat().st_size == 0]
    if missing:
        raise RuntimeErrorRubrova(
            "Faltan artefactos compilados desde las fuentes de Rubrova:\n- "
            + "\n- ".join(missing)
            + "\nGenerá una vez los artefactos con:\n"
            + "  mvn -B -ntp -f build/rubrova/pom.xml -Passemble -DskipTests package\n"
            + "  mvn -B -ntp -f vendor/platform/pom.xml -pl server,web-client -am -DskipTests package"
        )
    return artifacts


def ensure_extension_files(logics_dir: Path) -> None:
    module_names = [
        "RubrovaCustom.lsf",
        "RubrovaPOSLocalization.lsf",
        "RubrovaIntegrationResilience.lsf",
        "MyCompanyResourceBundle_es_AR.properties",
    ]
    for name in module_names:
        source = REPO_ROOT / "extensions" / "lsfusion" / name
        if not source.is_file():
            raise RuntimeErrorRubrova(f"Falta el módulo requerido: {source}")
        shutil.copy2(source, logics_dir / name)

    conf = logics_dir / "conf"
    conf.mkdir(parents=True, exist_ok=True)
    (conf / "settings.properties").write_text(
        "logics.topModule = RubrovaCustom\n"
        "user.setLanguage = es\n"
        "user.setCountry = AR\n",
        encoding="utf-8",
    )


def prepare_tomcat_base(tomcat_home: Path, base: Path, war: Path, ports: dict[str, int]) -> None:
    base.mkdir(parents=True, exist_ok=True)
    if not (base / "conf" / "server.xml").is_file():
        shutil.copytree(tomcat_home / "conf", base / "conf", dirs_exist_ok=True)

    for name in ("webapps", "logs", "temp", "work"):
        (base / name).mkdir(parents=True, exist_ok=True)
    webapp = base / "webapps" / "ROOT"

    war_digest = hashlib.sha256(war.read_bytes()).hexdigest()
    marker = base / ".rubrova-client.sha256"
    if marker.exists() and marker.read_text(encoding="utf-8").strip() == war_digest and (webapp / "WEB-INF" / "web.xml").is_file():
        pass
    else:
        shutil.rmtree(webapp, ignore_errors=True)
        webapp.mkdir(parents=True)
        with zipfile.ZipFile(war) as bundle:
            for member in bundle.infolist():
                destination = (webapp / member.filename).resolve()
                root = webapp.resolve()
                if destination != root and root not in destination.parents:
                    raise RuntimeErrorRubrova(f"El WAR contiene una ruta no segura: {member.filename}")
            bundle.extractall(webapp)
        marker.write_text(war_digest + "\n", encoding="utf-8")

    web_xml = webapp / "WEB-INF" / "web.xml"
    tree = ET.parse(web_xml)
    root = tree.getroot()
    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag.split("}", 1)[0] + "}"
    params = {}
    for item in root.findall(f"{namespace}context-param"):
        name = item.find(f"{namespace}param-name")
        value = item.find(f"{namespace}param-value")
        if name is not None and value is not None:
            params[name.text or ""] = value
    missing_params = {"host", "port"} - set(params)
    if missing_params:
        raise RuntimeErrorRubrova(
            "El cliente web no declara los parámetros RMI requeridos: "
            + ", ".join(sorted(missing_params))
        )
    params["host"].text = "127.0.0.1"
    params["port"].text = str(ports["rmi"])
    tree.write(web_xml, encoding="UTF-8", xml_declaration=True)

    server_xml = base / "conf" / "server.xml"
    server_tree = ET.parse(server_xml)
    server_root = server_tree.getroot()
    connectors = server_root.findall(".//Connector")
    http_connector = next(
        (connector for connector in connectors if connector.get("port") in {"8080", str(ports["web"])}),
        None,
    )
    if http_connector is None:
        raise RuntimeErrorRubrova("No se encontró el conector HTTP de Tomcat en server.xml.")
    http_connector.set("port", str(ports["web"]))
    http_connector.set("address", "127.0.0.1")
    server_tree.write(server_xml, encoding="UTF-8", xml_declaration=True)


def tail_file(path: Path, lines: int = 50) -> str:
    if not path.is_file():
        return "(todavía no se creó el archivo de log)"
    content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(content[-lines:])


def port_is_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def wait_for_port(host: str, port: int, timeout: int, process: subprocess.Popen[Any] | None = None) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            raise RuntimeErrorRubrova(f"El proceso terminó antes de abrir {host}:{port} (código {process.returncode}).")
        if port_is_open(host, port):
            return
        time.sleep(1)
    raise RuntimeErrorRubrova(f"El servicio no abrió {host}:{port} dentro de {timeout} segundos.")


def wait_for_server_ready(
    process: subprocess.Popen[Any],
    log_dir: Path,
    rmi_port: int,
    timeout: int = STARTUP_TIMEOUT_SECONDS,
) -> None:
    # Wait for application bootstrap, the configured RMI port, and the onStarted action.
    # The port can open before MyCompany has completed initialization.
    candidates = [log_dir / "start.log", log_dir / "stdout.log", log_dir / "stderr.log"]
    started = False
    onstarted = False
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            logs = "\n\n".join(f"--- {path} ---\n{tail_file(path, 80)}" for path in candidates)
            raise RuntimeErrorRubrova(
                f"El servidor Rubrova terminó durante el arranque (código {process.returncode}).\n{logs}"
            )
        snapshots = [
            path.read_text(encoding="utf-8", errors="replace")
            for path in candidates
            if path.is_file()
        ]
        combined = "\n".join(snapshots)
        started = started or "Server has successfully started in" in combined
        onstarted = onstarted or "Executing onStarted action finished" in combined
        rmi_ready = port_is_open("127.0.0.1", rmi_port)
        if started and rmi_ready and onstarted:
            return
        time.sleep(2)
    logs = "\n\n".join(f"--- {path} ---\n{tail_file(path, 80)}" for path in candidates)
    raise RuntimeErrorRubrova(
        "El servidor no completó toda la inicialización (inicio, RMI y onStarted) "
        f"dentro de {timeout} segundos.\n{logs}"
    )


def tomcat_startup_diagnostics(tomcat_base: Path | None, last_http_body: str = "") -> str:
    if tomcat_base is None:
        return ""

    details = ["Diagnóstico del despliegue web de Tomcat:"]
    webapp = tomcat_base / "webapps" / "ROOT"
    web_xml = webapp / "WEB-INF" / "web.xml"
    details.append(f"Directorio ROOT presente: {webapp.is_dir()}.")
    details.append(f"Descriptor ROOT/WEB-INF/web.xml presente: {web_xml.is_file()}.")

    if web_xml.is_file():
        try:
            root = ET.parse(web_xml).getroot()
            namespace = root.tag.split("}", 1)[0] + "}" if root.tag.startswith("{") else ""
            welcome = root.find(f"{namespace}welcome-file-list/{namespace}welcome-file")
            details.append(f"Página de bienvenida configurada: {(welcome.text or '').strip() if welcome is not None else 'no declarada'}.")
        except (ET.ParseError, OSError) as exc:
            details.append(f"No se pudo leer web.xml: {exc}.")

    server_xml = tomcat_base / "conf" / "server.xml"
    if server_xml.is_file():
        try:
            server_root = ET.parse(server_xml).getroot()
            for host in server_root.findall(".//Host"):
                details.append(
                    "Tomcat Host: "
                    f"name={host.get('name', '')}, appBase={host.get('appBase', '')}, "
                    f"unpackWARs={host.get('unpackWARs', '')}, autoDeploy={host.get('autoDeploy', '')}."
                )
            for connector in server_root.findall(".//Connector"):
                details.append(
                    f"Tomcat Connector: port={connector.get('port', '')}, address={connector.get('address', '')}."
                )
        except (ET.ParseError, OSError) as exc:
            details.append(f"No se pudo leer server.xml: {exc}.")

    if last_http_body.strip():
        body = re.sub(
            r"(?i)((?:password|passwd|secret|token|api[_-]?key)\s*[=:]\s*)[^\s,;]+",
            r"\1[redactado]",
            last_http_body.strip(),
        )
        details.append(f"Respuesta HTTP (primeros 1200 caracteres): {body[:1200]}")

    logs_dir = tomcat_base / "logs"
    log_files = sorted(
        (
            path for path in logs_dir.iterdir()
            if path.is_file() and (path.suffix.lower() == ".log" or path.name.endswith(".txt"))
        ),
        key=lambda path: (0 if path.name == "rubrova-console.log" else 1, path.name),
    ) if logs_dir.is_dir() else []
    if not log_files:
        details.append(f"Tomcat todavía no generó archivos de log en {logs_dir}.")
    for path in log_files[-8:]:
        content = tail_file(path, 100)
        content = re.sub(
            r"(?i)((?:password|passwd|secret|token|api[_-]?key)\s*[=:]\s*)[^\s,;]+",
            r"\1[redactado]",
            content,
        )
        details.append(f"--- {path.name} (últimas 100 líneas) ---\n{content}")

    return "\n".join(details)


def wait_for_web(
    url: str,
    process: subprocess.Popen[Any],
    tomcat_base: Path | None = None,
    timeout: int = WEB_TIMEOUT_SECONDS,
    not_found_grace_seconds: int = 60,
) -> None:
    deadline = time.monotonic() + timeout
    last_error = "sin respuesta HTTP"
    last_http_body = ""
    not_found_since: float | None = None

    def fail(message: str) -> RuntimeErrorRubrova:
        diagnostics = tomcat_startup_diagnostics(tomcat_base, last_http_body)
        if diagnostics:
            message = f"{message}\n{diagnostics}"
        return RuntimeErrorRubrova(message)

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise fail(f"Tomcat terminó durante el arranque (código {process.returncode}).")
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if 200 <= response.status < 400:
                    return
                last_error = f"HTTP {response.status}"
                not_found_since = None
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            try:
                last_http_body = exc.read(2048).decode("utf-8", errors="replace")
            except OSError:
                last_http_body = ""
            if exc.code == 404:
                if not_found_since is None:
                    not_found_since = time.monotonic()
            else:
                not_found_since = None
        except (OSError, urllib.error.URLError) as exc:
            last_error = str(exc)
            not_found_since = None

        if not_found_since is not None:
            missing_for = time.monotonic() - not_found_since
            if missing_for >= not_found_grace_seconds:
                raise fail(
                    "Tomcat abrió el puerto HTTP, pero mantuvo HTTP 404 en el cliente "
                    f"durante {int(missing_for)} segundos. El contexto ROOT no quedó disponible."
                )
        time.sleep(2)

    raise fail(f"El cliente web no respondió correctamente en {timeout} segundos: {last_error}")


def stop_process(process: subprocess.Popen[Any] | None, name: str, timeout: int = 30) -> None:
    if process is None or process.poll() is not None:
        return
    print(f"Deteniendo {name}...")
    if os.name == "nt":
        # catalina.bat launches java.exe as a child. Terminate the full tree,
        # otherwise an orphan Tomcat JVM can keep the ports occupied.
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        return
    try:
        process.terminate()
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def postgres_cluster_is_running(pg_ctl: Path, data_dir: Path) -> bool:
    if not (data_dir / "PG_VERSION").is_file():
        return False
    result = subprocess.run(
        [str(pg_ctl), "-D", str(data_dir), "status"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode == 0


def stop_postgres(pg_bin: Path, data_dir: Path, started_by_this_process: bool) -> None:
    # Never stop a developer's pre-existing PostgreSQL service.
    if not started_by_this_process or not data_dir.exists() or not (data_dir / "PG_VERSION").is_file():
        return
    pg_ctl = pg_bin / ("pg_ctl.exe" if os.name == "nt" else "pg_ctl")
    result = subprocess.run(
        [str(pg_ctl), "-D", str(data_dir), "-m", "fast", "-w", "stop"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0 and "no server running" not in (result.stdout or "").lower():
        print(f"Advertencia al detener PostgreSQL:\n{result.stdout}", file=sys.stderr)


def ensure_database(pg_bin: Path, data_dir: Path, port: int, log_dir: Path) -> bool:
    """Start only Rubrova's private cluster; return whether this call started it."""
    initdb = pg_bin / ("initdb.exe" if os.name == "nt" else "initdb")
    pg_ctl = pg_bin / ("pg_ctl.exe" if os.name == "nt" else "pg_ctl")
    pg_isready = pg_bin / ("pg_isready.exe" if os.name == "nt" else "pg_isready")
    psql = pg_bin / ("psql.exe" if os.name == "nt" else "psql")
    createdb = pg_bin / ("createdb.exe" if os.name == "nt" else "createdb")
    logfile = log_dir / "postgres.log"
    data_dir.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    if not (data_dir / "PG_VERSION").is_file():
        if data_dir.exists() and any(data_dir.iterdir()):
            raise RuntimeErrorRubrova(
                f"El directorio de PostgreSQL no está vacío pero no contiene PG_VERSION. "
                f"No se modificará: {data_dir}"
            )
        data_dir.mkdir(parents=True, exist_ok=True)
        run_checked(
            [
                str(initdb),
                "-D", str(data_dir),
                "-U", "postgres",
                "--encoding=UTF8",
                "--auth-local=trust",
                "--auth-host=trust",
            ]
        )
        # Development-only cluster: TCP is bound to loopback, never exposed to the LAN.
        # The production installer must use SCRAM and the OS credential store.
        with (data_dir / "postgresql.conf").open("a", encoding="utf-8") as conf:
            conf.write("\nlisten_addresses = '127.0.0.1'\n")
            conf.write(f"port = {port}\n")
            conf.write("max_connections = 100\n")
            # The private cluster uses TCP loopback only and does not depend on
            # a system-wide Unix socket directory owned by another service.
            conf.write("unix_socket_directories = ''\n")
        with (data_dir / "pg_hba.conf").open("a", encoding="utf-8") as hba:
            hba.write("\nhost all all 127.0.0.1/32 trust\n")
            hba.write("host all all ::1/128 trust\n")

    version = (data_dir / "PG_VERSION").read_text(encoding="utf-8").strip()
    if version != "18":
        raise RuntimeErrorRubrova(
            f"El directorio local de Rubrova usa PostgreSQL {version}; se requiere PostgreSQL 18. "
            "No se ejecutará una migración automática."
        )

    started_here = False
    try:
        if postgres_cluster_is_running(pg_ctl, data_dir):
            # A listening PostgreSQL process is accepted only if it belongs to this exact data dir.
            identity = run_checked(
                [
                    str(psql), "-X", "-h", "127.0.0.1", "-p", str(port),
                    "-U", "postgres", "-d", "postgres", "-At",
                    "-c", "SHOW data_directory",
                ]
            ).stdout.strip()
            if Path(identity).resolve() != data_dir.resolve():
                raise RuntimeErrorRubrova(
                    f"El puerto {port} responde, pero PostgreSQL no pertenece al directorio privado de Rubrova. "
                    "No se utilizará ni detendrá esa instancia."
                )
        else:
            if port_is_open("127.0.0.1", port):
                raise RuntimeErrorRubrova(
                    f"El puerto PostgreSQL {port} ya está ocupado por otra instancia. "
                    "No se conectará a una base de datos ajena."
                )
            run_checked(
                [
                    str(pg_ctl),
                    "-D", str(data_dir),
                    "-l", str(logfile),
                    "-o", f"-p {port} -h 127.0.0.1",
                    "-w", "-t", "90", "start",
                ]
            )
            started_here = True

        wait_for_port("127.0.0.1", port, 60)
        run_checked([str(pg_isready), "-h", "127.0.0.1", "-p", str(port), "-U", "postgres", "-t", "5"])
        identity = run_checked(
            [
                str(psql), "-X", "-h", "127.0.0.1", "-p", str(port),
                "-U", "postgres", "-d", "postgres", "-At",
                "-c", "SELECT current_setting('data_directory') || '|' || current_setting('port') || '|' || current_setting('server_version_num')",
            ]
        ).stdout.strip()
        try:
            actual_dir, actual_port, actual_version = identity.split("|", 2)
        except ValueError as exc:
            raise RuntimeErrorRubrova(f"No se pudo identificar la instancia PostgreSQL local: {identity!r}") from exc
        if (
            Path(actual_dir).resolve() != data_dir.resolve()
            or int(actual_port) != port
            or not actual_version.startswith("18")
        ):
            raise RuntimeErrorRubrova(
                "La instancia PostgreSQL no coincide con el directorio, puerto y versión configurados para Rubrova."
            )

        query = run_checked(
            [
                str(psql), "-X", "-h", "127.0.0.1", "-p", str(port),
                "-U", "postgres", "-d", "postgres", "-tAc",
                "SELECT 1 FROM pg_database WHERE datname = 'rubrova_dev'",
            ]
        ).stdout.strip()
        if query != "1":
            run_checked(
                [
                    str(createdb), "-h", "127.0.0.1", "-p", str(port),
                    "-U", "postgres", "rubrova_dev",
                ]
            )
        return started_here
    except Exception:
        # Do not leave a half-started cluster behind when initialization fails.
        stop_postgres(pg_bin, data_dir, started_here)
        raise


def run_preview(config_path: Path, open_browser: bool, allow_tomcat_download: bool) -> None:
    config = load_config(config_path)
    if config["execution"]["target"] != "native-local":
        raise RuntimeErrorRubrova(
            "El destino guardado no es native-local. Cambialo con runtime-config.py antes de iniciar esta vista previa."
        )

    local = config["local_runtime"]
    ports = local["ports"]
    artifacts = check_artifacts()
    java = find_java(local.get("java_home"))
    pg_bin = find_postgres_bin(local.get("postgres_bin"))
    tomcat_home = download_tomcat(
        dependency_cache_root(),
        allow_download=allow_tomcat_download,
        configured_home=local.get("tomcat_home"),
    )

    data_root = Path(local["data_directory"]).expanduser() if local.get("data_directory") else user_data_root() / "native-preview"
    pg_data = data_root / "postgres-data"
    runtime_dir = data_root / "runtime"
    server_parent = runtime_dir
    logics_dir = runtime_dir / "lsfusion"
    tomcat_base = runtime_dir / "tomcat-base"
    log_dir = data_root / "logs"
    for directory in (server_parent, logics_dir, log_dir):
        directory.mkdir(parents=True, exist_ok=True)

    wait_for_port("127.0.0.1", ports["postgres"], 1) if port_is_open("127.0.0.1", ports["postgres"]) else None
    if port_is_open("127.0.0.1", ports["postgres"]) and not (pg_data / "PG_VERSION").is_file():
        raise RuntimeErrorRubrova(
            f"El puerto {ports['postgres']} ya está ocupado por otro servicio. "
            "No se conectará a una base de datos ajena."
        )

    server_jar = server_parent / "server.jar"
    logic_jar = logics_dir / "mycompany.jar"
    shutil.copy2(artifacts["server"], server_jar)
    shutil.copy2(artifacts["logic"], logic_jar)
    ensure_extension_files(logics_dir)
    prepare_tomcat_base(tomcat_home, tomcat_base, artifacts["client"], ports)

    if port_is_open("127.0.0.1", ports["rmi"]):
        raise RuntimeErrorRubrova(
            f"El puerto RMI {ports['rmi']} ya está ocupado. Detené el otro servidor antes de iniciar esta instancia."
        )
    if port_is_open("127.0.0.1", ports["web"]):
        raise RuntimeErrorRubrova(
            f"El puerto web {ports['web']} ya está ocupado. Detené el otro servidor antes de iniciar esta instancia."
        )

    classpath = os.pathsep.join([".", "./*", "../server.jar"])
    server_log = log_dir / "server-console.log"
    server_stream = server_log.open("ab")
    server_command = [
        str(java),
        "-Xms512m",
        "-Xmx2048m",
        "-Djava.rmi.server.hostname=127.0.0.1",
        "-Dlsfusion.rmi.bindAddress=127.0.0.1",
        f"-Ddb.server=127.0.0.1:{ports['postgres']}",
        "-Ddb.name=rubrova_dev",
        "-Ddb.user=postgres",
        "-Ddb.password=",
        f"-Drmi.port={ports['rmi']}",
        "-Dlogics.topModule=RubrovaCustom",
        "-Duser.setLanguage=es",
        "-Duser.setCountry=AR",
        "-cp",
        classpath,
        "lsfusion.server.logics.BusinessLogicsBootstrap",
    ]

    server_process: subprocess.Popen[Any] | None = None
    tomcat_process: subprocess.Popen[Any] | None = None
    tomcat_stream = None
    postgres_started_here = False
    try:
        postgres_started_here = ensure_database(pg_bin, pg_data, ports["postgres"], log_dir)
        print("PostgreSQL local listo.")
        print("Iniciando servidor Rubrova nativo (sin Docker)...")
        server_process = subprocess.Popen(
            server_command,
            cwd=logics_dir,
            stdout=server_stream,
            stderr=subprocess.STDOUT,
            env={**os.environ, "JAVA_HOME": str(java.parents[1])},
            creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS) if os.name == "nt" else 0,
            start_new_session=(os.name != "nt"),
        )
        wait_for_server_ready(server_process, logics_dir / "logs", ports["rmi"])
        print("Servidor Rubrova y PostgreSQL están listos.")

        env = {
            **os.environ,
            "JAVA_HOME": str(java.parents[1]),
            "CATALINA_HOME": str(tomcat_home),
            "CATALINA_BASE": str(tomcat_base),
            "CATALINA_TMPDIR": str(tomcat_base / "temp"),
        }
        if os.name == "nt":
            catalina = tomcat_home / "bin" / "catalina.bat"
            tomcat_command = ["cmd.exe", "/d", "/s", "/c", f'"{catalina}" run']
        else:
            catalina = tomcat_home / "bin" / "catalina.sh"
            catalina.chmod(catalina.stat().st_mode | 0o111)
            tomcat_command = [str(catalina), "run"]

        tomcat_stream = (tomcat_base / "logs" / "rubrova-console.log").open("ab")
        print("Iniciando cliente web Tomcat...")
        tomcat_process = subprocess.Popen(
            tomcat_command,
            cwd=tomcat_home / "bin",
            stdout=tomcat_stream,
            stderr=subprocess.STDOUT,
            env=env,
            creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS) if os.name == "nt" else 0,
            start_new_session=(os.name != "nt"),
        )

        web_url = f"http://127.0.0.1:{ports['web']}/login"
        wait_for_web(web_url, tomcat_process, tomcat_base)
        print("")
        print("RUBROVA LOCAL ACTIVO (sin Docker)")
        print(f"URL: {web_url}")
        print(f"Datos persistentes: {pg_data}")
        print(f"Logs del supervisor y PostgreSQL: {log_dir}")
        print(f"Logs del servidor lsFusion: {logics_dir / 'logs'}")
        print(f"Logs de Tomcat: {tomcat_base / 'logs'}")
        print("El núcleo se ejecuta localmente. Internet sólo se necesita para integraciones externas que estén habilitadas.")
        print("Presioná Ctrl+C para detener los procesos; la base de datos se conserva.")
        if open_browser:
            import webbrowser
            webbrowser.open(web_url)

        while True:
            if server_process.poll() is not None:
                raise RuntimeErrorRubrova("El servidor Rubrova se detuvo inesperadamente.")
            if tomcat_process.poll() is not None:
                raise RuntimeErrorRubrova("Tomcat se detuvo inesperadamente.")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nDeteniendo Rubrova...")
    finally:
        stop_process(tomcat_process, "cliente web")
        stop_process(server_process, "servidor de aplicación")
        stop_postgres(pg_bin, pg_data, postgres_started_here)
        if server_stream:
            server_stream.close()
        if tomcat_stream:
            tomcat_stream.close()
        print("Rubrova quedó detenido. Los datos locales se conservaron.")


def doctor(config_path: Path, allow_tomcat_download: bool) -> None:
    config = load_config(config_path)
    if config["execution"]["target"] != "native-local":
        raise RuntimeErrorRubrova("El destino configurado no es native-local.")
    artifacts = check_artifacts()
    java = find_java(config["local_runtime"].get("java_home"))
    pg_bin = find_postgres_bin(config["local_runtime"].get("postgres_bin"))
    tomcat = download_tomcat(
        dependency_cache_root(),
        allow_download=allow_tomcat_download,
        configured_home=config["local_runtime"].get("tomcat_home"),
    )
    print("Diagnóstico nativo correcto:")
    print(f"  Java: {java}")
    print(f"  PostgreSQL 18: {pg_bin}")
    print(f"  Tomcat: {tomcat}")
    for name, path in artifacts.items():
        print(f"  {name}: {path}")
    print("  Docker: no requerido")


def _handle_termination_signal(signum: int, frame: Any) -> None:
    # Convert TERM into the same cleanup path as Ctrl+C for CI and service managers.
    raise KeyboardInterrupt


def main() -> int:
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_termination_signal)
    parser = argparse.ArgumentParser(description="Vista previa nativa de Rubrova, sin Docker.")
    parser.add_argument("--config", type=Path, default=runtime_config.default_config_path())
    parser.add_argument("--offline", action="store_true", help="No descargar Tomcat si todavía no está en caché.")
    parser.add_argument("--no-open", action="store_true", help="No abrir el navegador automáticamente.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Comprobar Java, PostgreSQL, Tomcat y artefactos.")
    sub.add_parser("start", help="Iniciar PostgreSQL, el servidor Rubrova y el cliente web.")
    args = parser.parse_args()

    try:
        if args.command == "doctor":
            doctor(args.config.expanduser(), allow_tomcat_download=not args.offline)
        else:
            run_preview(
                args.config.expanduser(),
                open_browser=not args.no_open,
                allow_tomcat_download=not args.offline,
            )
    except RuntimeErrorRubrova as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
