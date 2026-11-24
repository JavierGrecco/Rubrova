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


CASH_ACCOUNT_TARGET = ROOT / "vendor/mycompany/src/main/lsfusion/retail/pos/PosPaymentMethod.lsf"
CASH_ACCOUNT_ANCHOR = "cashBalance 'Cash at the checkout' (Pos p) = balance(cashAccount(p));"
CASH_ACCOUNT_REQUIRED_MARKER = "CONSTRAINT account(Pos p) = cashAccount(p)"
CASH_ACCOUNT_REPLACEMENT = (
    CASH_ACCOUNT_ANCHOR
    + "\n\n"
    + "// Rubrova guard ported from the maintained MyCompany 6.x line. The central account\n"
    + "// is the counterparty for deposits/withdrawals and cannot also be the till drawer.\n"
    + "CONSTRAINT account(Pos p) = cashAccount(p)\n"
    + "                MESSAGE 'La cuenta central de caja no puede ser la misma que la cuenta de efectivo';"
)

# Backport from upstream MyCompany commit 9dca1499bd4e2615d34983fe77c2927560fd5f9b.
# APPLY is deliberately placed before NEWSESSION so dirty form values are committed
# before the action reads the document in a fresh session.
NEWSESSION_GUARD_TARGETS = (
    ("vendor/mycompany/src/main/lsfusion/inventory/receipts/Receipt.lsf", "copy 'Copy' (Receipt from) { "),
    ("vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptScrap.lsf", "scrap 'Scrap' (Receipt r) {"),
    ("vendor/mycompany/src/main/lsfusion/inventory/receipts/shipment/ReceiptShipment.lsf", "return 'Return' (Receipt r) {    "),
    ("vendor/mycompany/src/main/lsfusion/inventory/scraps/Scrap.lsf", "copy 'Copy' (Scrap s) {"),
    ("vendor/mycompany/src/main/lsfusion/inventory/shipments/Shipment.lsf", "copy 'Copy' (Shipment from)  { "),
    ("vendor/mycompany/src/main/lsfusion/inventory/shipments/receipt/ShipmentReceipt.lsf", "return 'Return' (Shipment s) {    "),
    ("vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf", "copy 'Copy' (Bill from)  { "),
    ("vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf", "copy 'Copy' (Invoice from)  { "),
    ("vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrder.lsf", "copy 'Copy' (Order from)  { "),
    ("vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf", "copy 'Copy' (Order from)  { "),
)

GWT_MESSAGES_SOURCE = ROOT / "patches/lsfusion/ClientMessages_es.properties"
GWT_MESSAGES_SOURCE = ROOT / "patches/lsfusion/ClientMessages_es.properties"
GWT_MESSAGES_TARGET = ROOT / "vendor/platform/web-client/src/main/java/lsfusion/gwt/client/ClientMessages_es.properties"



def apply_newsession_guards() -> bool:
    for relative_path, anchor in NEWSESSION_GUARD_TARGETS:
        target = ROOT / relative_path
        if not target.is_file():
            print(f"No se encontró el módulo MyCompany fijado: {target}", file=sys.stderr)
            return False

        source = target.read_text(encoding="utf-8")
        occurrences = source.count(anchor)
        if occurrences != 1:
            print(
                "No se aplicó la protección NEWSESSION. Se esperaba exactamente "
                f"una coincidencia en {relative_path} y se encontraron {occurrences}.",
                file=sys.stderr,
            )
            return False

        remainder = source[source.index(anchor) + len(anchor):].lstrip(" \t\r\n")
        expected_guard = "APPLY;\n    IF canceled() THEN RETURN;"
        if remainder.startswith("APPLY;"):
            if not remainder.startswith(expected_guard):
                print(
                    f"El guard NEWSESSION en {relative_path} existe pero difiere del esperado.",
                    file=sys.stderr,
                )
                return False
            continue

        if not remainder.startswith("NEWSESSION {"):
            print(
                f"El ancla de {relative_path} ya no abre NEWSESSION inmediatamente; "
                "requiere revisión manual.",
                file=sys.stderr,
            )
            return False

        insertion = "\n    APPLY;\n    IF canceled() THEN RETURN;"
        source = source.replace(anchor, anchor + insertion, 1)
        target.write_text(source, encoding="utf-8")
        print(f"Protección de cambios pendientes aplicada: {relative_path}")

    print(f"Protección NEWSESSION verificada en {len(NEWSESSION_GUARD_TARGETS)} módulos.")
    return True


