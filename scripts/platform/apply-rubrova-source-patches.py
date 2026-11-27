#!/usr/bin/env python3
"""Apply Rubrova compatibility and Spanish localization patches to pinned lsFusion/MyCompany sources."""

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
    ("vendor/mycompany/src/main/lsfusion/crm/leads/Lead.lsf", "copy 'Copy' (Lead from)  {"),
    ("vendor/mycompany/src/main/lsfusion/fleet/vehicles/service/VehicleService.lsf", "copy 'Copy' (VehicleService from)  {"),
    ("vendor/mycompany/src/main/lsfusion/inventory/receipts/Receipt.lsf", "copy 'Copy' (Receipt from) { "),
    ("vendor/mycompany/src/main/lsfusion/inventory/receipts/ReceiptScrap.lsf", "scrap 'Scrap' (Receipt r) {"),
    ("vendor/mycompany/src/main/lsfusion/inventory/receipts/shipment/ReceiptShipment.lsf", "return 'Return' (Receipt r) {    "),
    ("vendor/mycompany/src/main/lsfusion/inventory/scraps/Scrap.lsf", "copy 'Copy' (Scrap s) {"),
    ("vendor/mycompany/src/main/lsfusion/inventory/shipments/Shipment.lsf", "copy 'Copy' (Shipment from)  { "),
    ("vendor/mycompany/src/main/lsfusion/inventory/shipments/receipt/ShipmentReceipt.lsf", "return 'Return' (Shipment s) {    "),
    ("vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf", "copy 'Copy' (Bill from)  { "),
    ("vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf", "copy 'Copy' (Invoice from)  { "),
    ("vendor/mycompany/src/main/lsfusion/manufacturing/bom/Bom.lsf", "copy 'Copy' (Bom b) {"),
    ("vendor/mycompany/src/main/lsfusion/manufacturing/orders/ManufacturingOrder.lsf", "copy 'Copy' (ManufacturingOrder from) {"),
    ("vendor/mycompany/src/main/lsfusion/manufacturing/orders/scrap/ManufacturingOrderScrap.lsf", "scrap 'Scrap' (ManufacturingOrder o) {"),
    ("vendor/mycompany/src/main/lsfusion/masterdata/items/products/Product.lsf", "copy 'Copy' (Product p) {"),
    ("vendor/mycompany/src/main/lsfusion/masterdata/items/services/ServiceP.lsf", "copy 'Copy' (Service s) {"),
    ("vendor/mycompany/src/main/lsfusion/projectManagement/timeEntries/TimeEntry.lsf", "copy 'Copy' (TimeEntry from) {"),
    ("vendor/mycompany/src/main/lsfusion/purchase/orders/PurchaseOrder.lsf", "copy 'Copy' (Order from)  { "),
    ("vendor/mycompany/src/main/lsfusion/purchase/pricelists/PurchasePricelist.lsf", "copy 'Copy' (Pricelist pl) {"),
    ("vendor/mycompany/src/main/lsfusion/region/pl/invoicing/ksef/invoices/KSeFInvoiceSend.lsf", "sendToKSeF 'Wyślij do KSeF' (Invoice i) {"),
    ("vendor/mycompany/src/main/lsfusion/sales/orders/SalesOrder.lsf", "copy 'Copy' (Order from)  { "),
    ("vendor/mycompany/src/main/lsfusion/sales/pricelists/SalesPricelist.lsf", "copy 'Copy' (Pricelist pl) {"),
)

