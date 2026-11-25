#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"
if [[ "$(uname -s)" != "Darwin" ]]; then
  printf '\nERROR: La demostración de doble clic está preparada para macOS.\n' >&2
  exit 2
fi
command -v python3 >/dev/null 2>&1 || {
  printf '\nERROR: Se necesita Python 3 para preparar el runtime nativo.\n' >&2
  exit 2
}

# La demostración usa configuración, PostgreSQL, puertos y datos separados del runtime normal.
export RUBROVA_RUNTIME_CONFIG_PATH="$HOME/Library/Application Support/Rubrova/demo-runtime-config.json"
export RUBROVA_LOCAL_DEMO_DATA=true

python3 "$REPO_ROOT/scripts/platform/run-local-native-preview.py" init-demo
exec "$REPO_ROOT/Iniciar Rubrova.command"
