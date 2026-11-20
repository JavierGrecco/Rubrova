#!/usr/bin/env bash
set -Eeuo pipefail

CACHE_DIR="$HOME/.cache/rubrova/platforms/mycompany-6.2"
mkdir -p "$CACHE_DIR"

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

COMPOSE_URL="https://download.lsfusion.org/solutions/mycompany-docker/6.2/compose.yaml"
COMPOSE_PATH="$CACHE_DIR/compose.yaml"
COMPOSE_TMP="$COMPOSE_PATH.download"
if [[ ! -f "$COMPOSE_PATH" ]]; then
  curl --fail --location --retry 2 --connect-timeout 20 --max-time 120 "$COMPOSE_URL" --output "$COMPOSE_TMP"
  [[ -s "$COMPOSE_TMP" ]] || { rm -f "$COMPOSE_TMP"; echo "El Compose descargado está vacío." >&2; exit 1; }
  mv "$COMPOSE_TMP" "$COMPOSE_PATH"
fi

compose_hash="$(shasum -a 256 "$COMPOSE_PATH" | awk '{print tolower($1)}')"
echo "Compose oficial versionado 6.2: $COMPOSE_PATH"
echo "SHA-256 local del Compose: $compose_hash"
echo "Revisá el contenido y fijá los digests de imagen antes de iniciar contenedores."
case "$(uname -m)" in
  arm64|aarch64)
    echo "AVISO: Apple Silicon: verificar arquitectura de cada imagen y medir emulación; no usar tags SNAPSHOT."
    ;;
esac
echo "Este script sólo prepara artefactos. No instala ni ejecuta la plataforma."