CASH_ACCOUNT_QUERIES_TARGET = ROOT / "vendor/mycompany/src/main/lsfusion/invoicing/accounts/cash/CashAccount.lsf"
CASH_ACCOUNT_QUERY_REPLACEMENTS = (
    (
        "calcDefaultCashAccount (Partner p) = GROUP LAST CashAccount a ORDER a WHERE holder(a) = p IF countCashAccount(p) = 1;",
        "calcDefaultCashAccount (Partner p) = GROUP LAST CashAccount a ORDER a WHERE a IS CashAccount AND holder(a) = p IF countCashAccount(p) = 1;",
    ),
    (
        "cashAccount (Employee e) = GROUP LAST CashAccount a ORDER a WHERE holder(a) = legalEntity(e) AND responsible(a) = e;",
        "cashAccount (Employee e) = GROUP LAST CashAccount a ORDER a WHERE a IS CashAccount AND holder(a) = legalEntity(e) AND responsible(a) = e;",
    ),
)

BANK_ACCOUNT_QUERIES_TARGET = ROOT / "vendor/mycompany/src/main/lsfusion/invoicing/accounts/bank/BankAccount.lsf"
BANK_ACCOUNT_QUERY_REPLACEMENTS = (
    (
        "calcDefaultBankAccount (Partner p) = GROUP LAST BankAccount a ORDER a WHERE holder(a) = p IF countBankAccount(p) = 1;",
        "calcDefaultBankAccount (Partner p) = GROUP LAST BankAccount a ORDER a WHERE a IS BankAccount AND holder(a) = p IF countBankAccount(p) = 1;",
    ),
)

# Literal captions bypass ResourceBundle lookup; use the existing localized key instead.
CASH_MOVEMENT_DATE_CAPTION_TARGETS = (
    (
        ROOT / "vendor/mycompany/src/main/lsfusion/invoicing/payments/incoming/IncomingPayment.lsf",
        "dateTime 'Date' = DATA DATETIME (IncomingPayment) NONULL IN id;",
        "dateTime '{Date}' = DATA DATETIME (IncomingPayment) NONULL IN id;",
    ),
    (
        ROOT / "vendor/mycompany/src/main/lsfusion/invoicing/payments/outgoing/OutgoingPayment.lsf",
        "dateTime 'Date' = DATA DATETIME (OutgoingPayment) NONULL IN id;",
        "dateTime '{Date}' = DATA DATETIME (OutgoingPayment) NONULL IN id;",
    ),
)

# MyCompany's item-attribute navigator caption is literal in the upstream file.
# Resolve it through the existing "Attributes" ResourceBundle key.
ITEM_ATTRIBUTE_NAVIGATION_TARGET = ROOT / "vendor/mycompany/src/main/lsfusion/masterdata/items/attributes/ItemAttribute.lsf"
ITEM_ATTRIBUTE_NAVIGATION_BEFORE = "FORM attributes 'Attributes'"
ITEM_ATTRIBUTE_NAVIGATION_AFTER = "FORM attributes '{Attributes}'"

# The Markdown renderer is a documentation-only feature. Never load its CDN
# dependencies in SystemEvents.onWebClientLoad, which runs during POS startup.
MARKDOWN_VIEWER_TARGET = ROOT / "vendor/mycompany/src/main/lsfusion/utils/MarkdownViewer.lsf"
MARKDOWN_VIEWER_CDN_BLOCK = """onWebClientLoad() + {
    INTERNAL CLIENT WAIT r'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
    INTERNAL CLIENT WAIT r'https://cdn.jsdelivr.net/npm/marked-gfm-heading-id/lib/index.umd.js';
}"""
MARKDOWN_VIEWER_SHOW_ANCHOR = """showMarkdownResourceViewer(STRING caption, STRING file) {
    NEWSESSION {"""
MARKDOWN_VIEWER_SHOW_LAZY = """showMarkdownResourceViewer(STRING caption, STRING file) {
    // Markdown is only needed when a user opens Documentation, never to start POS.
    INTERNAL CLIENT WAIT r'https://cdn.jsdelivr.net/npm/marked@18.3.0/lib/marked.umd.js';
    INTERNAL CLIENT WAIT r'https://cdn.jsdelivr.net/npm/marked-gfm-heading-id@4.1.4/lib/index.umd.js';
    NEWSESSION {"""
