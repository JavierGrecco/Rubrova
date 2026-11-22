#!/usr/bin/env bash
set -Eeuo pipefail

if [[ -n "${RUBROVA_CACHE_DIR:-}" ]]; then
  CACHE_DIR="$RUBROVA_CACHE_DIR"
else
  case "$(uname -s)" in
    Darwin) CACHE_ROOT="${XDG_CACHE_HOME:-$HOME/Library/Caches}" ;;
    *) CACHE_ROOT="${XDG_CACHE_HOME:-$HOME/.cache}" ;;
  esac
  CACHE_DIR="$CACHE_ROOT/Rubrova/platforms/mycompany-6.2"
fi
mkdir -p "$CACHE_DIR"

if [[ "${RUBROVA_SKIP_OFFICIAL_LOGIC_JAR:-false}" == "true" ]]; then
  echo "Omitiendo el JAR oficial de lógica: el smoke usará el ensamblado compilado desde Rubrova."
else
  JAR_URL="https://download.lsfusion.org/solutions/mycompany-6.2.jar"
  JAR_SHA256="fe5a9bda49295f2292ae229a30c9461a16c137fc350a0aa944df7812a1e2f392"
  JAR_PATH="$CACHE_DIR/mycompany-6.2.jar"
  JAR_TMP="$JAR_PATH.download"

  if [[ -f "$JAR_PATH" ]]; then
    actual="$(shasum -a 256 "$JAR_PATH" | awk '{print tolower($1)}')"
    [[ "$actual" == "$JAR_SHA256" ]] || { echo "El JAR existente no coincide con el hash oficial; no se sobrescribió." >&2; exit 1; }
    echo "JAR verificado: $JAR_PATH"
  else
    curl --fail --location --retry 2 --connect-timeout 20 --max-time 600 "$JAR_URL" --output "$JAR_TMP"
    actual="$(shasum -a 256 "$JAR_TMP" | awk '{print tolower($1)}')"
    if [[ "$actual" != "$JAR_SHA256" ]]; then
      rm -f "$JAR_TMP"
      echo "Hash SHA-256 incorrecto. Esperado $JAR_SHA256, recibido $actual." >&2
      exit 1
    fi
    mv "$JAR_TMP" "$JAR_PATH"
    echo "JAR descargado y verificado: $JAR_PATH"
  fi
fi

COMPOSE_URL="https://download.lsfusion.org/solutions/mycompany-docker/6.2/compose.yaml"
COMPOSE_SHA256="4b7eeb62c92a4701f46f18255c290f9227ab9694986aa82e8034b2ea8a3d2def"
COMPOSE_PATH="$CACHE_DIR/compose.yaml"
COMPOSE_TMP="$COMPOSE_PATH.download"
if [[ ! -f "$COMPOSE_PATH" ]]; then
  if ! curl --fail --location --retry 2 --connect-timeout 20 --max-time 120 "$COMPOSE_URL" --output "$COMPOSE_TMP"; then
    rm -f "$COMPOSE_TMP"
    echo "No se pudo descargar el Compose oficial MyCompany 6.2." >&2
    exit 1
  fi
  [[ -s "$COMPOSE_TMP" ]] || { rm -f "$COMPOSE_TMP"; echo "El Compose descargado está vacío." >&2; exit 1; }
  actual="$(shasum -a 256 "$COMPOSE_TMP" | awk '{print tolower($1)}')"
  if [[ "$actual" != "$COMPOSE_SHA256" ]]; then
    rm -f "$COMPOSE_TMP"
    echo "Hash SHA-256 incorrecto para el Compose. Esperado $COMPOSE_SHA256, recibido $actual." >&2
    exit 1
  fi
  mv "$COMPOSE_TMP" "$COMPOSE_PATH"
fi

compose_hash="$(shasum -a 256 "$COMPOSE_PATH" | awk '{print tolower($1)}')"
if [[ "$compose_hash" != "$COMPOSE_SHA256" ]]; then
  echo "El Compose existente no coincide con el SHA-256 fijado; no se sobrescribió." >&2
  exit 1
fi
echo "Compose oficial 6.2 verificado: $COMPOSE_PATH"
echo "SHA-256 del Compose: $compose_hash"
echo "Revisá el contenido y fijá los digests de imagen antes de iniciar contenedores."
case "$(uname -m)" in
  arm64|aarch64)
    echo "AVISO: Apple Silicon: la imagen de lógica MyCompany 6.2 es linux/amd64; el runtime local requerirá emulación y una prueba real. No se fuerza ninguna plataforma ni se inicia Docker."
    ;;
esac
echo "Este script sólo prepara artefactos. No instala ni ejecuta la plataforma."
