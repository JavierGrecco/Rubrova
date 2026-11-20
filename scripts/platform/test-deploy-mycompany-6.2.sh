#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_SCRIPT="$SCRIPT_DIR/deploy-mycompany-6.2.sh"

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TEMP_DIR"' EXIT

INSTALL_DIR="$TEMP_DIR/mycompany-6.2"
MODULE_DIR="$INSTALL_DIR/docker-server"
mkdir -p "$MODULE_DIR"

# A minimal marker is enough: the deploy helper stages files and settings only.
printf 'services: {}\n' > "$INSTALL_DIR/compose.yaml"
printf '# Existing local settings\nlogics.topModule = OldModule\ncustom.setting = preserve-me\n' > "$MODULE_DIR/settings.properties"
printf 'previous module content\n' > "$MODULE_DIR/RubrovaPOSLocalization.lsf"

# Fail immediately if the script unexpectedly tries to invoke Docker.
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
  "MyCompanyResourceBundle_es_AR.properties"
do
  cmp -s "$REPO_ROOT/extensions/lsfusion/$file" "$MODULE_DIR/$file" || {
    echo "El archivo desplegado no coincide: $file" >&2
    exit 1
  }
done

grep -q '^custom.setting = preserve-me

backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaPOSLocalization.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup del módulo existente." >&2
  exit 1
}

settings_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'settings.properties.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$settings_backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup de settings.properties." >&2
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

echo "OK: staging Docker simulado; 3 archivos copiados, settings preservado y backups generados. Docker no fue invocado."
 "$MODULE_DIR/settings.properties"
grep -q '^logics.topModule = RubrovaCustom

backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaPOSLocalization.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup del módulo existente." >&2
  exit 1
}

settings_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'settings.properties.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$settings_backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup de settings.properties." >&2
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

echo "OK: staging Docker simulado; 3 archivos copiados, settings preservado y backups generados. Docker no fue invocado."
 "$MODULE_DIR/settings.properties"
grep -q '^user.setLanguage = es

backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaPOSLocalization.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup del módulo existente." >&2
  exit 1
}

settings_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'settings.properties.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$settings_backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup de settings.properties." >&2
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

echo "OK: staging Docker simulado; 3 archivos copiados, settings preservado y backups generados. Docker no fue invocado."
 "$MODULE_DIR/settings.properties"
grep -q '^user.setCountry = AR

backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaPOSLocalization.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup del módulo existente." >&2
  exit 1
}

settings_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'settings.properties.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$settings_backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup de settings.properties." >&2
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

echo "OK: staging Docker simulado; 3 archivos copiados, settings preservado y backups generados. Docker no fue invocado."
 "$MODULE_DIR/settings.properties"

for setting_key in logics.topModule user.setLanguage user.setCountry; do
  setting_count="$(grep -c "^$setting_key =" "$MODULE_DIR/settings.properties")"
  [[ "$setting_count" -eq 1 ]] || {
    echo "Se esperaba un único $setting_key; se encontró $setting_count." >&2
    exit 1
  }
done

backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'RubrovaPOSLocalization.lsf.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup del módulo existente." >&2
  exit 1
}

settings_backup_count="$(find "$MODULE_DIR" -maxdepth 1 -type f -name 'settings.properties.rubrova-backup.*' | wc -l | tr -d ' ')"
[[ "$settings_backup_count" -eq 1 ]] || {
  echo "No se generó exactamente un backup de settings.properties." >&2
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

echo "OK: staging Docker simulado; 3 archivos copiados, settings preservado y backups generados. Docker no fue invocado."