def main() -> int:
    if not TARGET.is_file():
        print(f"No se encontró el fuente fijado del motor: {TARGET}", file=sys.stderr)
        return 2

    source = TARGET.read_text(encoding="utf-8")
    if not all(marker in source for marker in REQUIRED_MARKERS):
        # Do not apply a partial or fuzzy change: upstream drift must be reviewed.
        for before, _ in REPLACEMENTS:
            count = source.count(before)
            if count != 1:
                print(
                    "No se aplicó el parche HTTP. Se esperaba exactamente una coincidencia "
                    f"del ancla del fuente y se encontraron {count}: {before[:140]!r}",
                    file=sys.stderr,
                )
                return 1

        for before, after in REPLACEMENTS:
            source = source.replace(before, after, 1)

        missing = [marker for marker in REQUIRED_MARKERS if marker not in source]
        if missing:
            print("El parche HTTP quedó incompleto: " + ", ".join(missing), file=sys.stderr)
            return 1

        TARGET.write_text(source, encoding="utf-8")
        print("Protección global HTTP aplicada: 10 s por defecto, 60 s máximo.")
    else:
        print("La protección global HTTP de Rubrova ya está aplicada.")

    if not CASH_ACCOUNT_TARGET.is_file():
        print(f"No se encontró el módulo de caja de MyCompany: {CASH_ACCOUNT_TARGET}", file=sys.stderr)
        return 2

    cash_source = CASH_ACCOUNT_TARGET.read_text(encoding="utf-8")
    if CASH_ACCOUNT_REQUIRED_MARKER not in cash_source:
        count = cash_source.count(CASH_ACCOUNT_ANCHOR)
        if count != 1:
            print(
                "No se aplicó el control de cuentas de caja. Se esperaba exactamente "
                f"una coincidencia del ancla y se encontraron {count}.",
                file=sys.stderr,
            )
            return 1

        cash_source = cash_source.replace(CASH_ACCOUNT_ANCHOR, CASH_ACCOUNT_REPLACEMENT, 1)
        if CASH_ACCOUNT_REQUIRED_MARKER not in cash_source:
            print("El control de cuentas de caja quedó incompleto.", file=sys.stderr)
            return 1

        CASH_ACCOUNT_TARGET.write_text(cash_source, encoding="utf-8")
        print("Control de caja aplicado: cuenta central y cajón de efectivo deben ser distintos.")
    else:
        print("El control de cuentas de caja de Rubrova ya está aplicado.")

    if not apply_newsession_guards():
        return 1

    if not GWT_MESSAGES_SOURCE.is_file():
        print(f"No se encontró el glosario español del cliente GWT: {GWT_MESSAGES_SOURCE}", file=sys.stderr)
        return 2

    expected_messages = GWT_MESSAGES_SOURCE.read_text(encoding="utf-8")
    if GWT_MESSAGES_TARGET.exists():
        current_messages = GWT_MESSAGES_TARGET.read_text(encoding="utf-8")
        if current_messages != expected_messages:
            print(
                "El bundle español generado de GWT difiere de su fuente Rubrova; "
                "se detiene para evitar sobrescribir cambios.",
                file=sys.stderr,
            )
            return 1
        print("Traducciones españolas críticas del cliente GWT ya aplicadas.")
    else:
        GWT_MESSAGES_TARGET.parent.mkdir(parents=True, exist_ok=True)
        GWT_MESSAGES_TARGET.write_text(expected_messages, encoding="utf-8")
        print("Traducciones españolas críticas del cliente GWT aplicadas.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
