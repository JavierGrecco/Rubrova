#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck source=scripts/platform/native-listener-check.sh
source "$SCRIPT_DIR/native-listener-check.sh"

expect_pass() {
  local label="$1"
  local host_os="$2"
  local service="$3"
  local port="$4"
  local output="$5"
  if ! rubrova_assert_loopback_listeners "$host_os" "$service" "$port" "$output" >/dev/null; then
    printf 'ERROR: el caso válido falló: %s\n' "$label" >&2
    exit 1
  fi
}

expect_fail() {
  local label="$1"
  local host_os="$2"
  local service="$3"
  local port="$4"
  local output="$5"
  if rubrova_assert_loopback_listeners "$host_os" "$service" "$port" "$output" >/dev/null 2>&1; then
    printf 'ERROR: se aceptó un listener no permitido: %s\n' "$label" >&2
    exit 1
  fi
}

# Linux ss output: accept both native IPv4 loopback and IPv4-mapped IPv6 loopback.
expect_pass "Linux RMI IPv4-mapped loopback" Linux RMI 7652 \
  'LISTEN 0 500 [::ffff:127.0.0.1]:7652 *:*'
expect_pass "Linux PostgreSQL IPv4 loopback" Linux PostgreSQL 55432 \
  'LISTEN 0 128 127.0.0.1:55432 0.0.0.0:*'

# macOS lsof output.
expect_pass "macOS RMI loopback" Darwin RMI 7652 \
  'java 123 runner 20u IPv6 0x123 0t0 TCP 127.0.0.1:7652 (LISTEN)'

# A wildcard, IPv6 wildcard, LAN address, or a mixed listener set must fail.
expect_fail "Linux IPv4 wildcard" Linux RMI 7652 \
  'LISTEN 0 500 0.0.0.0:7652 0.0.0.0:*'
expect_fail "Linux IPv6 wildcard" Linux RMI 7652 \
  'LISTEN 0 500 [::]:7652 [::]:*'
expect_fail "Linux LAN address" Linux RMI 7652 \
  'LISTEN 0 500 192.168.1.20:7652 0.0.0.0:*'
expect_fail "mixed loopback and external listeners" Linux RMI 7652 \
  $'LISTEN 0 500 127.0.0.1:7652 0.0.0.0:*\nLISTEN 0 500 10.0.0.5:7652 0.0.0.0:*'
expect_fail "missing listener" Linux RMI 7652 ''

echo "NATIVE_LOOPBACK_LISTENER_TESTS=passed"