MARKDOWN_VIEWER_REQUIRED_MARKERS = (
    "marked@18.3.0/lib/marked.umd.js",
    "marked-gfm-heading-id@4.1.4/lib/index.umd.js",
)

# Preserve the distinction between an empty adjustment-list group and a group whose
# recorded quantities sum to zero. In lsFusion, GROUP SUM returns NULL for a zero sum.
STOCKTAKE_LIST_TARGET = ROOT / "vendor/mycompany/src/main/lsfusion/inventory/adjustments/lists/AdjustmentList.lsf"
STOCKTAKE_LIST_AGGREGATE_BEFORE = """listRealQuantity (Adjustment, Product, Location) = 
    GROUP SUM realQuantity(AdjustmentListLine l) BY adjustment(adjustmentList(l)), product(l), location(l);"""
STOCKTAKE_LIST_AGGREGATE_AFTER = """listRealQuantitySum (Adjustment, Product, Location) =
    GROUP SUM realQuantity(AdjustmentListLine l) BY adjustment(adjustmentList(l)), product(l), location(l);

listRealQuantityZeroFallback (Adjustment, Product, Location) =
    GROUP MAX 0.000 IF realQuantity(AdjustmentListLine l)
        BY adjustment(adjustmentList(l)), product(l), location(l);

listRealQuantity (Adjustment a, Product p, Location loc) =
    (OVERRIDE listRealQuantitySum(a, p, loc), listRealQuantityZeroFallback(a, p, loc));"""
STOCKTAKE_LIST_AGGREGATE_MARKERS = (
    "listRealQuantitySum (Adjustment, Product, Location) =",
    "GROUP MAX 0.000 IF realQuantity(AdjustmentListLine l)",
    "listRealQuantity (Adjustment a, Product p, Location loc) =",
    "(OVERRIDE listRealQuantitySum(a, p, loc), listRealQuantityZeroFallback(a, p, loc))",
    "WHEN SETCHANGED(listRealQuantity(Adjustment a, Product p, Location l))",
)


# MyCompany's refund dialog compares each payment method only with the original
# invoice payment. Rubrova adds a global cumulative cap over active native outgoings
# and requests serializable isolation for the native payment confirmation.
RETURN_PAYMENT_TARGET = ROOT / "vendor/mycompany/src/main/lsfusion/retail/pos/dashboard/return/PosDashboardReturnPayment.lsf"
RETURN_PAYMENT_REQUIRE_BEFORE = "REQUIRE PosDashboardReturn, PosDashboardPayment, CreditNote, OutgoingPaymentDone;"
RETURN_PAYMENT_REQUIRE_AFTER = "REQUIRE PosDashboardReturn, PosDashboardPayment, CreditNote, OutgoingPaymentDone, RubrovaRetailRefundLimits;"
RETURN_PAYMENT_INVALID_BEFORE = "invalidAmount(Bill b, PaymentMethod pm) = amount(pm) > OVERRIDE invoicePaid(b, pm), 0.0;"
RETURN_PAYMENT_INVALID_AFTER = "invalidAmount(Bill b, PaymentMethod pm) = amount(pm) > rubrovaRefundRemaining(b, pm);"
RETURN_PAYMENT_FORM_BEFORE = "PROPERTIES name(pm) READONLY, invoicePaid(b, pm), amount(pm) BACKGROUND invalidAmount(b, pm)"
RETURN_PAYMENT_FORM_AFTER = "PROPERTIES name(pm) READONLY, rubrovaOriginalPaidForReturn(b, pm), rubrovaRefundRemaining(b, pm), amount(pm) BACKGROUND invalidAmount(b, pm)"
RETURN_PAYMENT_DESIGN_BEFORE = "PROPERTY(invoicePaid(b, pm)) { fontSize = 24; }"
RETURN_PAYMENT_DESIGN_AFTER = chr(10).join((
    "PROPERTY(rubrovaOriginalPaidForReturn(b, pm)) { fontSize = 24; }",
    "                        PROPERTY(rubrovaRefundRemaining(b, pm)) { fontSize = 24; }",
))
RETURN_PAYMENT_APPLY_BEFORE = """ready(b) <- TRUE;
        APPLY;
        IF canceled() THEN {"""
