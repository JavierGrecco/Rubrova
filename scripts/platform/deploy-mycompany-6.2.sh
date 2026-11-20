#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 docker <carpeta-con-compose-6.2> | native <carpeta-de-instalacion>" >&2
  exit 2
fi
MODE="$1"
TARGET="$PWD"
if [[ $# -ge 2 ]]; then TARGET="$2"; fi

if [[ "$MODE" != "docker" && "$MODE" != "native" ]]; then
  echo "Modo no válido: $MODE. Usá docker o native." >&2
  exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
MODULE_SOURCE="$REPO_ROOT/extensions/lsfusion/RubrovaCustom.lsf"
BUNDLE_SOURCE="$REPO_ROOT/extensions/lsfusion/MyCompanyResourceBundle_es_AR.properties"

for file in "$MODULE_SOURCE" "$BUNDLE_SOURCE"; do
  [[ -s "$file" ]] || { echo "Falta el archivo requerido: $file" >&2; exit 1; }
done

BACKUP=""
if [[ "$MODE" == "docker" ]]; then
  INSTALL_DIR="$(cd -- "$TARGET" && pwd)"
  [[ -s "$INSTALL_DIR/compose.yaml" ]] || {
    echo "No se encontró compose.yaml. Prepará y revisá el Compose oficial MyCompany 6.2 primero." >&2
    exit 1
  }
  MODULE_DIR="$INSTALL_DIR/docker-server"
  SETTINGS_FILE="$MODULE_DIR/settings.properties"
  mkdir -p "$MODULE_DIR"
  RESTART_NATIVE=0
else
  if [[ "$EUID" -ne 0 ]]; then
    echo "El modo native necesita permisos de administrador (sudo)." >&2
    exit 1
  fi
  MODULE_DIR="$(printenv RUBROVA_LSFUSION_MODULE_DIR || true)"
  SETTINGS_FILE="$(printenv RUBROVA_LSFUSION_SETTINGS || true)"
  [[ -n "$MODULE_DIR" ]] || MODULE_DIR="/var/lib/lsfusion"
  [[ -n "$SETTINGS_FILE" ]] || SETTINGS_FILE="/etc/lsfusion6-server/settings.properties"
  [[ -d "$MODULE_DIR" ]] || { echo "No existe el directorio de módulos: $MODULE_DIR" >&2; exit 1; }
  [[ -f "$SETTINGS_FILE" ]] || { echo "No existe settings.properties: $SETTINGS_FILE" >&2; exit 1; }
  RESTART_NATIVE=1
fi

if [[ -e "$SETTINGS_FILE" ]]; then
  BACKUP="$SETTINGS_FILE.rubrova-backup.$(date +%Y%m%d-%H%M%S)"
  cp -p -- "$SETTINGS_FILE" "$BACKUP"
  chmod 600 "$BACKUP" 2>/dev/null || true
fi

TMP_SETTINGS="$(mktemp)"
cleanup() { rm -f -- "$TMP_SETTINGS"; }
trap cleanup EXIT

if [[ -f "$SETTINGS_FILE" ]]; then
  cp -- "$SETTINGS_FILE" "$TMP_SETTINGS"
else
  : > "$TMP_SETTINGS"
fi

python3 - "$TMP_SETTINGS" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8-sig") if path.exists() else ""
pattern = re.compile(r"^\s*logics\.topModule\s*=.*$", re.MULTILINE)
replacement = "logics.topModule = RubrovaCustom"
updated, count = pattern.subn(replacement, text)
if count == 0:
    updated = text.rstrip("\r\n")
    if updated:
        updated += "\n"
    updated += replacement + "\n"
path.write_text(updated, encoding="utf-8", newline="\n")
PY

if [[ "$RESTART_NATIVE" -eq 1 ]]; then
  systemctl stop lsfusion6-server
fi

install -m 0644 "$MODULE_SOURCE" "$MODULE_DIR/RubrovaCustom.lsf"
install -m 0644 "$BUNDLE_SOURCE" "$MODULE_DIR/MyCompanyResourceBundle_es_AR.properties"
install -m 0640 "$TMP_SETTINGS" "$SETTINGS_FILE"

if [[ "$RESTART_NATIVE" -eq 1 ]]; then
  systemctl start lsfusion6-server
  systemctl is-active --quiet lsfusion6-server || {
    echo "El servicio no quedó activo. Revisá el log de inicio y restaurá el backup de settings si hace falta." >&2
    exit 1
  }
  echo "Extensión copiada y servicio lsfusion6-server activo."
else
  echo "Extensión y ResourceBundle preparados en $MODULE_DIR."
  echo "Se configuró logics.topModule=RubrovaCustom."
  echo "No se inició ni modificó ningún contenedor. Revisá el Compose y reiniciá el stack manualmente."
fi

echo "Módulo: $MODULE_DIR/RubrovaCustom.lsf"
echo "Traducción: $MODULE_DIR/MyCompanyResourceBundle_es_AR.properties"
if [[ -n "$BACKUP" ]]; then echo "Backup local de settings: $BACKUP"; fi
echo "La carga efectiva debe confirmarse en el log del servidor y en la interfaz."
