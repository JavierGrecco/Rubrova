#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_SCRIPT="$SCRIPT_DIR/deploy-mycompany-6.2.sh"
OVERRIDE_SOURCE="$REPO_ROOT/platform/compose.rubrova.override.yaml"

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TEMP_DIR"' EXIT

INSTALL_DIR="$TEMP_DIR/mycompany-6.2"
MODULE_DIR="$INSTALL_DIR/docker-server"
mkdir -p "$MODULE_DIR"

printf 'services: {}\n' > "$INSTALL_DIR/compose.yaml"
printf '# Existing local settings\nlogics.topModule = OldModule\nuser.setLanguage = ru\nuser.setCountry = RU\ncustom.setting = preserve-me\n' > "$MODULE_DIR/settings.properties"
printf 'previous module content\n' > "$MODULE_DIR/RubrovaPOSLocalization.lsf"
printf 'previous resilience module content\n' > "$MODULE_DIR/RubrovaIntegrationResilience.lsf"
printf 'previous payment terminal module content\n' > "$MODULE_DIR/RubrovaPaymentTerminals.lsf"
printf 'previous replenishment export module content\n' > "$MODULE_DIR/RubrovaReplenishmentExport.lsf"
printf 'previous retail returns module content\n' > "$MODULE_DIR/RubrovaRetailReturns.lsf"
printf 'previous override content\n' > "$INSTALL_DIR/compose.rubrova.override.yaml"

FAKE_BIN="$TEMP_DIR/bin"
mkdir -p "$FAKE_BIN"
cat > "$FAKE_BIN/docker" <<'SH'
#!/usr/bin/env sh
echo "The staging helper must not start Docker commands." >&2
exit 97
SH
chmod +x "$FAKE_BIN/docker"

PATH="$FAKE_BIN:$PATH" bash "$DEPLOY_SCRIPT" docker "$INSTALL_DIR"

for file in \
  "RubrovaCustom.lsf" \
  "RubrovaPOSLocalization.lsf" \
  "RubrovaIntegrationResilience.lsf" \
  "RubrovaPaymentTerminals.lsf" \
  "RubrovaReplenishmentExport.lsf" \
  "RubrovaRetailReturns.lsf" \
  "MyCompanyResourceBundle_es_AR.properties"
do
  cmp -s "$REPO_ROOT/extensions/lsfusion/$file" "$MODULE_DIR/$file" || {
    echo "El archivo desplegado no coincide: $file" >&2
    exit 1
  }
done

cmp -s "$OVERRIDE_SOURCE" "$INSTALL_DIR/compose.rubrova.override.yaml" || {
  echo "El override Docker desplegado no coincide con el archivo controlado por Rubrova." >&2
  exit 1
}
grep -Fq 'JAVA_OPTS: "-Dlogics.topModule=RubrovaCustom"' "$INSTALL_DIR/compose.rubrova.override.yaml"
grep -Fq 'USER_SETLANGUAGE: "es"' "$INSTALL_DIR/compose.rubrova.override.yaml"
grep -Fq 'USER_SETCOUNTRY: "AR"' "$INSTALL_DIR/compose.rubrova.override.yaml"
grep -Fq 'image: postgres:18@sha256:eb63372c1e05c755f55fa30cbd07aecc443676fc6c0fa90b9002d01537841e1a' "$INSTALL_DIR/compose.rubrova.override.yaml"
grep -Fq './docker-db-pg18:/var/lib/postgresql' "$INSTALL_DIR/compose.rubrova.override.yaml"
grep -Fq 'condition: service_healthy' "$INSTALL_DIR/compose.rubrova.override.yaml"
grep -Fq 'pg_isready -U postgres -d postgres' "$INSTALL_DIR/compose.rubrova.override.yaml"

grep -q '^custom.setting = preserve-me$' "$MODULE_DIR/settings.properties"
grep -q '^logics.topModule = RubrovaCustom$' "$MODULE_DIR/settings.properties"
grep -q '^user.setLanguage = es$' "$MODULE_DIR/settings.properties"
grep -q '^user.setCountry = AR$' "$MODULE_DIR/settings.properties"

for setting_key in logics.topModule user.setLanguage user.setCountry; do
  setting_count="$(grep -c "^$setting_key =" "$MODULE_DIR/settings.properties")"
  [[ "$setting_count" -eq 1 ]] || {
    echo "Se esperaba un único $setting_key; se encontró $setting_count." >&2
    exit 1
  }
done

module_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaPOSLocalization.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$module_backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup del módulo existente." >&2
  exit 1
}

resilience_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaIntegrationResilience.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$resilience_backup_count" -eq 1 ]] || { echo "No se generó el backup del módulo de resiliencia existente." >&2; exit 1; }

payment_terminal_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaPaymentTerminals.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$payment_terminal_backup_count" -eq 1 ]] || { echo "No se generó el backup del módulo de terminales existente." >&2; exit 1; }

replenishment_export_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaReplenishmentExport.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$replenishment_export_backup_count" -eq 1 ]] || { echo "No se generó el backup del módulo de exportación de reposición existente." >&2; exit 1; }
retail_returns_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaRetailReturns.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$retail_returns_backup_count" -eq 1 ]] || { echo "No se generó el backup del módulo de devoluciones parciales existente." >&2; exit 1; }

settings_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'settings.properties.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$settings_backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup de settings.properties." >&2
  exit 1
}

override_backup_count="$(find "$INSTALL_DIR" -maxdepth 1 -type f -name 'compose.rubrova.override.yaml.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$override_backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup del override Docker existente." >&2
  exit 1
}

if [[ "$(uname -s)" == "Darwin" ]]; then
  native_log="$TEMP_DIR/native-mode.log"
  native_exit=0
  bash "$DEPLOY_SCRIPT" native "$INSTALL_DIR" > "$native_log" 2>&1 || native_exit=$?
  [[ "$native_exit" -eq 2 ]] || {
    echo "El modo native debía rechazarse en macOS con código 2." >&2
    exit 1
  }
  grep -q "El modo native sólo está disponible en Linux" "$native_log" || {
    echo "No se explicó cómo desplegar desde macOS." >&2
    exit 1
  }
fi

echo "OK: staging Docker simulado; módulos, overlay, idioma y país configurados; settings y backups preservados. Docker no fue invocado."
