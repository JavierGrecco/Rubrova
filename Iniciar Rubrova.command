#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$REPO_ROOT"

fail() {
  printf '\nERROR: %s\n' "$1" >&2
  printf '\nConsultá docs/MACOS_SUPPORT.md para revisar los requisitos.\n' >&2
  exit 2
}

if [[ "$(uname -s)" != "Darwin" ]]; then
  fail "Este acceso directo es exclusivo de macOS."
fi

command -v python3 >/dev/null 2>&1 || fail "No se encontró Python 3. Instalalo y volvé a abrir Rubrova."
command -v java >/dev/null 2>&1 || fail "No se encontró Java 21. Instalá un JDK 21 para macOS."

if ! java -version 2>&1 | grep -Eq 'version "21([.]|")'; then
  java -version 2>&1 || true
  fail "Rubrova requiere Java 21. La versión activa no es compatible."
fi
JAVA_ARCH="$(java -XshowSettings:properties -version 2>&1 | sed -n 's/^[[:space:]]*os.arch = //p' | head -n 1)"
HOST_ARCH="$(uname -m)"
case "$HOST_ARCH:$JAVA_ARCH" in
  arm64:aarch64|arm64:arm64|x86_64:amd64|x86_64:x86_64) ;;
  *) fail "Java ($JAVA_ARCH) no coincide con la arquitectura de este Mac ($HOST_ARCH). Instalá el JDK 21 nativo correspondiente." ;;
esac

# Detectar PostgreSQL 18 sin iniciar ni modificar servicios ajenos.
if [[ -z "${RUBROVA_POSTGRES_BIN:-}" ]]; then
  for candidate in \
    "/Applications/Postgres.app/Contents/Versions/18/bin" \
    "/opt/homebrew/opt/postgresql@18/bin" \
    "/usr/local/opt/postgresql@18/bin"; do
    if [[ -x "$candidate/pg_ctl" && -x "$candidate/initdb" && -x "$candidate/pg_isready" && -x "$candidate/createdb" && -x "$candidate/psql" ]]; then
      export RUBROVA_POSTGRES_BIN="$candidate"
      break
    fi
  done
fi

if [[ -n "${RUBROVA_POSTGRES_BIN:-}" ]]; then
  PG_BIN="$RUBROVA_POSTGRES_BIN"
elif command -v pg_ctl >/dev/null 2>&1; then
  PG_BIN="$(dirname "$(command -v pg_ctl)")"
else
  fail "No se encontraron las herramientas de PostgreSQL 18. Instalá Postgres.app 18 o Homebrew postgresql@18."
fi
for tool in initdb pg_ctl pg_isready createdb psql; do
  [[ -x "$PG_BIN/$tool" ]] || fail "Falta $tool en $PG_BIN. Se necesitan todas las herramientas de PostgreSQL 18."
done
export RUBROVA_POSTGRES_BIN="$PG_BIN"
if ! "$PG_BIN/pg_ctl" --version | grep -Eq 'PostgreSQL\) 18([.]|$)'; then
  "$PG_BIN/pg_ctl" --version || true
  fail "La instalación encontrada no es PostgreSQL 18."
fi

SERVER_JAR="vendor/platform/server/target/lsfusion-server-6.2.jar"
LOGICS_JAR="vendor/mycompany/target/lsfusion-server-6.2.jar"
CLIENT_WAR="vendor/platform/web-client/target/lsfusion-client-6.2.war"
NEEDS_BUILD=false
for artifact in "$SERVER_JAR" "$LOGICS_JAR" "$CLIENT_WAR"; do
  if [[ ! -s "$artifact" ]]; then
    NEEDS_BUILD=true
    break
  fi
done

# No reutilizar artefactos de otra revisión ni de un árbol modificado.
command -v git >/dev/null 2>&1 || fail "No se encontró Git. Abrí Rubrova desde una copia clonada del repositorio."
CURRENT_REVISION="$(git rev-parse HEAD 2>/dev/null)" || fail "Esta carpeta no parece ser un repositorio Git de Rubrova."
BUILD_STATE_DIR="$HOME/Library/Application Support/Rubrova"
BUILD_STAMP="$BUILD_STATE_DIR/native-build-revision"
WORKTREE_STATE="$(git status --porcelain)"
if [[ ! -s "$BUILD_STAMP" ]] || [[ "$(cat "$BUILD_STAMP")" != "$CURRENT_REVISION" ]] || [[ -n "$WORKTREE_STATE" ]]; then
  NEEDS_BUILD=true
fi
if [[ "${RUBROVA_FORCE_BUILD:-false}" == "true" ]]; then
  NEEDS_BUILD=true
fi

if [[ "$NEEDS_BUILD" == "true" ]]; then
  command -v mvn >/dev/null 2>&1 || fail "Faltan artefactos actualizados y no se encontró Maven. Instalá Maven para compilar Rubrova."
  printf '\nCompilando Rubrova desde las fuentes fijadas de lsFusion 6.2 y MyCompany 6.2...\n'
  mvn -B -ntp -f build/rubrova/pom.xml -Passemble -DskipTests package
  mvn -B -ntp -f vendor/platform/pom.xml -pl server,web-client -am -DskipTests package
  test -s "$SERVER_JAR" && test -s "$LOGICS_JAR" && test -s "$CLIENT_WAR" || fail "La compilación terminó, pero falta uno o más artefactos del runtime."
  mkdir -p "$BUILD_STATE_DIR"
  printf '%s\n' "$CURRENT_REVISION" > "$BUILD_STAMP"
else
  printf '\nLos artefactos corresponden a esta revisión y no hay cambios locales. Se omite la recompilación.\n'
fi

printf '\nPreparando la configuración local (sin Docker)...\n'
python3 scripts/platform/runtime-config.py init
printf '\nComprobando Java, PostgreSQL, Tomcat y artefactos...\n'
python3 scripts/platform/run-local-native-preview.py doctor
printf '\nIniciando Rubrova local. El navegador se abrirá cuando el POS esté listo.\n'
printf 'Para detenerlo, volvé a esta ventana y presioná Ctrl+C. La base local se conserva.\n\n'
exec python3 scripts/platform/run-local-native-preview.py start