RETURN_PAYMENT_APPLY_AFTER = """ready(b) <- TRUE;
        APPLY SERIALIZABLE;
        IF canceled() THEN {"""


# Backport from upstream MyCompany v6 commit ade105058457bf9ab38aa4ab90b958bf73b5a7fb.
# Tax changes are part of the document-line audit trail, alongside quantity and amount.
TAX_HISTORY_TARGETS = (
    (
        ROOT / "vendor/mycompany/src/main/lsfusion/invoicing/bills/Bill.lsf",
        "@defineDocHistoryLineProperty(bill, BillLine, untaxedAmount, '{Amount}', nameItem);",
        "@defineDocHistoryLineProperty(bill, BillLine, taxes, 'Taxes', nameItem);",
    ),
    (
        ROOT / "vendor/mycompany/src/main/lsfusion/invoicing/invoices/Invoice.lsf",
        "@defineDocHistoryLineProperty(invoice, InvoiceLine, untaxedAmount, '{Amount}', nameItem);",
        "@defineDocHistoryLineProperty(invoice, InvoiceLine, taxes, 'Taxes', nameItem);",
    ),
)

RMI_SERVER_SOCKET_TARGET = ROOT / "vendor/platform/api/src/main/java/lsfusion/base/remote/ZipServerSocket.java"
RMI_SERVER_SOCKET_BEFORE = """    public ZipServerSocket(int port) throws IOException {
        super(port, 500);
    }"""
RMI_SERVER_SOCKET_AFTER = """    public ZipServerSocket(int port) throws IOException {
        super();
        String bindAddress = System.getProperty("lsfusion.rmi.bindAddress");
        if (bindAddress == null || bindAddress.trim().isEmpty()) {
            bind(new InetSocketAddress(port), 500);
        } else {
            bind(new InetSocketAddress(InetAddress.getByName(bindAddress.trim()), port), 500);
        }
    }"""
RMI_SERVER_SOCKET_MARKER = 'System.getProperty("lsfusion.rmi.bindAddress")'


def apply_rmi_server_bind_address() -> bool:
    target = RMI_SERVER_SOCKET_TARGET
    if not target.is_file():
        print(f"No se encontró el socket RMI fijado del motor: {target}", file=sys.stderr)
        return False

    source = target.read_text(encoding="utf-8")
    if RMI_SERVER_SOCKET_MARKER in source:
        required = (
            "new InetSocketAddress(port), 500",
            "InetAddress.getByName(bindAddress.trim())",
        )
        missing = [marker for marker in required if marker not in source]
        if missing:
            print("El parche de bind RMI existe pero difiere del esperado: " + ", ".join(missing), file=sys.stderr)
            return False
        print("Configuración de bind RMI por interfaz ya aplicada.")
        return True

    count = source.count(RMI_SERVER_SOCKET_BEFORE)
    if count != 1:
        print(
            "No se aplicó el bind RMI. Se esperaba exactamente una coincidencia "
            f"del constructor original y se encontraron {count}.",
            file=sys.stderr,
        )
        return False

    source = source.replace(RMI_SERVER_SOCKET_BEFORE, RMI_SERVER_SOCKET_AFTER, 1)
    if RMI_SERVER_SOCKET_MARKER not in source:
        print("El parche de bind RMI quedó incompleto.", file=sys.stderr)
        return False

    imports = "import java.io.IOException;\nimport java.net.ServerSocket;"
    updated_imports = (
        "import java.io.IOException;\n"
        "import java.net.InetAddress;\n"
        "import java.net.InetSocketAddress;\n"
        "import java.net.ServerSocket;"
    )
    if source.count(imports) != 1:
        print("No se encontraron los imports originales esperados en ZipServerSocket.java.", file=sys.stderr)
        return False
    source = source.replace(imports, updated_imports, 1)

    target.write_text(source, encoding="utf-8")
    print("Bind RMI configurable aplicado: el modo nativo puede limitar el socket a loopback.")
    return True


