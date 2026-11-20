#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

fail() { echo "ERROR: $*" >&2; exit 1; }
[[ -f vendor/platform/.rubrova-source.json ]] || fail "No está incorporado el snapshot lsFusion."
[[ -f vendor/mycompany/.rubrova-source.json ]] || fail "No está incorporado el snapshot MyCompany."
[[ -f vendor/platform/LICENSE ]] || fail "Falta la licencia original de lsFusion."
[[ -f vendor/mycompany/LICENSE ]] || fail "Falta la licencia original de MyCompany."
[[ -f vendor/platform/server/pom.xml ]] || fail "Falta el proyecto del servidor lsFusion."
[[ -f vendor/platform/web-client/pom.xml ]] || fail "Falta el proyecto del cliente web lsFusion."
[[ -f vendor/mycompany/pom.xml ]] || fail "Falta el POM original de MyCompany."
[[ -f vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/PosDashboard.lsf ]] || fail "Falta el código del POS de MyCompany."
[[ -f vendor/platform/server/src/main/java/lsfusion/server/logics/BusinessLogicsBootstrap.java ]] || fail "Falta la clase de inicio del motor."

grep -q "relativePath>../platform/build/logics/pom.xml" vendor/mycompany/pom.xml || fail "El layout de vendor no respeta la ruta de parent POM esperada."
grep -q "Apache License" vendor/mycompany/LICENSE || fail "No se reconoce la licencia Apache original de MyCompany."
grep -q "GNU LESSER GENERAL PUBLIC LICENSE" vendor/platform/LICENSE || fail "No se reconoce la licencia LGPL original de lsFusion."

platform_files="$(find vendor/platform -type f | wc -l | tr -d ' ')"
mycompany_files="$(find vendor/mycompany -type f | wc -l | tr -d ' ')"
platform_java="$(find vendor/platform -type f -name '*.java' | wc -l | tr -d ' ')"
platform_lsf="$(find vendor/platform -type f -name '*.lsf' | wc -l | tr -d ' ')"
mycompany_lsf="$(find vendor/mycompany -type f -name '*.lsf' | wc -l | tr -d ' ')"

[[ "$platform_files" -ge 4800 ]] || fail "El snapshot lsFusion parece incompleto: $platform_files archivos."
[[ "$mycompany_files" -ge 1300 ]] || fail "El snapshot MyCompany parece incompleto: $mycompany_files archivos."
[[ "$platform_java" -ge 3300 ]] || fail "Faltan fuentes Java del motor: $platform_java."
[[ "$platform_lsf" -ge 45 ]] || fail "Faltan módulos lsFusion del motor: $platform_lsf."
[[ "$mycompany_lsf" -ge 790 ]] || fail "Faltan módulos de MyCompany: $mycompany_lsf."

if find vendor -type d -name .git -print -quit | grep -q .; then
  fail "No se permiten repositorios Git anidados: las fuentes deben vivir en el historial de Rubrova."
fi
if find vendor -type f -size +90M -print -quit | grep -q .; then
  fail "Hay un archivo de más de 90 MiB en vendor; debe revisarse antes de subirlo."
fi

printf 'FUENTES VERIFICADAS\nlsFusion: archivos=%s Java=%s LSF=%s\nMyCompany: archivos=%s LSF=%s\n' \
  "$platform_files" "$platform_java" "$platform_lsf" "$mycompany_files" "$mycompany_lsf"
