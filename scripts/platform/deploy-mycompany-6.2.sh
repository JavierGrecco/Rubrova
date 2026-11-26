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

if [[ "$MODE" == "native" && "$(uname -s)" != "Linux" ]]; then
  echo "El modo native sólo está disponible en Linux. En macOS usá Docker; en Windows, el script PowerShell." >&2
  exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
MODULE_FILES=(
  "RubrovaCustom.lsf"
  "RubrovaPOSLocalization.lsf"
  "RubrovaIntegrationResilience.lsf"
  "RubrovaPaymentTerminals.lsf"
  "RubrovaReplenishmentExport.lsf"
  "RubrovaRetailControls.lsf"
  "MyCompanyResourceBundle_es_AR.properties"
)
for file in "${MODULE_FILES[@]}"; do
  [[ -s "$REPO_ROOT/extensions/lsfusion/$file" ]] || {
    echo "Falta el archivo requerido: $REPO_ROOT/extensions/lsfusion/$file" >&2
    exit 1
  }
done

if [[ "$MODE" == "docker" ]]; then
  INSTALL_DIR="$(cd -- "$TARGET" && pwd)"
  [[ -s "$INSTALL_DIR/compose.yaml" ]] || {
    echo "No se encontró compose.yaml. Prepará y revisá el Compose oficial MyCompany 6.2 primero." >&2
    exit 1
  }
  OVERRIDE_SOURCE="$REPO_ROOT/platform/compose.rubrova.override.yaml"
  [[ -s "$OVERRIDE_SOURCE" ]] || {
    echo "Falta el override Docker de Rubrova: $OVERRIDE_SOURCE" >&2
    exit 1
  }
  OVERRIDE_TARGET="$INSTALL_DIR/compose.rubrova.override.yaml"
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

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_SETTINGS=""
BACKUP_OVERRIDE=""
if [[ -e "$SETTINGS_FILE" ]]; then
  BACKUP_SETTINGS="$SETTINGS_FILE.rubrova-backup.$STAMP"
  cp -p "$SETTINGS_FILE" "$BACKUP_SETTINGS"
  chmod 600 "$BACKUP_SETTINGS" 2>/dev/null || true
fi
if [[ "$MODE" == "docker" && -e "$OVERRIDE_TARGET" ]]; then
  BACKUP_OVERRIDE="$OVERRIDE_TARGET.rubrova-backup.$STAMP"
  cp -p "$OVERRIDE_TARGET" "$BACKUP_OVERRIDE"
fi

TMP_SETTINGS="$(mktemp)"
cleanup() { rm -f "$TMP_SETTINGS"; }
trap cleanup EXIT

if [[ -f "$SETTINGS_FILE" ]]; then
  cp "$SETTINGS_FILE" "$TMP_SETTINGS"
else
  : > "$TMP_SETTINGS"
fi

python3 - "$TMP_SETTINGS" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8-sig") if path.exists() else ""
lines = text.splitlines()
settings = {
    "logics.topModule": "RubrovaCustom",
    "user.setLanguage": "es",
    "user.setCountry": "AR",
}
for key, value in settings.items():
    pattern = re.compile(r"^[ \t]*" + re.escape(key) + r"[ \t]*=")
    matches = [index for index, line in enumerate(lines) if pattern.match(line)]
    replacement = f"{key} = {value}"
    if matches:
        lines[matches[0]] = replacement
        for duplicate_index in reversed(matches[1:]):
            lines.pop(duplicate_index)
    else:
        lines.append(replacement)
path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
PY

if [[ "$RESTART_NATIVE" -eq 1 ]]; then
  systemctl stop lsfusion6-server
fi

for file in "${MODULE_FILES[@]}"; do
  destination="$MODULE_DIR/$file"
  if [[ -e "$destination" ]]; then
    cp -p "$destination" "$destination.rubrova-backup.$STAMP"
  fi
  install -m 0644 "$REPO_ROOT/extensions/lsfusion/$file" "$destination"
done
install -m 0640 "$TMP_SETTINGS" "$SETTINGS_FILE"

if [[ "$MODE" == "docker" ]]; then
  install -m 0644 "$OVERRIDE_SOURCE" "$OVERRIDE_TARGET"
fi

if [[ "$RESTART_NATIVE" -eq 1 ]]; then
  systemctl start lsfusion6-server
  systemctl is-active --quiet lsfusion6-server || {
    echo "El servicio no quedó activo. Restaurá settings y los archivos .rubrova-backup.$STAMP antes de reintentar." >&2
    exit 1
  }
  echo "Extensión Rubrova instalada y servicio lsfusion6-server activo."
else
  echo "Módulos, ResourceBundle y override Docker preparados en $INSTALL_DIR."
  echo "Se configuraron logics.topModule=RubrovaCustom, user.setLanguage=es y user.setCountry=AR."
  echo "Para aplicar la configuración, ejecutá:"
  echo "  docker compose -f compose.yaml -f compose.rubrova.override.yaml up -d"
  echo "Este script no inicia ni modifica contenedores."
fi

echo "Módulos instalados:"
for file in "${MODULE_FILES[@]}"; do echo "  $MODULE_DIR/$file"; done
[[ -n "$BACKUP_SETTINGS" ]] && echo "Backup de settings: $BACKUP_SETTINGS"
[[ -n "$BACKUP_OVERRIDE" ]] && echo "Backup del override: $BACKUP_OVERRIDE"
echo "La carga efectiva debe confirmarse en el log del servidor y en la interfaz."