GWT_MESSAGES_SOURCE = ROOT / "patches/lsfusion/ClientMessages_es.properties"
GWT_MESSAGES_TARGET = ROOT / "vendor/platform/web-client/src/main/java/lsfusion/gwt/client/ClientMessages_es.properties"
SERVER_MESSAGES_SOURCE = ROOT / "patches/lsfusion/ServerResourceBundle_es.properties"
SERVER_MESSAGES_TARGET = ROOT / "vendor/platform/server/src/main/resources/ServerResourceBundle_es.properties"
SERVER_TEXT_MESSAGES_SOURCE = ROOT / "patches/lsfusion/ServerMessages_es.properties"
SERVER_TEXT_MESSAGES_TARGET = ROOT / "vendor/platform/web-client/src/main/resources/ServerMessages_es.properties"




def apply_cash_account_query_filters() -> bool:
    if not CASH_ACCOUNT_QUERIES_TARGET.is_file():
        print(f"No se encontró el módulo CashAccount: {CASH_ACCOUNT_QUERIES_TARGET}", file=sys.stderr)
        return False

    source = CASH_ACCOUNT_QUERIES_TARGET.read_text(encoding="utf-8")
    changed = False
    for before, after in CASH_ACCOUNT_QUERY_REPLACEMENTS:
        if after in source:
            continue
        count = source.count(before)
        if count != 1:
            print(
                "No se aplicó el filtro CashAccount. Se esperaba exactamente "
                f"una coincidencia y se encontraron {count}: {before}",
                file=sys.stderr,
            )
            return False
        source = source.replace(before, after, 1)
        changed = True

    if changed:
        CASH_ACCOUNT_QUERIES_TARGET.write_text(source, encoding="utf-8")
        print("Filtros de clase CashAccount aplicados en las dos búsquedas de cuenta.")
    else:
        print("Filtros de clase CashAccount ya aplicados.")
    return True



def apply_bank_account_query_filters() -> bool:
    if not BANK_ACCOUNT_QUERIES_TARGET.is_file():
        print(f"No se encontró el módulo BankAccount: {BANK_ACCOUNT_QUERIES_TARGET}", file=sys.stderr)
        return False

    source = BANK_ACCOUNT_QUERIES_TARGET.read_text(encoding="utf-8")
    changed = False
    for before, after in BANK_ACCOUNT_QUERY_REPLACEMENTS:
        if after in source:
            continue
        count = source.count(before)
        if count != 1:
            print(
                "No se aplicó el filtro BankAccount. Se esperaba exactamente "
                f"una coincidencia y se encontraron {count}: {before}",
                file=sys.stderr,
            )
            return False
        source = source.replace(before, after, 1)
        changed = True

    if changed:
        BANK_ACCOUNT_QUERIES_TARGET.write_text(source, encoding="utf-8")
        print("Filtro de clase BankAccount aplicado.")
    else:
        print("Filtro de clase BankAccount ya aplicado.")
    return True


def apply_item_attribute_navigation_caption() -> bool:
    target = ITEM_ATTRIBUTE_NAVIGATION_TARGET
    if not target.is_file():
        print(f"No se encontró el módulo de atributos: {target}", file=sys.stderr)
        return False

    source = target.read_text(encoding="utf-8")
    if ITEM_ATTRIBUTE_NAVIGATION_AFTER in source:
        print("Caption de navegación Atributos ya localizado.")
        return True

    count = source.count(ITEM_ATTRIBUTE_NAVIGATION_BEFORE)
    if count != 1:
        print(
            "No se localizó el caption literal de atributos. Se esperaba exactamente "
            f"una coincidencia en {target} y se encontraron {count}.",
            file=sys.stderr,
        )
        return False

    source = source.replace(
        ITEM_ATTRIBUTE_NAVIGATION_BEFORE,
        ITEM_ATTRIBUTE_NAVIGATION_AFTER,
        1,
    )
    target.write_text(source, encoding="utf-8")
    print("Caption de navegación Atributos localizado.")
    return True


