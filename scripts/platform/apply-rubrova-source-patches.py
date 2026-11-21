#!/usr/bin/env python3
"""Apply Rubrova's bounded HTTP timeout policy to the pinned lsFusion source."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / (
    "vendor/platform/server/src/main/java/lsfusion/server/physics/dev/integration/external/to/"
    "CallHTTPAction.java"
)

REPLACEMENTS = (
    (
        "public abstract class CallHTTPAction extends CallAction {\n",
        "public abstract class CallHTTPAction extends CallAction {\n"
        "    // Rubrova safety net for every EXTERNAL HTTP call, including upstream modules.\n"
        "    private static final long RUBROVA_DEFAULT_EXTERNAL_HTTP_TIMEOUT_MS = 10_000L;\n"
        "    private static final long RUBROVA_MAX_EXTERNAL_HTTP_TIMEOUT_MS = 60_000L;\n",
    ),
    (
        "                Long timeout = nvl((Long) context.getBL().LM.timeoutHttp.read(context), getDefaultTimeout());",
        "                Long configuredTimeout = (Long) context.getBL().LM.timeoutHttp.read(context);\n"
        "                Long timeout = configuredTimeout == null ? getDefaultTimeout()\n"
        "                        : Math.max(1L, Math.min(configuredTimeout, RUBROVA_MAX_EXTERNAL_HTTP_TIMEOUT_MS));",
    ),
    (
        "    protected Long getDefaultTimeout() {\n"
        "        return 1800000L; //30 minutes\n"
        "    }",
        "    protected Long getDefaultTimeout() {\n"
        "        return RUBROVA_DEFAULT_EXTERNAL_HTTP_TIMEOUT_MS;\n"
        "    }",
    ),
)

REQUIRED_MARKERS = (
    "RUBROVA_DEFAULT_EXTERNAL_HTTP_TIMEOUT_MS = 10_000L",
    "RUBROVA_MAX_EXTERNAL_HTTP_TIMEOUT_MS = 60_000L",
    "Math.min(configuredTimeout, RUBROVA_MAX_EXTERNAL_HTTP_TIMEOUT_MS)",
    "return RUBROVA_DEFAULT_EXTERNAL_HTTP_TIMEOUT_MS;",
)


def main() -> int:
    if not TARGET.is_file():
        print(f"No se encontró el fuente fijado del motor: {TARGET}", file=sys.stderr)
        return 2

    source = TARGET.read_text(encoding="utf-8")
    if all(marker in source for marker in REQUIRED_MARKERS):
        print("La protección global HTTP de Rubrova ya está aplicada.")
        return 0

    # Do not apply a partial or fuzzy change: upstream drift must be reviewed.
    for before, _ in REPLACEMENTS:
        count = source.count(before)
        if count != 1:
            print(
                "No se aplicó el parche. Se esperaba exactamente una coincidencia "
                f"del ancla del fuente y se encontraron {count}: {before[:140]!r}",
                file=sys.stderr,
            )
            return 1

    for before, after in REPLACEMENTS:
        source = source.replace(before, after, 1)

    missing = [marker for marker in REQUIRED_MARKERS if marker not in source]
    if missing:
        print("El parche quedó incompleto: " + ", ".join(missing), file=sys.stderr)
        return 1

    TARGET.write_text(source, encoding="utf-8")
    print("Protección global HTTP aplicada: 10 s por defecto, 60 s máximo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
