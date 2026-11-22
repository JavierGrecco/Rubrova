#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"

ARTIFACT_DIR="${1:-${RUBROVA_BUILD_ARTIFACTS_DIR:-}}"
IMAGE_TAG="${2:-${RUBROVA_RUNTIME_IMAGE_TAG:-${GITHUB_SHA:-local}}}"
IMAGE_TAG="${IMAGE_TAG:0:12}"

if [[ -z "$ARTIFACT_DIR" || ! -d "$ARTIFACT_DIR" ]]; then
  echo "Falta el directorio con los artefactos compilados del mismo SHA de Rubrova." >&2
  echo "Uso: $0 <directorio-con-server.jar-logics.jar-client.war> [tag]" >&2
  exit 2
fi

if [[ ! "$IMAGE_TAG" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$ ]]; then
  echo "Tag de imagen no válido: $IMAGE_TAG" >&2
  exit 2
fi

for artifact in server.jar logics.jar client.war; do
  [[ -s "$ARTIFACT_DIR/$artifact" ]] || {
    echo "Falta el artefacto compilado: $ARTIFACT_DIR/$artifact" >&2
    exit 1
  }
done

SERVER_IMAGE="rubrova/server:6.2-$IMAGE_TAG"
LOGICS_IMAGE="rubrova/logics:6.2-$IMAGE_TAG"
CLIENT_IMAGE="rubrova/client:6.2-$IMAGE_TAG"
BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/rubrova-images.XXXXXX")"
cleanup() {
  local result=$?
  trap - EXIT
  rm -rf "$BUILD_DIR"
  exit "$result"
}
trap cleanup EXIT

mkdir -p "$BUILD_DIR/server" "$BUILD_DIR/logics" "$BUILD_DIR/client"

cp "$ARTIFACT_DIR/server.jar" "$BUILD_DIR/server/server.jar"
cp "$REPO_ROOT/vendor/platform/server/entrypoint.sh" "$BUILD_DIR/server/entrypoint.sh"
cp "$REPO_ROOT/build/rubrova/runtime/Dockerfile.server" "$BUILD_DIR/server/Dockerfile"

cp "$ARTIFACT_DIR/logics.jar" "$BUILD_DIR/logics/mycompany.jar"
cp "$REPO_ROOT/vendor/platform/server/src/main/resources/logics/docker/Dockerfile" "$BUILD_DIR/logics/Dockerfile"
cp "$REPO_ROOT/vendor/platform/server/src/main/resources/logics/docker/entrypoint.sh" "$BUILD_DIR/logics/entrypoint.sh"

cp "$ARTIFACT_DIR/client.war" "$BUILD_DIR/client/client.war"
cp "$REPO_ROOT/build/rubrova/runtime/Dockerfile.client" "$BUILD_DIR/client/Dockerfile"

echo "Construyendo servidor propio: $SERVER_IMAGE"
docker build --platform linux/amd64 --tag "$SERVER_IMAGE" "$BUILD_DIR/server"

echo "Construyendo lógica MyCompany/Rubrova propia: $LOGICS_IMAGE"
docker build --platform linux/amd64 --build-arg FILENAME=mycompany.jar --tag "$LOGICS_IMAGE" "$BUILD_DIR/logics"

echo "Construyendo cliente web propio: $CLIENT_IMAGE"
docker build --platform linux/amd64 --tag "$CLIENT_IMAGE" "$BUILD_DIR/client"

for image in "$SERVER_IMAGE" "$LOGICS_IMAGE" "$CLIENT_IMAGE"; do
  docker image inspect "$image" >/dev/null
  printf 'RUBROVA_RUNTIME_IMAGE=%s\n' "$image"
done

echo "Las tres imágenes de aplicación se construyeron localmente desde artefactos del fork Rubrova."