def apply_markdown_viewer_lazy_load() -> bool:
    target = MARKDOWN_VIEWER_TARGET
    if not target.is_file():
        print(f"No se encontró el visor Markdown de MyCompany: {target}", file=sys.stderr)
        return False

    source = target.read_text(encoding="utf-8")
    if all(marker in source for marker in MARKDOWN_VIEWER_REQUIRED_MARKERS):
        if MARKDOWN_VIEWER_CDN_BLOCK in source or "onWebClientLoad() +" in source:
            print(
                "El visor Markdown conserva una carga global aunque las URL estén fijadas.",
                file=sys.stderr,
            )
            return False
        print("Dependencias Markdown fijadas y cargadas bajo demanda.")
        return True

    remote_count = source.count(MARKDOWN_VIEWER_CDN_BLOCK)
    action_count = source.count(MARKDOWN_VIEWER_SHOW_ANCHOR)
    if remote_count != 1 or action_count != 1:
        print(
            "No se aisló la dependencia Markdown. Se esperaba exactamente una carga "
            f"global y una acción pública; se encontraron {remote_count} y {action_count}.",
            file=sys.stderr,
        )
        return False

    updated = source.replace(MARKDOWN_VIEWER_CDN_BLOCK, "", 1)
    updated = updated.replace(MARKDOWN_VIEWER_SHOW_ANCHOR, MARKDOWN_VIEWER_SHOW_LAZY, 1)
    missing = [marker for marker in MARKDOWN_VIEWER_REQUIRED_MARKERS if marker not in updated]
    if missing or "onWebClientLoad() +" in updated:
        print(
            "El cambio de carga diferida del visor Markdown quedó incompleto: "
            + ", ".join(missing or ["onWebClientLoad() sigue presente"]),
            file=sys.stderr,
        )
        return False

    target.write_text(updated, encoding="utf-8")
    print("Visor Markdown aislado: sus dependencias se descargan sólo al abrir Documentación.")
    return True


def apply_cash_movement_date_captions() -> bool:
    for target, before, after in CASH_MOVEMENT_DATE_CAPTION_TARGETS:
        if not target.is_file():
            print(f"No se encontró el módulo de pagos: {target}", file=sys.stderr)
            return False

        source = target.read_text(encoding="utf-8")
        if after in source:
            continue

        count = source.count(before)
        if count != 1:
            print(
                "No se corrigió el caption Date de movimientos de caja. Se esperaba "
                f"exactamente una coincidencia en {target} y se encontraron {count}.",
                file=sys.stderr,
            )
            return False

        source = source.replace(before, after, 1)
        target.write_text(source, encoding="utf-8")
        print(f"Caption de fecha localizado al español: {target.name}")

    print("Captions de fecha de ingresos y retiros verificados.")
    return True


