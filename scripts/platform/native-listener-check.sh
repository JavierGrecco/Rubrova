#!/usr/bin/env bash
# Validate that every listening socket is bound only to Rubrova's configured loopback.
# Linux ss may display an IPv4 loopback socket as an IPv4-mapped IPv6 address.

rubrova_assert_loopback_listeners() {
  local host_os="$1"
  local service="$2"
  local port="$3"
  local output="$4"
  local endpoints
  local endpoint
  local count=0

  case "$host_os" in
    Linux)
      # ss -H -ltn: State Recv-Q Send-Q Local-Address:Port Peer-Address:Port
      endpoints="$(awk '$1 == "LISTEN" && NF >= 5 { print $4 }' <<< "$output")"
      ;;
    Darwin)
      # lsof -nP -iTCP:<port> -sTCP:LISTEN ends with "<local-endpoint> (LISTEN)".
      endpoints="$(awk '/TCP/ && /\(LISTEN\)$/ && NF >= 2 { print $(NF - 1) }' <<< "$output")"
      ;;
    *)
      printf '%s: sistema no admitido para validar listeners: %s\n' "$service" "$host_os" >&2
      return 2
      ;;
  esac

  if [[ -z "$endpoints" ]]; then
    printf '%s: no se encontró ningún listener TCP en el puerto $port.\n' "$service" >&2
    return 1
  fi

  while IFS= read -r endpoint; do
    [[ -n "$endpoint" ]] || continue
    count=$((count + 1))
    case "$endpoint" in
      "127.0.0.1:$port"|"[::ffff:127.0.0.1]:$port")
        ;;
      *)
        printf '%s: listener fuera del loopback permitido en el puerto $port: %s\n' \
          "$service" "$endpoint" >&2
        return 1
        ;;
    esac
  done <<< "$endpoints"

  if (( count == 0 )); then
    printf '%s: no se pudo interpretar ningún listener del puerto $port.\n' "$service" >&2
    return 1
  fi

  return 0
}
