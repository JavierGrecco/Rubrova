#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "\${BASH_SOURCE[0]}")/../.." && pwd)"
LOCK_FILE="$ROOT_DIR/platform/source-lock.json"
VENDOR_DIR="$ROOT_DIR/vendor"

for command_name in git tar find python3; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "Falta el comando requerido: $command_name" >&2
    exit 2
  }
done
[[ -s "$LOCK_FILE" ]] || { echo "No existe el lock de fuentes: $LOCK_FILE" >&2; exit 2; }

read_lock() {
  python3 - "$LOCK_FILE" "$1" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    lock = json.load(handle)
source = next(item for item in lock["sources"] if item["name"] == sys.argv[2])
print(source["repository"])
print(source["commit"])
print(source["destination"])
PY
}

import_source() {
  local name="$1"
  local repo commit destination actual temp marker
  mapfile -t fields < <(read_lock "$name")
  repo="\${fields[0]}"
  commit="\${fields[1]}"
  destination="$ROOT_DIR/\${fields[2]}"
  marker="$destination/.rubrova-source.json"

  if [[ -f "$marker" ]]; then
    actual="$(python3 - "$marker" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["commit"])
PY
)"
    if [[ "$actual" == "$commit" ]]; then
      echo "FUENTE YA INCORPORADA: $name @ $commit"
      return 0
    fi
    echo "La fuente $name ya existe en $destination con commit $actual; se requiere revisión manual antes de reemplazarla." >&2
    return 1
  fi

  if [[ -e "$destination" ]] && find "$destination" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
    echo "El destino $destination ya contiene archivos sin marcador de origen. No se sobrescribe." >&2
    return 1
  fi

  temp="$(mktemp -d)"
  git -C "$temp" init -q
  git -C "$temp" remote add origin "$repo"
  echo "Descargando fuente fijada: $name @ $commit"
  git -C "$temp" fetch --depth=1 --no-tags origin "$commit"
  actual="$(git -C "$temp" rev-parse FETCH_HEAD)"
  [[ "$actual" == "$commit" ]] || {
    echo "El commit recibido para $name no coincide: esperado $commit, recibido $actual." >&2
    rm -rf "$temp"
    return 1
  }

  mkdir -p "$destination"
  git -C "$temp" archive "$actual" | tar -x -C "$destination"
  python3 - "$marker" "$name" "$repo" "$commit" <<'PY'
import json, sys
path, name, repo, commit = sys.argv[1:]
with open(path, "w", encoding="utf-8") as handle:
    json.dump({
        "managedBy": "Rubrova",
        "upstreamName": name,
        "repository": repo,
        "commit": commit,
        "note": "This marker is Rubrova metadata. The adjacent files are the upstream source snapshot."
    }, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
PY
  echo "FUENTE INCORPORADA: $name @ $commit"
  rm -rf "$temp"
}

mkdir -p "$VENDOR_DIR"
import_source "lsFusion platform"
import_source "MyCompany"

cat > "$VENDOR_DIR/UPSTREAM_SOURCES.md" <<'MD'
# Fuentes de terceros incorporadas

Estas carpetas contienen snapshots completos, fijados por commit, de proyectos externos incorporados a Rubrova. No son submódulos Git y no se consultan repositorios externos al iniciar la aplicación.

- platform/: lsFusion 6.2. Código bajo LGPL-3.0; conservar LICENSE y avisos originales.
- mycompany/: MyCompany 6.2. Código bajo Apache-2.0; conservar LICENSE y avisos originales.

Los archivos .rubrova-source.json registran el repositorio, nombre y commit exacto. Los archivos de origen se mantienen dentro del repositorio Rubrova. Las modificaciones propias se registran en Git y se documentan; no se sobrescriben automáticamente al actualizar el origen.

Para comparar una futura versión, descargarla en un área temporal, generar un diff por archivo, revisar licencias/dependencias y ejecutar la batería completa. No se permite reemplazar estas carpetas con una rama flotante ni con latest.
MD