def apply_stocktake_list_zero_aware_aggregate() -> bool:
    target = STOCKTAKE_LIST_TARGET
    if not target.is_file():
        print(f"No se encontró el módulo de hojas de inventario: {target}", file=sys.stderr)
        return False

    source = target.read_text(encoding="utf-8")
    missing = [marker for marker in STOCKTAKE_LIST_AGGREGATE_MARKERS if marker not in source]
    if not missing and STOCKTAKE_LIST_AGGREGATE_BEFORE not in source:
        print("El agregado nativo de conteo conserva cero y NULL sin confundir grupos vacíos.")
        return True

    if STOCKTAKE_LIST_AGGREGATE_AFTER in source:
        print("El parche de agregado de conteo existe, pero faltan marcadores esperados.", file=sys.stderr)
        return False

    occurrences = source.count(STOCKTAKE_LIST_AGGREGATE_BEFORE)
    if occurrences != 1:
        print(
            "No se ajustó el agregado de hojas de inventario. Se esperaba exactamente "
            f"una coincidencia del agregado upstream y se encontraron {occurrences}.",
            file=sys.stderr,
        )
        return False

    source = source.replace(
        STOCKTAKE_LIST_AGGREGATE_BEFORE,
        STOCKTAKE_LIST_AGGREGATE_AFTER,
        1,
    )
    missing = [marker for marker in STOCKTAKE_LIST_AGGREGATE_MARKERS if marker not in source]
    if missing or STOCKTAKE_LIST_AGGREGATE_BEFORE in source:
        print(
            "El parche de agregado cero/NULL de AdjustmentList quedó incompleto: "
            + ", ".join(missing or ["el agregado upstream original sigue presente"]),
            file=sys.stderr,
        )
        return False

    target.write_text(source, encoding="utf-8")
    print("Agregado nativo de AdjustmentList corregido: cero presente y grupo vacío NULL.")
    return True




def apply_cumulative_refund_guard() -> bool:
    target = RETURN_PAYMENT_TARGET
    if not target.is_file():
        print(f"No se encontró el flujo nativo de reintegros POS: {target}", file=sys.stderr)
        return False

    source = target.read_text(encoding="utf-8")
    require_occurrences = source.count(RETURN_PAYMENT_REQUIRE_AFTER)
    require_changed = False
    if require_occurrences == 0:
        require_before_count = source.count(RETURN_PAYMENT_REQUIRE_BEFORE)
        if require_before_count != 1:
            print(
                "No se declaró la dependencia del guard de reintegros en PosDashboardReturnPayment. "
                f"Se esperaba exactamente una REQUIRE original y se encontraron {require_before_count}.",
                file=sys.stderr,
            )
            return False
        source = source.replace(RETURN_PAYMENT_REQUIRE_BEFORE, RETURN_PAYMENT_REQUIRE_AFTER, 1)
        require_changed = True
    elif require_occurrences != 1 or RETURN_PAYMENT_REQUIRE_BEFORE in source:
        print(
            "La dependencia del guard de reintegros existe duplicada o conserva la REQUIRE original.",
            file=sys.stderr,
        )
        return False

    replacements = (
        (RETURN_PAYMENT_INVALID_BEFORE, RETURN_PAYMENT_INVALID_AFTER),
        (RETURN_PAYMENT_FORM_BEFORE, RETURN_PAYMENT_FORM_AFTER),
        (RETURN_PAYMENT_DESIGN_BEFORE, RETURN_PAYMENT_DESIGN_AFTER),
        (RETURN_PAYMENT_APPLY_BEFORE, RETURN_PAYMENT_APPLY_AFTER),
    )
    required = tuple(after for _, after in replacements)
    if all(marker in source for marker in required):
        if RETURN_PAYMENT_DESIGN_BEFORE in source:
            print("El diseño del diálogo conserva la propiedad retirada del formulario.", file=sys.stderr)
            return False
        if require_changed:
            target.write_text(source, encoding="utf-8")
        print("Tope acumulado por medio, dependencia nativa y confirmación SERIALIZABLE ya aplicados al reintegro.")
        return True

    for before, after in replacements:
        if after in source:
            print(
                "El parche del tope acumulado quedó parcialmente aplicado; "
                "se detiene para evitar una reparación por sustitución ambigua.",
                file=sys.stderr,
            )
            return False
        count = source.count(before)
        if count != 1:
            print(
                "No se aplicó el tope acumulado de reintegros. Se esperaba exactamente "
                f"una coincidencia en {target.name} y se encontraron {count}: {before[:120]!r}",
                file=sys.stderr,
            )
            return False

    for before, after in replacements:
        source = source.replace(before, after, 1)

    missing = [marker for marker in required if marker not in source]
    if missing:
        print("El parche de reintegros quedó incompleto: " + ", ".join(missing), file=sys.stderr)
        return False

    target.write_text(source, encoding="utf-8")
    print("Reintegros POS protegidos: cupo por medio acumulado y APPLY SERIALIZABLE.")
    return True

def apply_tax_history_line_tracking() -> bool:
    for target, anchor, replacement in TAX_HISTORY_TARGETS:
        if not target.is_file():
            print(f"No se encontró el módulo documental: {target}", file=sys.stderr)
            return False

        source = target.read_text(encoding="utf-8")
        if replacement in source:
            continue

        count = source.count(anchor)
        if count != 1:
            print(
                "No se incorporó el historial de impuestos. Se esperaba exactamente "
                f"una coincidencia en {target} y se encontraron {count}.",
                file=sys.stderr,
            )
            return False

        source = source.replace(anchor, anchor + "\n" + replacement, 1)
        target.write_text(source, encoding="utf-8")
        print(f"Historial de impuestos por línea aplicado: {target.name}")

    print(f"Historial de impuestos verificado en {len(TAX_HISTORY_TARGETS)} documentos.")
    return True


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
    if not apply_rmi_server_bind_address():
        return 1

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

    if not apply_stocktake_list_zero_aware_aggregate():
        return 1

    if not apply_cumulative_refund_guard():
        return 1

    if not apply_cash_account_query_filters():
        return 1

    if not apply_bank_account_query_filters():
        return 1

    if not apply_tax_history_line_tracking():
        return 1

    if not apply_cash_movement_date_captions():
        return 1

    if not apply_item_attribute_navigation_caption():
        return 1

    if not apply_markdown_viewer_lazy_load():
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

    if not SERVER_MESSAGES_SOURCE.is_file():
        print(f"No se encontró el paquete español del servidor: {SERVER_MESSAGES_SOURCE}", file=sys.stderr)
        return 2

    expected_server_messages = SERVER_MESSAGES_SOURCE.read_text(encoding="utf-8")
    if SERVER_MESSAGES_TARGET.exists():
        current_server_messages = SERVER_MESSAGES_TARGET.read_text(encoding="utf-8")
        if current_server_messages != expected_server_messages:
            print(
                "El paquete español del servidor difiere de su fuente Rubrova; "
                "se detiene para evitar sobrescribir cambios.",
                file=sys.stderr,
            )
            return 1
        print("Traducciones españolas críticas del servidor ya aplicadas.")
    else:
        SERVER_MESSAGES_TARGET.parent.mkdir(parents=True, exist_ok=True)
        SERVER_MESSAGES_TARGET.write_text(expected_server_messages, encoding="utf-8")
        print("Traducciones españolas críticas del servidor aplicadas.")

    if not SERVER_TEXT_MESSAGES_SOURCE.is_file():
        print(f"No se encontró el glosario español del acceso web: {SERVER_TEXT_MESSAGES_SOURCE}", file=sys.stderr)
        return 2

    expected_text_messages = SERVER_TEXT_MESSAGES_SOURCE.read_text(encoding="utf-8")
    if SERVER_TEXT_MESSAGES_TARGET.exists():
        current_text_messages = SERVER_TEXT_MESSAGES_TARGET.read_text(encoding="utf-8")
        if current_text_messages != expected_text_messages:
            print(
                "El glosario español del acceso web difiere de su fuente Rubrova; "
                "se detiene para evitar sobrescribir cambios.",
                file=sys.stderr,
            )
            return 1
        print("Traducciones españolas de acceso web ya aplicadas.")
    else:
        SERVER_TEXT_MESSAGES_TARGET.parent.mkdir(parents=True, exist_ok=True)
        SERVER_TEXT_MESSAGES_TARGET.write_text(expected_text_messages, encoding="utf-8")
        print("Traducciones españolas de acceso web aplicadas.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
