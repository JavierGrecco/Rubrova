#!/usr/bin/env python3
"""Read-only browser inspection for the isolated MyCompany runtime smoke test."""

from __future__ import annotations

import json
import math
from concurrent.futures import ThreadPoolExecutor
import os
from decimal import Decimal, InvalidOperation
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from native_runtime_url import application_endpoint_url

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


NATIVE_EXPORT_SCHEMA_VERSION = 2


SERVER_ERROR_MARKERS = (
    "AppServerNotAvailableDispatchException",
    "Application server [",
    "Connection refused",
    "NotBoundException",
)


def attach_browser_diagnostics(page: Any) -> dict[str, list[dict[str, Any]]]:
    """Collect concise browser-side evidence without changing the application."""
    diagnostics: dict[str, list[dict[str, Any]]] = {
        "page_errors": [],
        "console_errors": [],
        "failed_requests": [],
        "markdown_requests": [],
        "http_errors": [],
        "dispatch_responses": [],
    }
    dispatch_started: dict[int, float] = {}

    def remember(category: str, item: dict[str, Any]) -> None:
        bucket = diagnostics[category]
        bucket.append(item)
        if len(bucket) > 30:
            del bucket[:-30]

    def on_page_error(error: Any) -> None:
        remember("page_errors", {"message": str(error)[:1200]})

    def on_console(message: Any) -> None:
        if message.type == "error":
            remember("console_errors", {"message": str(message.text)[:1200]})

    def on_request(request: Any) -> None:
        if "cdn.jsdelivr.net/npm/marked" in request.url:
            remember("markdown_requests", {
                "method": request.method,
                "url": request.url.split("?", 1)[0][:500],
            })
        if request.method.upper() == "POST" and "/dispatch" in request.url:
            dispatch_started[id(request)] = time.monotonic()

    def on_response(response: Any) -> None:
        request = response.request
        request_url = request.url.split("?", 1)[0]
        if response.status >= 400:
            remember("http_errors", {
                "status": response.status,
                "method": request.method,
                "url": request_url[:500],
            })
        if request.method.upper() == "POST" and "/dispatch" in request.url:
            started = dispatch_started.pop(id(request), None)
            remember("dispatch_responses", {
                "status": response.status,
                "elapsed_seconds": round(time.monotonic() - started, 3) if started else None,
                "content_length": response.headers.get("content-length", ""),
                "url": request_url[:500],
            })

    def on_request_failed(request: Any) -> None:
        request_url = request.url.split("?", 1)[0]
        failure = request.failure
        remember("failed_requests", {
            "method": request.method,
            "url": request_url[:500],
            "failure": str(failure or "unknown")[:500],
        })
        dispatch_started.pop(id(request), None)

    page.on("pageerror", on_page_error)
    page.on("console", on_console)
    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)
    return diagnostics


def emit_browser_diagnostics(
    page: Any,
    diagnostics: dict[str, list[dict[str, Any]]],
    label: str,
    screenshot_path: Path | None = None,
) -> None:
    """Write the browser's last known state even when the UI smoke aborts."""
    try:
        print(f"{label}_URL={page.url}")
    except PlaywrightError as error:
        print(f"{label}_URL_UNAVAILABLE={str(error)[:500]}")
    try:
        print(f"{label}_READY_STATE={page.evaluate('() => document.readyState')}")
    except PlaywrightError as error:
        print(f"{label}_READY_STATE_UNAVAILABLE={str(error)[:500]}")
    try:
        body_text = page.locator("body").inner_text(timeout=3_000)
        print(f"{label}_BODY_TEXT={body_text.strip()[:2500]}")
    except PlaywrightError as error:
        print(f"{label}_BODY_TEXT_UNAVAILABLE={str(error)[:500]}")
    for category, entries in diagnostics.items():
        print(f"{label}_{category.upper()}=" + json.dumps(entries[-20:], ensure_ascii=False))
    if screenshot_path is not None:
        try:
            page.screenshot(path=str(screenshot_path), full_page=True, timeout=5_000)
            print(f"{label}_SCREENSHOT={screenshot_path}")
        except PlaywrightError as error:
            print(f"{label}_SCREENSHOT_FAILED={str(error)[:500]}")


def visible_snapshot(page: Any, label: str) -> str:
    title = page.title()
    body_text = page.locator("body").inner_text(timeout=10_000)
    input_data: list[dict[str, Any]] = page.locator("input").evaluate_all(
        """elements => elements.slice(0, 40).map(element => ({
            type: element.type || "",
            name: element.name || "",
            id: element.id || "",
            placeholder: element.placeholder || "",
            value: element.value || "",
            title: element.getAttribute("title") || "",
            ariaLabel: element.getAttribute("aria-label") || "",
            visible: !!(element.offsetWidth || element.offsetHeight)
        }))"""
    )
    selectors = page.locator("select, [role=combobox], [role=listbox]").evaluate_all(
        """elements => elements.slice(0, 40).map(element => ({
            tag: element.tagName.toLowerCase(),
            value: "value" in element ? element.value || "" : "",
            text: (element.innerText || element.textContent || "").trim(),
            title: element.getAttribute("title") || "",
            ariaLabel: element.getAttribute("aria-label") || "",
            selectedText: element.tagName === "SELECT" && element.selectedOptions.length
                ? element.selectedOptions[0].textContent.trim()
                : "",
            options: Array.from(element.options || []).map(option => (option.textContent || "").trim()),
            visible: !!(element.offsetWidth || element.offsetHeight)
        }))"""
    )
    buttons = page.locator("button, input[type=submit], [role=button]").evaluate_all(
        """elements => elements.slice(0, 60).map(element => ({
            text: (element.innerText || element.value || element.textContent || "").trim(),
            type: element.type || "",
            ariaLabel: element.getAttribute("aria-label") || "",
            visible: !!(element.offsetWidth || element.offsetHeight)
        }))"""
    )
    links = page.locator("a").evaluate_all(
        """elements => elements.slice(0, 40).map(element => ({
            text: (element.innerText || element.textContent || "").trim(),
            href: element.getAttribute("href") || ""
        }))"""
    )
    alerts = page.locator(
        '[role="alert"], [role="status"], [class*="alert"], [class*="notification"], [class*="error"]'
    ).evaluate_all(
        """elements => elements.slice(0, 40).map(element => ({
            text: (element.innerText || element.textContent || "").trim(),
            className: typeof element.className === "string" ? element.className : "",
            role: element.getAttribute("role") || "",
            title: element.getAttribute("title") || "",
            ariaLabel: element.getAttribute("aria-label") || "",
            visible: !!(element.offsetWidth || element.offsetHeight)
        }))"""
    )

    print(f"{label}_TITLE={title}")
    print(f"{label}_URL={page.url}")
    print(f"{label}_BODY_TEXT_LENGTH={len(body_text.strip())}")
    print(f"{label}_VISIBLE_TEXT_BEGIN")
    print(body_text.strip()[:4500])
    print(f"{label}_VISIBLE_TEXT_END")
    print(f"{label}_INPUTS=" + json.dumps(input_data, ensure_ascii=False))
    print(f"{label}_SELECTORS=" + json.dumps(selectors, ensure_ascii=False))
    print(f"{label}_BUTTONS=" + json.dumps(buttons, ensure_ascii=False))
    print(f"{label}_LINKS=" + json.dumps(links, ensure_ascii=False))
    print(f"{label}_ALERTS=" + json.dumps(alerts, ensure_ascii=False))
    return body_text


def has_server_error(text: str) -> bool:
    return any(marker in text for marker in SERVER_ERROR_MARKERS)


def wait_for_application_server(page: Any) -> str:
    timeout_seconds = int(os.environ.get("RUBROVA_UI_READY_TIMEOUT_SECONDS", "180"))
    deadline = time.monotonic() + timeout_seconds
    attempts = 0
    last_text = ""

    while time.monotonic() < deadline:
        last_text = page.locator("body").inner_text(timeout=10_000)
        if (
            not has_server_error(last_text)
            and page.locator("#username").is_visible()
            and page.locator("#password").is_visible()
        ):
            print(f"UI_APPLICATION_SERVER_READY=true; reloads={attempts}")
            return last_text

        if attempts == 0:
            print("UI_APPLICATION_SERVER_READY=false; el login todavía muestra el estado de arranque.")
        attempts += 1
        page.wait_for_timeout(2_000)
        response = page.reload(wait_until="domcontentloaded", timeout=60_000)
        if response is not None and response.status >= 400:
            raise RuntimeError(
                f"La recarga de la pantalla de acceso respondió HTTP {response.status}."
            )

    raise RuntimeError(
        "El servidor RMI todavía no publicó su RemoteLogicsLoader después de "
        f"{timeout_seconds}s. Último texto visible: {last_text.strip()[:1600]}"
    )


def login_to_ephemeral_instance(page: Any) -> str:
    username = os.environ.get("RUBROVA_UI_TEST_USERNAME", "admin")
    password = os.environ.get("RUBROVA_UI_TEST_PASSWORD", "")

    username_field = page.locator("#username")
    password_field = page.locator("#password")
    submit_field = page.locator('input[type="submit"]')

    if not username_field.is_visible() or not password_field.is_visible():
        raise RuntimeError("No se encontró el formulario esperado de acceso MyCompany.")
    if not submit_field.is_visible():
        raise RuntimeError("No se encontró el botón de acceso del formulario MyCompany.")

    username_field.fill(username)
    password_field.fill(password)
    # lsFusion completes authentication through an asynchronous GWT flow.
    # Do not make Playwright wait for a full-page navigation after the click.
    submit_field.click(no_wait_after=True)
    print("UI_LOGIN_SUBMIT_CLICKED=true")

    # The browser navigates to /main after the asynchronous lsFusion login.
    # Wait for that transition explicitly, but keep polling if it takes longer.
    try:
        page.wait_for_url("**/main", timeout=30_000)
        print("UI_LOGIN_NAVIGATION_STATUS=main")
    except PlaywrightTimeoutError:
        print("UI_LOGIN_NAVIGATION_STATUS=still-waiting")

    deadline = time.monotonic() + 60
    last_text = ""
    while time.monotonic() < deadline:
        page.wait_for_timeout(1_000)
        try:
            last_text = page.locator("body").inner_text(timeout=5_000)
        except PlaywrightError:
            # The body can be temporarily unavailable while GWT replaces the page.
            continue

        try:
            login_visible = username_field.is_visible()
        except PlaywrightError:
            login_visible = False

        if not login_visible and not has_server_error(last_text) and last_text.strip():
            # Require the authenticated page to remain stable for another second.
            page.wait_for_timeout(1_000)
            try:
                stable_text = page.locator("body").inner_text(timeout=5_000)
                login_still_visible = page.locator("#username").is_visible()
            except PlaywrightError:
                continue
            if (
                not login_still_visible
                and not has_server_error(stable_text)
                and stable_text.strip()
            ):
                print("UI_LOGIN_BODY_STABLE=true")
                return stable_text

    raise RuntimeError(
        "No se pudo completar el acceso a la instancia efímera con "
        f"{username!r}. Texto visible: {last_text.strip()[:1600]}"
    )


def wait_until_form_loaded(
    page: Any,
    label: str,
    timeout_seconds: int = 45,
    *,
    register_name: str = "Caja de prueba Rubrova",
) -> str:
    deadline = time.monotonic() + timeout_seconds
    stable_reads = 0
    last_state: dict[str, Any] = {"text": "", "searchable": "", "selectors": [], "actions": []}

    while time.monotonic() < deadline:
        try:
            last_state = page.evaluate(
                """() => {
                    const visible = element => {
                        const style = getComputedStyle(element);
                        return style.display !== "none" && style.visibility !== "hidden" &&
                            !!(element.offsetWidth || element.offsetHeight);
                    };
                    const selectors = [...document.querySelectorAll(
                        'input, select, [role="combobox"], [role="listbox"], [role="option"]'
                    )].map(element => ({
                        tag: element.tagName.toLowerCase(),
                        id: element.id || "",
                        checked: element instanceof HTMLInputElement && element.type === "radio"
                            ? element.checked
                            : null,
                        value: "value" in element ? element.value || "" : "",
                        text: (element.innerText || element.textContent || "").trim(),
                        title: element.getAttribute("title") || "",
                        ariaLabel: element.getAttribute("aria-label") || "",
                        selectedText: element.tagName === "SELECT" && element.selectedOptions.length
                            ? element.selectedOptions[0].textContent.trim()
                            : "",
                        visible: visible(element)
                    }));
                    const actions = [...document.querySelectorAll(
                        'button, input[type="submit"], [role="button"], a'
                    )].filter(visible).map(element => ({
                        text: (element.innerText || element.value || element.textContent || "").trim(),
                        title: element.getAttribute("title") || "",
                        ariaLabel: element.getAttribute("aria-label") || ""
                    }));
                    const text = (document.body && document.body.innerText) || "";
                    const searchable = [
                        text,
                        ...selectors.filter(item => item.visible).flatMap(item => [
                            item.value, item.text, item.title, item.ariaLabel, item.selectedText
                        ]),
                        ...actions.flatMap(item => [item.text, item.title, item.ariaLabel])
                    ].filter(Boolean).join("\\n");
                    return { text, searchable, selectors, actions };
                }"""
            )
        except PlaywrightError:
            stable_reads = 0
            page.wait_for_timeout(1_000)
            continue

        last_text = str(last_state.get("text", ""))
        searchable = str(last_state.get("searchable", ""))
        normalized = searchable.casefold()
        is_loading = "loading" in normalized or "cargando" in normalized
        register_available = register_name in searchable
        open_session_available = "Abrir turno" in searchable

        if not is_loading and register_available and open_session_available:
            stable_reads += 1
            if stable_reads >= 2:
                print(f"{label}_POS_REGISTER_FOUND=true")
                print(f"{label}_OPEN_SESSION_ACTION_FOUND=true")
                print(f"{label}_RENDER_STATUS=ready")
                return last_text
        else:
            stable_reads = 0

        page.wait_for_timeout(1_000)

    print(f"{label}_POS_REGISTER_FOUND=false")
    print(f"{label}_OPEN_SESSION_ACTION_FOUND=false")
    print(f"{label}_LAST_SELECTORS=" + json.dumps(last_state.get("selectors", []), ensure_ascii=False))
    print(f"{label}_LAST_ACTIONS=" + json.dumps(last_state.get("actions", []), ensure_ascii=False))
    raise RuntimeError(
        f"{label} no mostró el puesto disponible {register_name!r} y la acción 'Abrir turno' "
        f"en {timeout_seconds}s. Último texto visible: {last_text.strip()[:1600]}"
    )


def select_pos_register(page: Any, register_name: str) -> None:
    """Verify the native POS selector across single-value and multi-register renderings."""
    # MyCompany renders name SELECTOR as a text input when only one POS is available.
    # In that case the selected register is the input's value, not a text node or label.
    # Treat an exact, unique visible value as already selected; do not try to click it.
    value_matches = page.locator('input[type="text"]').evaluate_all(
        """(elements, expected) => elements.filter(element => {
            const style = getComputedStyle(element);
            return style.display !== "none" &&
                style.visibility !== "hidden" &&
                !!(element.offsetWidth || element.offsetHeight) &&
                element.value === expected;
        }).map(element => ({
            value: element.value,
            readOnly: element.readOnly,
            disabled: element.disabled,
            id: element.id || "",
            name: element.name || "",
            title: element.getAttribute("title") || "",
            outerHTML: element.outerHTML.slice(0, 700)
        }))""",
        register_name,
    )
    print(f"UI_POS_REGISTER_VALUE_FIELD_MATCH_COUNT={len(value_matches)}")
    if len(value_matches) > 1:
        raise RuntimeError(
            f"Se encontraron varios campos visibles con el valor del puesto {register_name!r}: "
            + json.dumps(value_matches, ensure_ascii=False)
        )
    if len(value_matches) == 1:
        print("UI_POS_REGISTER_VALUE_FIELD_FOUND=true")
        print(
            "UI_POS_REGISTER_VALUE_FIELD="
            + json.dumps(value_matches[0], ensure_ascii=False)
        )
        print("UI_POS_REGISTER_ALREADY_SELECTED_BY_VALUE=true")
        print("UI_POS_REGISTER_ALREADY_SELECTED=true")
        print("UI_POS_REGISTER_SELECTION_VERIFIED=true")
        print(f"UI_POS_REGISTER_SELECTION_NAME={register_name}")
        return

    # With multiple POS, MyCompany renders explicit labels and native radio inputs.
    # Preserve this path so the CI smoke verifies (and changes) the actual radio state.
    register = page.get_by_text(register_name, exact=True)
    register.wait_for(state="visible", timeout=10_000)
    matches = [register.nth(index) for index in range(register.count())]
    visible_matches = []
    for match in matches:
        try:
            if match.is_visible():
                visible_matches.append(match)
        except PlaywrightError:
            continue
    if len(visible_matches) != 1:
        raise RuntimeError(
            f"Se esperaba un único selector visible para {register_name!r}; "
            f"coincidencias={len(visible_matches)}"
        )

    radio_id = visible_matches[0].get_attribute("for")
    if not radio_id:
        raise RuntimeError(
            f"El selector POS {register_name!r} no referencia un control de radio"
        )
    radio = page.locator(f'input[type="radio"][id="{radio_id}"]')
    if radio.count() != 1:
        raise RuntimeError(
            f"Se esperaba un radio nativo para {register_name!r}; "
            f"coincidencias={radio.count()}"
        )
    radio.wait_for(state="visible", timeout=10_000)
    print(f"UI_POS_REGISTER_RADIO_ID={radio_id}")

    if radio.is_checked():
        print("UI_POS_REGISTER_ALREADY_SELECTED=true")
    else:
        # El tooltip de documentación de lsFusion puede quedar sobre el label.
        # Cerrar el tooltip y operar sobre el radio nativo, no sobre texto libre.
        page.mouse.move(0, 0)
        page.keyboard.press("Escape")
        page.wait_for_timeout(350)
        radio.check(timeout=10_000)
        if not radio.is_checked():
            raise RuntimeError(
                f"El radio nativo no quedó seleccionado para {register_name!r}"
            )
        print("UI_POS_REGISTER_SELECTION_CLICKED=true")

    print("UI_POS_REGISTER_SELECTION_VERIFIED=true")
    print(f"UI_POS_REGISTER_SELECTION_NAME={register_name}")


def click_exact_action(page: Any, label: str) -> bool:
    # Prefer the stable lsFusion property container, but GWT can leave a hidden
    # projection node with that ID while the actual visible submit control is elsewhere.
    container = ACTION_CONTAINER_BY_LABEL.get(label)
    button = None

    if container:
        stable_button = page.locator(f'button[lsfusion-container="{container}"]')
        stable_count = stable_button.count()
        if stable_count == 1 and stable_button.is_visible():
            button = stable_button
        elif stable_count == 1:
            print(f"UI_ACTION_{label.upper().replace(' ', '_')}_STABLE_SELECTOR_HIDDEN=true")
            print(
                f"UI_ACTION_{label.upper().replace(' ', '_')}_HIDDEN_OUTERHTML="
                + stable_button.evaluate("element => element.outerHTML.slice(0, 900)")
            )
        else:
            print(
                f"UI_ACTION_{label.upper().replace(' ', '_')}_STABLE_SELECTOR_MATCH_COUNT={stable_count}"
            )

    if button is None:
        # Resolve the visible action by its accessible name at click time.
        # Never retain a DOM index: GWT can replace controls during rerenders.
        button = page.get_by_role("button", name=label, exact=True)
        accessible_count = button.count()
        if accessible_count != 1:
            # Some lsFusion builds render toolbar actions as input[type=submit].
            button = page.locator(
                f'input[type="submit"][value={json.dumps(label, ensure_ascii=False)}]:visible'
            )
            submit_count = button.count()
            if submit_count != 1:
                print(f"UI_ACTION_{label.upper().replace(' ', '_')}_FOUND=false")
                print(f"UI_ACTION_{label.upper().replace(' ', '_')}_MATCH_COUNT={accessible_count}")
                print(f"UI_ACTION_{label.upper().replace(' ', '_')}_SUBMIT_MATCH_COUNT={submit_count}")
                print(
                    f"UI_ACTION_{label.upper().replace(' ', '_')}_DIAGNOSTIC="
                    + json.dumps(
                        page.locator('button, input[type="submit"], [role="button"]').evaluate_all(
                            """elements => elements.map(element => ({
                                tag: element.tagName.toLowerCase(),
                                text: (element.innerText || element.value || element.textContent || "").trim(),
                                container: element.getAttribute("lsfusion-container") || "",
                                visible: getComputedStyle(element).display !== "none" &&
                                    getComputedStyle(element).visibility !== "hidden" &&
                                    !!(element.offsetWidth || element.offsetHeight),
                                outerHTML: element.outerHTML.slice(0, 700)
                            }))"""
                        ),
                        ensure_ascii=False,
                    )
                )
                return False

    try:
        button.wait_for(state="visible", timeout=12_000)
    except PlaywrightTimeoutError:
        print(f"UI_ACTION_{label.upper().replace(' ', '_')}_FOUND=false")
        print(f"UI_ACTION_{label.upper().replace(' ', '_')}_VISIBLE=false")
        return False

    actual_label = button.evaluate(
        'element => (element.innerText || element.value || element.textContent || "").trim()'
    )
    if actual_label != label:
        print(f"UI_ACTION_{label.upper().replace(' ', '_')}_LABEL_MISMATCH={actual_label!r}")
        return False

    button.scroll_into_view_if_needed()
    button.click(no_wait_after=True)
    print(f"UI_ACTION_{label.upper().replace(' ', '_')}_CLICKED=true")
    return True


def wait_for_payment_dialog(page: Any, timeout_seconds: int = 20) -> str:
    """Wait for the asynchronous lsFusion payment dialog, not an arbitrary delay."""
    deadline = time.monotonic() + timeout_seconds
    stable_reads = 0
    last_text = ""

    while time.monotonic() < deadline:
        try:
            last_text = page.locator("body").inner_text(timeout=5_000)
        except PlaywrightError:
            stable_reads = 0
            page.wait_for_timeout(500)
            continue

        normalized = last_text.casefold()
        if all(marker in normalized for marker in ("cobro", "medio de pago", "efectivo", "tarjeta")):
            stable_reads += 1
            if stable_reads >= 2:
                print("UI_PAYMENT_FORM_RENDERED=true")
                return last_text
        else:
            stable_reads = 0

        page.wait_for_timeout(500)

    print("UI_PAYMENT_FORM_RENDERED=false")
    visible_snapshot(page, "UI_PAYMENT_DIALOG_NOT_READY")
    raise RuntimeError(
        f"El diálogo de cobro no terminó de mostrar Efectivo y Tarjeta en {timeout_seconds}s. "
        f"Último texto visible: {last_text.strip()[:2500]}"
    )


def wait_for_session_open(page: Any, timeout_seconds: int = 45) -> str:
    deadline = time.monotonic() + timeout_seconds
    stable_reads = 0
    last_state: dict[str, Any] = {"text": "", "actions": []}

    while time.monotonic() < deadline:
        last_state = page.evaluate(
            """() => {
                const visible = element => {
                    const style = getComputedStyle(element);
                    return style.display !== "none" && style.visibility !== "hidden" &&
                        !!(element.offsetWidth || element.offsetHeight);
                };
                const actions = [...document.querySelectorAll(
                    'button, input[type="submit"], [role="button"]'
                )].filter(visible).map(element => ({
                    text: (element.innerText || element.value || element.textContent || "").trim(),
                    title: element.getAttribute("title") || "",
                    ariaLabel: element.getAttribute("aria-label") || ""
                }));
                return { text: (document.body && document.body.innerText) || "", actions };
            }"""
        )
        actions = last_state.get("actions", [])
        has_close_action = any(action.get("text") == "Cerrar turno" for action in actions)
        has_open_action = any(action.get("text") == "Abrir turno" for action in actions)

        if has_close_action and not has_open_action:
            stable_reads += 1
            if stable_reads >= 2:
                print("UI_SESSION_OPEN=true")
                print("UI_SESSION_CLOSE_ACTION_FOUND=true")
                return str(last_state.get("text", ""))
        else:
            stable_reads = 0
        page.wait_for_timeout(1_000)

    print("UI_SESSION_OPEN=false")
    print("UI_SESSION_CLOSE_ACTION_FOUND=false")
    print("UI_SESSION_LAST_ACTIONS=" + json.dumps(last_state.get("actions", []), ensure_ascii=False))
    raise RuntimeError(
        f"El turno no quedó abierto en {timeout_seconds}s; no apareció 'Cerrar turno'. "
        f"Texto visible: {str(last_state.get('text', '')).strip()[:1600]}"
    )


NAVIGATOR_CONTAINER_BY_LABEL = {
    # Stable lsFusion navigator IDs observed in the successful MyCompany 6.2 runtime.
    "Comercio": "Retail.retail",
    "Punto de venta": "Retail.posDashboard",
}

ACTION_CONTAINER_BY_LABEL = {
    # MyCompany renders these actions as GWT buttons with stable property containers.
    "Abrir turno": "PROPERTY(openSession(p))",
    # The payment dialog exposes the visible caption, but GWT omits it from the accessible role name.
    "Ok (ctrl ENTER)": "PROPERTY(overFormOk)",
    "Cerrar turno": "PROPERTY(close(s))",
}


def navigator_item(page: Any, label: str) -> Any:
    container = NAVIGATOR_CONTAINER_BY_LABEL.get(label)
    if container:
        return page.locator(f'a[lsfusion-container="{container}"]')
    # Fallback for labels without a known lsFusion container ID.
    return page.locator(f'a:text-is({json.dumps(label, ensure_ascii=False)})')


def describe_navigator_item(locator: Any) -> dict[str, Any]:
    return locator.evaluate(
        """element => ({
            text: (element.innerText || element.textContent || "").trim(),
            container: element.getAttribute("lsfusion-container") || "",
            visible: getComputedStyle(element).display !== "none" &&
                getComputedStyle(element).visibility !== "hidden" &&
                !!(element.offsetWidth || element.offsetHeight),
            expanded: element.getAttribute("aria-expanded") || "",
            className: typeof element.className === "string" ? element.className : "",
            outerHTML: element.outerHTML.slice(0, 900)
        })"""
    )


def navigator_diagnostics(page: Any) -> list[dict[str, Any]]:
    return page.locator("a").evaluate_all(
        """elements => elements.map((element, index) => ({
            index,
            text: (element.innerText || element.textContent || "").trim(),
            container: element.getAttribute("lsfusion-container") || "",
            visible: getComputedStyle(element).display !== "none" &&
                getComputedStyle(element).visibility !== "hidden" &&
                !!(element.offsetWidth || element.offsetHeight),
            expanded: element.getAttribute("aria-expanded") || "",
            className: typeof element.className === "string" ? element.className : "",
            outerHTML: element.outerHTML.slice(0, 700)
        }))"""
    )


def click_exact_link(
    page: Any, label: str, submenu_label: str | None = None
) -> bool:
    # MyCompany navigator anchors intentionally have no href and no ARIA role.
    # Use lsFusion's stable container IDs instead of role=link or DOM indexes.
    link = navigator_item(page, label)
    match_count = link.count()
    if match_count != 1:
        print(f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_MATCH_COUNT={match_count}")
        print(
            f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_CANDIDATES="
            + json.dumps(navigator_diagnostics(page), ensure_ascii=False)
        )
        return False

    try:
        link.wait_for(state="visible", timeout=12_000)
    except PlaywrightTimeoutError:
        print(f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_FOUND=false")
        print(
            f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_CANDIDATES="
            + json.dumps(navigator_diagnostics(page), ensure_ascii=False)
        )
        return False

    target = describe_navigator_item(link)
    print(
        f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_TARGET="
        + json.dumps(target, ensure_ascii=False)
    )

    submenu = navigator_item(page, submenu_label) if submenu_label else None
    if submenu is not None and submenu.count() == 1 and submenu.is_visible():
        print(f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_EXPANDED=true")
        return True

    link.scroll_into_view_if_needed()
    link.click(no_wait_after=True)
    print(f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_CLICKED=true")

    if submenu is None:
        return True

    try:
        submenu.wait_for(state="visible", timeout=20_000)
    except PlaywrightTimeoutError:
        print(f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_EXPANDED=false")
        print(
            f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_STATE="
            + json.dumps(describe_navigator_item(link), ensure_ascii=False)
        )
        print(
            f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_CANDIDATES="
            + json.dumps(navigator_diagnostics(page), ensure_ascii=False)
        )
        visible_snapshot(page, f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_FAILED")
        return False

    print(f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_EXPANDED=true")
    return True


def accept_ls_fusion_confirmation(page: Any, action_label: str) -> str:
    """Accept lsFusion's GWT CONFIRM modal, not a browser-native JavaScript dialog."""
    modal = page.locator(".modal.show")
    modal.wait_for(state="visible", timeout=15_000)

    modal_count = modal.count()
    if modal_count != 1:
        raise RuntimeError(
            f"{action_label}: se esperaba un único modal de confirmación GWT, "
            f"pero aparecieron {modal_count}."
        )

    message = modal.locator(".modal-body").inner_text(timeout=5_000).strip()
    footer_buttons = modal.locator(".modal-footer button")
    button_labels = [
        label.strip()
        for label in footer_buttons.all_inner_texts()
        if label.strip()
    ]
    print(f"UI_GWT_CONFIRMATION_MESSAGE={message}")
    print("UI_GWT_CONFIRMATION_BUTTONS=" + json.dumps(button_labels, ensure_ascii=False))

    # DialogBoxHelper maps OptionType.YES to FormButton.ButtonStyle.PRIMARY.
    # This is the positive option; the secondary button is NO.
    affirmative = modal.locator(".modal-footer button.btn-primary")
    affirmative_count = affirmative.count()
    if affirmative_count != 1:
        raise RuntimeError(
            f"{action_label}: el modal GWT debe exponer exactamente un botón afirmativo "
            f"btn-primary; se encontraron {affirmative_count}. "
            f"Botones: {json.dumps(button_labels, ensure_ascii=False)}"
        )

    affirmative_label = affirmative.inner_text().strip()
    if affirmative_label != "Sí":
        raise RuntimeError(
            f"{action_label}: el botón afirmativo del cliente GWT no quedó localizado. "
            f"Se esperaba 'Sí', se recibió {affirmative_label!r}."
        )

    print("UI_GWT_CONFIRMATION_AFFIRMATIVE=Sí")
    affirmative.click(no_wait_after=True)
    modal.wait_for(state="detached", timeout=15_000)
    print("UI_GWT_CONFIRMATION_ACCEPTED=true")
    return message



def fetch_restart_api_payload(context: Any, endpoint: str, label: str) -> dict[str, Any]:
    response = context.request.get(endpoint, timeout=12_000)
    if response.status != 200:
        raise RuntimeError(
            f"La verificación posterior al reinicio ({label}) respondió HTTP "
            f"{response.status}: {response.text()[:1200]}"
        )
    try:
        payload = response.json()
    except ValueError as error:
        raise RuntimeError(
            f"La verificación posterior al reinicio ({label}) no devolvió JSON válido."
        ) from error
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"La verificación posterior al reinicio ({label}) devolvió "
            f"{type(payload).__name__}, no un objeto JSON."
        )
    print(f"UI_RESTART_PERSISTENCE_{label.upper()}_PAYLOAD=" + json.dumps(payload, ensure_ascii=False))
    return payload



def _native_collection(payload: dict[str, Any], field: str, label: str) -> list[dict[str, Any]]:
    count_field = f"{field}Count"
    expected_count = payload.get(count_field)
    if isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count < 0:
        raise ValueError(f"{count_field} debe ser un entero no negativo.")
    rows = payload.get(field)
    # lsFusion puede omitir el objeto JSON anidado si la consulta no tiene filas.
    # Sólo se interpreta como [] cuando el contador nativo independiente confirma cero filas.
    if rows is None and expected_count == 0:
        rows = []
    if not isinstance(rows, list):
        raise ValueError(f"{field} es {type(rows).__name__}; {count_field}={expected_count}.")
    if len(rows) != expected_count:
        raise ValueError(f"{count_field}={expected_count} no coincide con {len(rows)} filas en {field}.")
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"Todos los elementos de {field} deben ser objetos JSON.")
    return rows


def _outgoing_reservation_totals(
    commitments: list[dict[str, Any]],
    reservation_rows: list[dict[str, Any]],
) -> dict[str, float]:
    """Aggregate native ShipmentLine facts by the stable Sales.OrderLine key."""
    commitments_by_id: dict[str, float] = {}
    for index, row in enumerate(commitments):
        label = f"outgoingCommitments[{index}]"
        line_id = str(row.get("sourceLineId") or "").strip()
        if not line_id or line_id in commitments_by_id:
            raise ValueError(f"{label}.sourceLineId está vacío o duplicado.")
        open_quantity = row.get("openQuantity")
        if (isinstance(open_quantity, bool) or not isinstance(open_quantity, (int, float))
                or not math.isfinite(float(open_quantity)) or float(open_quantity) <= 0):
            raise ValueError(f"{label}.openQuantity debe ser positiva y finita.")
        commitments_by_id[line_id] = float(open_quantity)

    totals: dict[str, float] = {}
    seen_shipment_lines: set[str] = set()
    for index, row in enumerate(reservation_rows):
        label = f"outgoingReservations[{index}]"
        line_id = str(row.get("sourceLineId") or "").strip()
        if line_id not in commitments_by_id:
            raise ValueError(f"{label}.sourceLineId no referencia una línea de salida exportada.")
        shipment_line_id = str(row.get("shipmentLineId") or "").strip()
        if not shipment_line_id or shipment_line_id in seen_shipment_lines:
            raise ValueError(f"{label}.shipmentLineId está vacío o duplicado.")
        seen_shipment_lines.add(shipment_line_id)
        if not str(row.get("shipmentId") or "").strip():
            raise ValueError(f"{label}.shipmentId está vacío.")
        eligible = row.get("reserveEligible")
        if not isinstance(eligible, bool):
            raise ValueError(f"{label}.reserveEligible debe ser booleano.")
        def component_milli(field: str) -> int:
            if field not in row:
                raise ValueError(f"{label}.{field} debe estar presente (puede ser null).")
            value = row[field]
            if value is None:
                return 0
            if isinstance(value, bool) or not isinstance(value, (int, float, str)):
                raise ValueError(f"{label}.{field} debe ser numérico o null.")
            try:
                quantity = Decimal(str(value))
            except InvalidOperation as error:
                raise ValueError(f"{label}.{field} debe ser numérico o null.") from error
            if not quantity.is_finite():
                raise ValueError(f"{label}.{field} debe ser finito.")
            scaled = quantity * 1000
            if scaled != scaled.to_integral_value():
                raise ValueError(f"{label}.{field} supera tres decimales.")
            return int(scaled)

        reserved_quantity = component_milli("reservedQuantityNative")
        ledger_reserved_quantity = component_milli("ledgerReservedQuantityNative")
        line_reserved_milli = reserved_quantity - ledger_reserved_quantity
        if eligible and line_reserved_milli > 0:
            line_reserved = line_reserved_milli / 1000.0
            totals[line_id] = totals.get(line_id, 0.0) + line_reserved

    for line_id, reserved in totals.items():
        if reserved > commitments_by_id[line_id] + 0.001:
            raise ValueError(
                f"La reserva agregada supera el remanente de {line_id}: "
                f"openQuantity={commitments_by_id[line_id]}, effectiveReserved={reserved}."
            )
    return totals


def probe_replenishment_source_sections(context: Any, url: str) -> None:
    """Validate native array shape and count on each independently authenticated endpoint."""
    endpoint = application_endpoint_url(url, "exec/Rubrova.")
    probes = (
        ("inventory", "inventory", "rubrovaProbeInventory"),
        ("outgoing_commitments", "outgoingCommitments", "rubrovaProbeOutgoingCommitments"),
        ("receipts", "receipts", "rubrovaProbeReceipts"),
    )
    failures: list[str] = []
    require_positive = os.environ.get("RUBROVA_UI_REQUIRE_POSITIVE_REPLENISHMENT", "false").lower() == "true"
    for label, collection_field, action in probes:
        response = context.request.get(endpoint + action, timeout=20_000)
        print(f"UI_REPLENISHMENT_PROBE_{label.upper()}_HTTP={response.status}")
        if response.status != 200:
            detail = response.text()[:1800].replace("\r", " ").replace("\n", " ")
            print(f"UI_REPLENISHMENT_PROBE_{label.upper()}_ERROR={detail}")
            failures.append(f"{label}: HTTP {response.status} ({detail[:500]})")
            continue

        try:
            payload = response.json()
            if isinstance(payload, list):
                payload = payload[0] if len(payload) == 1 else {}
            if not isinstance(payload, dict):
                raise ValueError(f"la raíz JSON es {type(payload).__name__}, no un objeto")
            rows = _native_collection(payload, collection_field, label)
            if require_positive and label in {"outgoing_commitments", "receipts"} and not rows:
                raise ValueError(f"{collection_field} debe contener al menos una fila en el fixture positivo de CI.")
            count_field = f"{collection_field}Count"
            print(f"UI_REPLENISHMENT_PROBE_{label.upper()}_JSON=true")
            print(f"UI_REPLENISHMENT_PROBE_{label.upper()}_ROOT_KEYS=" + json.dumps(sorted(payload)))
            print(f"UI_REPLENISHMENT_PROBE_{label.upper()}_COLLECTION_TYPE=list")
            print(f"UI_REPLENISHMENT_PROBE_{label.upper()}_ROWS={len(rows)}")
            print(f"UI_REPLENISHMENT_PROBE_{label.upper()}_SOURCE_COUNT={payload[count_field]}")
            if label == "outgoing_commitments":
                reservation_rows = _native_collection(payload, "outgoingReservations", label)
                # Emit the exact source facts before semantic validation so CI retains
                # evidence even when a required native JSON key is missing.
                print("UI_REPLENISHMENT_PROBE_OUTGOING_COMMITMENTS_ROWS_JSON=" + json.dumps(rows, ensure_ascii=False))
                print("UI_REPLENISHMENT_PROBE_OUTGOING_RESERVATION_ROWS_JSON=" + json.dumps(reservation_rows, ensure_ascii=False))
                totals = _outgoing_reservation_totals(rows, reservation_rows)
                print("UI_REPLENISHMENT_PROBE_OUTGOING_EFFECTIVE_TOTALS=" + json.dumps(totals, ensure_ascii=False, sort_keys=True))
                print("UI_REPLENISHMENT_PROBE_OUTGOING_RESERVATION_SOURCE_COUNT=" + str(payload["outgoingReservationsCount"]))
                if require_positive and not any(value > 0 for value in totals.values()):
                    raise ValueError("El fixture positivo debe tener reservas efectivas positivas agregadas desde ShipmentLine.")
        except ValueError as error:
            print(f"UI_REPLENISHMENT_PROBE_{label.upper()}_JSON=false")
            failures.append(f"{label}: respuesta JSON incompatible ({error})")
    if failures:
        raise RuntimeError(
            "Falló la estructura de una consulta aislada de la exportación MyCompany: "
            + "; ".join(failures)
        )

def prepare_ci_outgoing_reservation(context: Any, url: str) -> None:
    """Run MyCompany's own availability precheck for the disposable CI sales order."""
    if os.environ.get("RUBROVA_UI_REQUIRE_POSITIVE_REPLENISHMENT", "false").lower() != "true":
        return
    endpoint = application_endpoint_url(url, "exec/Rubrova.")
    response = context.request.get(endpoint + "rubrovaPrepareOutgoingReservation", timeout=20_000)
    print(f"UI_REPLENISHMENT_CI_RESERVATION_HTTP={response.status}")
    if response.status != 200:
        raise RuntimeError(
            "No se pudo preparar la reserva del fixture de salida: "
            f"HTTP {response.status}: {response.text()[:1000]}"
        )
    try:
        payload = response.json()
    except ValueError as error:
        raise RuntimeError("La preparación de reserva CI no devolvió JSON válido.") from error
    if isinstance(payload, list):
        payload = payload[0] if len(payload) == 1 else {}
    if not isinstance(payload, dict):
        raise RuntimeError("La preparación de reserva CI no devolvió un objeto JSON.")
    print("UI_REPLENISHMENT_CI_RESERVATION_DIAGNOSTICS=" + json.dumps(payload, ensure_ascii=False))

    def quantity(field: str) -> float:
        value = payload.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise RuntimeError(f"La preparación de reserva CI devolvió {field} no numérico.")
        return float(value)

    open_quantity = quantity("outgoingOpenQuantity")
    reserved_quantity = quantity("outgoingReservedQuantity")
    if open_quantity <= 0 or reserved_quantity <= 0 or reserved_quantity > open_quantity + 0.001:
        raise RuntimeError(
            "El precheckAvailability nativo no generó una reserva válida para el pedido CI; "
            f"openQuantity={open_quantity}, effectiveReserved={reserved_quantity}."
        )
    print("UI_REPLENISHMENT_CI_RESERVATION_PREPARED=" + json.dumps({
        "openQuantity": open_quantity,
        "effectiveReserved": reserved_quantity,
    }, ensure_ascii=False))


def verify_replenishment_source_export(context: Any, url: str) -> None:
    """Validate the native MyCompany export without mutating the ERP."""
    prepare_ci_outgoing_reservation(context, url)
    probe_replenishment_source_sections(context, url)
    endpoint = application_endpoint_url(url, "exec/Rubrova.")
    response = context.request.get(
        endpoint + "rubrovaExportReplenishmentSource",
        timeout=20_000,
    )
    if response.status != 200:
        raise RuntimeError(
            "La exportación nativa de reposición respondió HTTP "
            f"{response.status}: {response.text()[:1200]}"
        )
    try:
        payload = response.json()
    except ValueError as error:
        raise RuntimeError("La exportación nativa de reposición no devolvió JSON válido.") from error
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    if not isinstance(payload, dict):
        raise RuntimeError("La exportación nativa de reposición no devolvió un objeto JSON.")

    expected_header = {
        "schemaVersion": NATIVE_EXPORT_SCHEMA_VERSION,
        "snapshotType": "mycompany-replenishment-source-export",
        "sourceSystem": "MyCompany",
        "sourceVersion": "6.2",
        "quantityUnit": "product-uom",
        "quantityPrecision": 3,
        "readOnly": True,
    }
    for field, expected in expected_header.items():
        if payload.get(field) != expected:
            raise RuntimeError(
                f"Contrato de exportación inválido en {field}: "
                f"esperado {expected!r}, recibido {payload.get(field)!r}."
            )

    from datetime import date, datetime
    try:
        date.fromisoformat(str(payload.get("asOf", ""))[:10])
        datetime.fromisoformat(str(payload.get("asOfDateTime", "")).replace("Z", "+00:00"))
    except ValueError as error:
        raise RuntimeError("La fecha asOf de la exportación no usa YYYY-MM-DD.") from error

    expected_semantics = {
        "inventoryOnHand": "Inventory.onHand(Location, Product), ubicación exacta",
        "inventoryAvailable": "Inventory.available(Location, Product), valor nativo MyCompany",
        "inventoryPlannedNet": "Inventory.planned(Location, Product), reservas firmadas que participan en available",
        "inventoryExpectedCoverage": "all negative ResLedger reservations for exact product/location; not limited to confirmed purchase receipts",
        "emptyAggregatePolicy": "raw *Native fields preserve NULL; effective numeric fields use OVERRIDE fallback 0",
        "emptyCollectionPolicy": "collection counts are authoritative; an omitted collection is an empty list only when its count is zero",
        "outgoingIdentity": "Sales.number(Order) + Sales.index(OrderLine)",
        "outgoingOpenQuantity": "Sales.toShip(OrderLine_confirmed)",
        "outgoingScheduledDateTime": "Sales.scheduledDateTime(Order)",
        "outgoingReservationSource": "ShipmentLine linked to a confirmed Sales.OrderLine; one raw row per shipment line",
        "outgoingReservationComponents": "Inventory.reserved(ShipmentLine) and Inventory.ledgerReserved(ShipmentLine); NULL components normalize to zero in Rubrova",
        "outgoingEffectiveReservation": "SUM((reservedQuantityNative - ledgerReservedQuantityNative) > 0 where reserveEligible = true, grouped by sourceLineId)",
        "incomingIdentity": "Receipt.number + ReceiptLine.index",
        "incomingExpectedQuantity": "0 - ReceiptResLedger.reserved; signed reservation remains negative",
        "incomingScheduledDateTime": "Receipt.scheduledDateTime",
        "incomingEligibility": "Receipt.ready AND NOT Receipt.done AND NOT Receipt.canceled AND Purchase.Order.confirmed",
        "incomingAvailabilityPolicy": "ReceiptType.increaseAvailableStock; skipAvailable is its inverse",
    }
    if payload.get("sourceSemantics") != expected_semantics:
        raise RuntimeError("sourceSemantics no coincide con el contrato de exportación MyCompany 6.2.")

    collections: dict[str, list[dict[str, Any]]] = {}
    source_counts: dict[str, int] = {}
    for field in ("inventory", "outgoingCommitments", "outgoingReservations", "receipts"):
        try:
            rows = _native_collection(payload, field, "export")
        except ValueError as error:
            raise RuntimeError(f"Contrato inválido para {field}: {error}") from error
        collections[field] = rows
        source_counts[field] = payload[f"{field}Count"]
    print("UI_REPLENISHMENT_SOURCE_EXPORT_OUTGOING_ROWS=" + json.dumps(
        collections["outgoingCommitments"], ensure_ascii=False
    ))
    outgoing_reservation_totals = _outgoing_reservation_totals(collections["outgoingCommitments"], collections["outgoingReservations"])
    print("UI_REPLENISHMENT_SOURCE_EXPORT_OUTGOING_RESERVATION_ROWS=" + json.dumps(collections["outgoingReservations"], ensure_ascii=False))
    print("UI_REPLENISHMENT_SOURCE_EXPORT_OUTGOING_EFFECTIVE_TOTALS=" + json.dumps(outgoing_reservation_totals, ensure_ascii=False, sort_keys=True))

    def numeric(row: dict[str, Any], field: str, row_label: str) -> float:
        value = row.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise RuntimeError(f"{row_label}.{field} debe ser un número finito.")
        return float(value)

    inventory_keys: set[tuple[str, str]] = set()
    for index, row in enumerate(collections["inventory"]):
        row_label = f"inventory[{index}]"
        product_id = str(row.get("productId") or "").strip()
        location_id = str(row.get("locationId") or "").strip()
        if not product_id or not location_id:
            raise RuntimeError(f"{row_label} no identifica producto y ubicación.")
        key = (product_id, location_id)
        if key in inventory_keys:
            raise RuntimeError(f"Inventario duplicado para producto/ubicación {product_id}/{location_id}.")
        inventory_keys.add(key)
        on_hand = numeric(row, "onHand", row_label)
        planned = numeric(row, "plannedNetReservation", row_label)
        available = numeric(row, "available", row_label)
        numeric(row, "physicalIncoming", row_label)
        numeric(row, "physicalOutgoing", row_label)
        gross_reserved = numeric(row, "grossReserved", row_label)
        planned = numeric(row, "plannedNetReservation", row_label)
        expected_inbound = numeric(row, "expectedInbound", row_label)
        native_values = {
            field: row.get(field)
            for field in ("onHandNative", "availableNative", "plannedNetReservationNative",
                          "physicalIncomingNative", "physicalOutgoingNative")
        }
        for field, value in native_values.items():
            if value is not None:
                numeric(row, field, row_label)
        if native_values["onHandNative"] is not None and abs(float(native_values["onHandNative"]) - on_hand) > 0.001:
            raise RuntimeError(f"{row_label}.onHand no coincide con onHandNative.")
        if native_values["availableNative"] is not None and abs(float(native_values["availableNative"]) - available) > 0.001:
            raise RuntimeError(f"{row_label}.available no coincide con availableNative.")
        if native_values["plannedNetReservationNative"] is not None and abs(float(native_values["plannedNetReservationNative"]) - planned) > 0.001:
            raise RuntimeError(f"{row_label}.plannedNetReservation no coincide con el ledger nativo.")
        if gross_reserved < 0 or expected_inbound < 0:
            raise RuntimeError(f"{row_label} contiene una reserva bruta o recepción prevista negativa.")
        if abs((on_hand - planned) - available) > 0.001:
            raise RuntimeError(
                f"Inventory.available no concilia en {product_id}/{location_id}: "
                f"onHand={on_hand}, planned={planned}, available={available}."
            )

    outgoing_ids: set[str] = set()
    for index, row in enumerate(collections["outgoingCommitments"]):
        row_label = f"outgoingCommitments[{index}]"
        line_id = str(row.get("sourceLineId") or "").strip()
        if not line_id or line_id in outgoing_ids:
            raise RuntimeError(f"{row_label}.sourceLineId está vacío o duplicado.")
        outgoing_ids.add(line_id)
        open_quantity = numeric(row, "openQuantity", row_label)
        reserved = outgoing_reservation_totals.get(line_id, 0.0)
        if row.get("status") != "confirmed" or open_quantity <= 0 or reserved < 0 or reserved > open_quantity + 0.001:
            raise RuntimeError(
                f"{row_label} viola la semántica de compromiso abierto/reserva efectiva: "
                f"openQuantity={open_quantity}, effectiveReserved={reserved}."
            )
        for field in ("sourceDocumentId", "productId", "locationId", "scheduledDate", "scheduledDateTime"):
            if not str(row.get(field) or "").strip():
                raise RuntimeError(f"{row_label}.{field} está vacío.")

    receipt_ids: set[str] = set()
    for index, row in enumerate(collections["receipts"]):
        row_label = f"receipts[{index}]"
        line_id = str(row.get("lineId") or "").strip()
        if not line_id or line_id in receipt_ids:
            raise RuntimeError(f"{row_label}.lineId está vacío o duplicado.")
        receipt_ids.add(line_id)
        signed_reservation = numeric(row, "expectedReservationSigned", row_label)
        quantity = numeric(row, "expectedQuantity", row_label)
        if (
            quantity <= 0
            or signed_reservation >= 0
            or abs(quantity + signed_reservation) > 0.001
            or row.get("status") != "ready"
            or row.get("purchaseOrderStatus") != "confirmed"
            or (row.get("increaseAvailableStock") is not None and not isinstance(row.get("increaseAvailableStock"), bool))
        ):
            raise RuntimeError(f"{row_label} no respeta el contrato de recepción pendiente.")
        for field in ("receiptId", "purchaseOrderId", "purchaseOrderLineId", "productId", "locationId", "scheduledDate", "scheduledDateTime"):
            if not str(row.get(field) or "").strip():
                raise RuntimeError(f"{row_label}.{field} está vacío.")

    require_positive = os.environ.get("RUBROVA_UI_REQUIRE_POSITIVE_REPLENISHMENT", "false").lower() == "true"
    if require_positive:
        if source_counts["outgoingCommitments"] < 1 or not collections["outgoingCommitments"]:
            raise RuntimeError("El fixture positivo debe generar al menos un compromiso de salida.")
        if source_counts["outgoingReservations"] < 1 or not collections["outgoingReservations"]:
            raise RuntimeError("El fixture positivo debe generar al menos una línea de reserva nativa.")
        if source_counts["receipts"] < 1 or not collections["receipts"]:
            raise RuntimeError("El fixture positivo debe generar al menos una recepción pendiente.")
        outgoing = collections["outgoingCommitments"][0]
        outgoing_line_id = str(outgoing.get("sourceLineId") or "")
        outgoing_quantity = numeric(outgoing, "openQuantity", "outgoingCommitments[0]")
        outgoing_reserved = outgoing_reservation_totals.get(outgoing_line_id, 0.0)
        if outgoing_quantity <= 0 or outgoing_reserved <= 0:
            raise RuntimeError(
                "El fixture de salida debe tener cantidad abierta y reserva efectiva positivas; "
                f"openQuantity={outgoing_quantity}, effectiveReserved={outgoing_reserved}."
            )
        receipt = collections["receipts"][0]
        receipt_quantity = numeric(receipt, "expectedQuantity", "receipts[0]")
        incoming_increase_available = receipt.get("increaseAvailableStock")
        if receipt_quantity <= 0 or incoming_increase_available is True:
            raise RuntimeError(
                "El fixture de recepción debe conservar cantidad pendiente positiva y "
                "no habilitar increaseAvailableStock."
            )
        print("UI_REPLENISHMENT_POSITIVE_FIXTURES=" + json.dumps({
            "outgoingOpenQuantity": outgoing_quantity,
            "outgoingEffectiveReserved": outgoing_reserved,
            "incomingExpectedQuantity": receipt_quantity,
            "incomingIncreaseAvailableStock": incoming_increase_available is True,
            "incomingNativeFlag": incoming_increase_available,
        }, ensure_ascii=False))

    print(
        "UI_REPLENISHMENT_SOURCE_EXPORT_COUNTS="
        + json.dumps(
            {
                "inventory": {"source": source_counts["inventory"], "rows": len(collections["inventory"])},
                "outgoingCommitments": {"source": source_counts["outgoingCommitments"], "rows": len(collections["outgoingCommitments"])},
                "outgoingReservations": {"source": source_counts["outgoingReservations"], "rows": len(collections["outgoingReservations"])},
                "receipts": {"source": source_counts["receipts"], "rows": len(collections["receipts"])},
            },
            ensure_ascii=False,
        )
    )
    print("UI_REPLENISHMENT_NATIVE_NULL_AGGREGATES="
          + json.dumps({field: sum(row.get(field) is None for row in collections["inventory"])
                         for field in ("onHandNative", "availableNative", "plannedNetReservationNative")},
                        ensure_ascii=False))
    print("UI_REPLENISHMENT_NATIVE_AVAILABLE_RECONCILED=true")
    print("UI_REPLENISHMENT_SOURCE_EXPORT_VERIFIED=true")


def verify_restarted_persistence(context: Any, url: str) -> None:
    base = application_endpoint_url(url, "exec/")

    sales = fetch_restart_api_payload(
        context,
        base + "Sales.rubrovaTestSalesReconciliationApi",
        "sale",
    )
    expected_sales = {
        "salesCount": 1,
        "paidSalesCount": 1,
        "invoiceAmount": 1250,
        "paidAmount": 1250,
        "cashPaidAmount": 1250,
        "incomingPaymentCount": 1,
        "cashBalance": 0,
    }
    for field, expected in expected_sales.items():
        try:
            actual = float(sales.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(
                f"La persistencia posterior al reinicio devolvió un valor inválido "
                f"para {field}: {sales.get(field)!r}"
            ) from error
        if abs(actual - expected) > 0.001:
            raise RuntimeError(
                f"La venta/pago no sobrevivió al reinicio en {field}: "
                f"esperado {expected}, recibido {actual}."
            )
    print("UI_RESTART_PERSISTENCE_SALE_RECONCILED=true")

    inventory = fetch_restart_api_payload(
        context,
        base + "Sales.rubrovaTestInventoryApi",
        "inventory",
    )
    for field, expected in {
        "incomingQuantity": 12,
        "outgoingQuantity": 2,
        "onHand": 10,
    }.items():
        try:
            actual = float(inventory.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(
                f"El inventario persistido devolvió un valor inválido para {field}."
            ) from error
        if abs(actual - expected) > 0.001:
            raise RuntimeError(
                f"El inventario no sobrevivió al reinicio en {field}: "
                f"esperado {expected}, recibido {actual}."
            )
    print("UI_RESTART_PERSISTENCE_STOCK_RECONCILED=true")

    session = fetch_restart_api_payload(
        context,
        base + "Sales.rubrovaTestSessionCloseApi",
        "session",
    )
    if (
        session.get("sessionStatus") != "CLOSED"
        or not session.get("sessionNumber")
        or not session.get("openingDateTime")
        or not session.get("closingDateTime")
    ):
        raise RuntimeError(
            "El cierre del turno no sobrevivió al reinicio o perdió sus marcas de tiempo: "
            + json.dumps(session, ensure_ascii=False)
        )
    for field, expected in {
        "salesCount": 1,
        "salesAmount": 1250,
        "returnsCount": 2,
        "returnsAmount": 1250,
        "netAmount": 0,
        "cashPaid": 0,
        "cashBalance": 0,
    }.items():
        try:
            actual = float(session.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(
                f"El cierre persistido devolvió un valor inválido para {field}."
            ) from error
        if abs(actual - expected) > 0.001:
            raise RuntimeError(
                f"El cierre persistido no coincide en {field}: "
                f"esperado {expected}, recibido {actual}."
            )
    print("UI_RESTART_PERSISTENCE_SESSION_CLOSED=true")
    print("UI_RESTART_PERSISTENCE_CASH_RECONCILED=true")

    partial_returns = fetch_restart_api_payload(
        context,
        base + "Sales.rubrovaPartialReturnsReconciliationApi",
        "partial returns",
    )
    for field, expected in {
        "returnBillCount": 2,
        "returnAmount": 1250,
        "returnedQuantity": 1,
        "cashRefundPaymentCount": 2,
        "cashRefundPaymentAmount": 1250,
        "sessionCashNet": 0,
        "cashBalance": 0,
        "onHand": 10,
    }.items():
        try:
            actual = float(partial_returns.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(
                f"Las devoluciones persistidas devolvieron un valor inválido en {field}."
            ) from error
        if abs(actual - expected) > 0.001:
            raise RuntimeError(
                f"Las devoluciones parciales no sobrevivieron al reinicio en {field}: "
                f"esperado {expected}, recibido {actual}."
            )
    if partial_returns.get("overReturnRejected") is not True:
        raise RuntimeError(
            "La evidencia persistida no conserva el rechazo de sobredevolución: "
            + json.dumps(partial_returns, ensure_ascii=False)
        )
    print("UI_RESTART_PERSISTENCE_PARTIAL_RETURNS=true")

    verify_cumulative_refunds_persistence(context, url)
    verify_stocktake_persistence(context, url)

    incidents = fetch_restart_api_payload(
        context,
        base + "Rubrova.rubrovaTestIncidentCountApi",
        "incidents",
    )
    try:
        incident_count = int(incidents.get("incidentCount") or 0)
    except (TypeError, ValueError) as error:
        raise RuntimeError("El contador de incidencias persistidas no es numérico.") from error
    if incident_count < 8:
        raise RuntimeError(
            "No sobrevivieron las ocho incidencias de integración al reinicio; "
            f"se encontraron {incident_count}."
        )
    print(f"UI_RESTART_PERSISTENCE_INCIDENT_COUNT={incident_count}")
    print("UI_RESTART_PERSISTENCE_INCIDENTS_RETAINED=true")




def verify_return_quantity_guard(context: Any, url: str) -> None:
    """Verify that Rubrova enables MyCompany's original invoice return-quantity constraint."""
    api_base = application_endpoint_url(url, "exec/Sales.")
    response = context.request.get(api_base + "rubrovaReturnSafetyApi", timeout=12_000)
    if response.status != 200:
        raise RuntimeError(
            "La sonda de protección contra sobredevolución respondió "
            f"HTTP {response.status}: {response.text()[:1200]}"
        )
    payload = response.json()
    if not isinstance(payload, dict) or payload.get("retailReturnQuantityGuardEnabled") is not True:
        raise RuntimeError(
            "MyCompany no tiene activado el límite de cantidad devuelta para el comprobante retail: "
            + json.dumps(payload, ensure_ascii=False)
        )
    print("UI_RETURN_QUANTITY_GUARD_ENABLED=true")




def _native_api_get_with_cookie_header(base_url: str, endpoint: str, cookie_header: str) -> dict[str, Any]:
    if not cookie_header:
        raise RuntimeError("No se encontraron cookies de sesión autenticada para la prueba concurrente.")

    request = urllib.request.Request(
        base_url + endpoint,
        headers={"Cookie": cookie_header, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
            content_type = response.headers.get("content-type", "")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"La API concurrente {endpoint} respondió HTTP {error.code}: {body[:1600]!r}"
        ) from error
    if status != 200:
        raise RuntimeError(f"La API concurrente {endpoint} respondió HTTP {status}: {body[:1600]!r}")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"La API concurrente {endpoint} no devolvió JSON; "
            f"Content-Type={content_type!r}, cuerpo={body[:1600]!r}"
        ) from error
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    if not isinstance(payload, dict):
        raise RuntimeError(f"La API concurrente {endpoint} no devolvió un objeto JSON.")
    return payload


def _cookie_header_for_api_context(context: Any, api_base: str) -> tuple[str, dict[str, str]]:
    cookies = context.cookies(api_base)
    values = {
        str(cookie["name"]): str(cookie["value"])
        for cookie in cookies
        if cookie.get("name") and cookie.get("value") is not None
    }
    return "; ".join(f"{name}={value}" for name, value in values.items()), values


def verify_cumulative_refunds(context: Any, url: str, browser: Any) -> None:
    """Exercise per-method cumulative caps, serializable competing applies and native cancellations."""
    api_base = application_endpoint_url(url, "exec/Sales.")
    initial = context.request.get(api_base + "rubrovaTestCumulativeRefundsApi", timeout=60_000)
    if initial.status != 200:
        raise RuntimeError(
            f"La preparación de reintegros mixtos respondió HTTP {initial.status}: {initial.text()[:1600]}"
        )
    initial_payload = initial.json()
    if isinstance(initial_payload, list):
        initial_payload = initial_payload[0] if initial_payload else {}
    if not isinstance(initial_payload, dict):
        raise RuntimeError("La preparación de reintegros mixtos no devolvió un objeto JSON.")
    expected_initial = {
        "sourceInvoiceFound": 1,
        "originalCashPaid": 500,
        "originalCardPaid": 750,
        "activeReturnCount": 1,
        "activeReturnAmount": 500,
        "returnedQuantity": 0.4,
        "activeCashRefundCount": 1,
        "activeCashRefundAmount": 200,
        "activeCardRefundCount": 1,
        "activeCardRefundAmount": 300,
        "cashAccountBalance": 1300,
        "cardAccountBalance": 1450,
    }
    for field, expected in expected_initial.items():
        try:
            actual = float(initial_payload.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(f"La preparación mixta devolvió un valor no numérico en {field}.") from error
        if abs(actual - expected) > 0.001:
            raise RuntimeError(
                f"La preparación de reintegros mixtos no coincide en {field}: "
                f"esperado {expected}, recibido {actual}. "
                f"{json.dumps(initial_payload, ensure_ascii=False)}"
            )
    if initial_payload.get("overLimitRejected") is not True:
        raise RuntimeError(
            "No se rechazó la segunda devolución acumulada de tarjeta (300 + 600 > 750): "
            + json.dumps(initial_payload, ensure_ascii=False)
        )
    if "El total reintegrado por medio de pago supera el importe cobrado originalmente" not in str(
        initial_payload.get("overLimitMessage") or ""
    ):
        raise RuntimeError(
            "El rechazo acumulado no provino de la restricción global por método: "
            + json.dumps(initial_payload, ensure_ascii=False)
        )
    # The failed APPLY must not leave the just-created native outgoings active.
    # The fixture mirrors DIALOG NOMANAGESESSION: after cancellation, the session
    # still contains its pending changes until they are explicitly cleaned and applied.
    if (
        float(initial_payload.get("activeCashRefundCount") or 0) != 1
        or abs(float(initial_payload.get("activeCashRefundAmount") or 0) - 200) > 0.001
        or float(initial_payload.get("activeCardRefundCount") or 0) != 1
        or abs(float(initial_payload.get("activeCardRefundAmount") or 0) - 300) > 0.001
    ):
        raise RuntimeError(
            "El APPLY rechazado dejó egresos pendientes o alteró los reintegros ya confirmados: "
            + json.dumps(initial_payload, ensure_ascii=False)
        )
    print("UI_CUMULATIVE_REFUNDS_OVER_LIMIT_REJECTED=true")
    print("UI_CUMULATIVE_REFUNDS_REJECTED_APPLY_CLEANED_UP=true")
    print("UI_CUMULATIVE_REFUNDS_INITIAL=" + json.dumps(initial_payload, ensure_ascii=False))

    # Crear una segunda sesión web autenticada. Las dos peticiones usan cookies
    # JSESSIONID distintas para competir desde sesiones del servidor independientes.
    secondary_context = browser.new_context(
        locale="es-AR",
        viewport={"width": 1280, "height": 900},
        color_scheme="light",
    )
    try:
        secondary_page = secondary_context.new_page()
        secondary_response = secondary_page.goto(
            url, wait_until="domcontentloaded", timeout=60_000
        )
        if secondary_response is None or secondary_response.status >= 400:
            raise RuntimeError(
                "La segunda sesión de navegador no pudo abrir la aplicación para la prueba concurrente."
            )
        wait_for_application_server(secondary_page)
        login_to_ephemeral_instance(secondary_page)

        primary_cookie_header, primary_cookie_values = _cookie_header_for_api_context(context, api_base)
        secondary_cookie_header, secondary_cookie_values = _cookie_header_for_api_context(
            secondary_context, api_base
        )
        session_cookie_names = {
            name for name in primary_cookie_values
            if "session" in name.lower() or "jsession" in name.lower()
        } & {
            name for name in secondary_cookie_values
            if "session" in name.lower() or "jsession" in name.lower()
        }
        distinct_session_cookie = any(
            primary_cookie_values[name] != secondary_cookie_values[name]
            for name in session_cookie_names
        )
        if not primary_cookie_header or not secondary_cookie_header or not distinct_session_cookie:
            raise RuntimeError(
                "La prueba concurrente no obtuvo dos cookies de sesión independientes; "
                f"nombres primarios={sorted(primary_cookie_values)}, "
                f"nombres secundarios={sorted(secondary_cookie_values)}."
            )

        # Ambas peticiones compiten por el mismo cupo restante de tarjeta (ARS 450).
        # Cada una pide ARS 300; sólo una puede confirmar bajo SERIALIZABLE.
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="rubrova-refund") as executor:
            future_a = executor.submit(
                _native_api_get_with_cookie_header,
                api_base,
                "rubrovaTestCumulativeRefundRaceAApi",
                primary_cookie_header,
            )
            future_b = executor.submit(
                _native_api_get_with_cookie_header,
                api_base,
                "rubrovaTestCumulativeRefundRaceBApi",
                secondary_cookie_header,
            )
            race_a = future_a.result()
            race_b = future_b.result()
    finally:
        secondary_context.close()

    accepted = [race_a.get("accepted") is True, race_b.get("accepted") is True]
    if sum(accepted) != 1:
        raise RuntimeError(
            "Las dos confirmaciones simultáneas no quedaron serializadas: "
            + json.dumps({"A": race_a, "B": race_b}, ensure_ascii=False)
        )
    rejected = race_b if accepted[0] else race_a
    if rejected.get("accepted") is True:
        raise RuntimeError("La confirmación perdedora informó aceptación.")
    rejection_message = str(rejected.get("applyMessage") or "")
    if "El total reintegrado por medio de pago supera el importe cobrado originalmente" not in rejection_message:
        raise RuntimeError(
            "La confirmación perdedora no fue rechazada por el límite acumulado: "
            + json.dumps({"A": race_a, "B": race_b}, ensure_ascii=False)
        )
    print("UI_CUMULATIVE_REFUNDS_RACE_A=" + json.dumps(race_a, ensure_ascii=False))
    print("UI_CUMULATIVE_REFUNDS_RACE_B=" + json.dumps(race_b, ensure_ascii=False))
    print("UI_CUMULATIVE_REFUNDS_CONCURRENT_SERIALIZED=true")

    finished = context.request.get(
        api_base + "rubrovaTestCumulativeRefundFinishApi", timeout=60_000
    )
    if finished.status != 200:
        raise RuntimeError(
            f"La conciliación final de reintegros mixtos respondió HTTP {finished.status}: "
            f"{finished.text()[:1600]}"
        )
    finished_payload = finished.json()
    if isinstance(finished_payload, list):
        finished_payload = finished_payload[0] if finished_payload else {}
    for field, expected in {
        "activeReturnCount": 3,
        "activeReturnAmount": 1250,
        "returnedQuantity": 1,
        "activeCashRefundAmount": 500,
        "activeCardRefundAmount": 750,
        "cashAccountBalance": 1000,
        "cardAccountBalance": 1000,
    }.items():
        try:
            actual = float(finished_payload.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(f"La conciliación de reintegros devolvió un valor inválido en {field}.") from error
        if abs(actual - expected) > 0.001:
            raise RuntimeError(
                f"La conciliación posterior a la carrera no coincide en {field}: "
                f"esperado {expected}, recibido {actual}. "
                f"{json.dumps(finished_payload, ensure_ascii=False)}"
            )

    # Anular la nota no anula los egresos que ya movieron dinero: el cupo debe seguir ocupado.
    cancelled_bill = context.request.get(
        api_base + "rubrovaTestCumulativeRefundBillCancelApi", timeout=60_000
    )
    if cancelled_bill.status != 200:
        raise RuntimeError(
            f"La prueba de cancelación de nota respondió HTTP {cancelled_bill.status}: "
            f"{cancelled_bill.text()[:1600]}"
        )
    cancelled_payload = cancelled_bill.json()
    if isinstance(cancelled_payload, list):
        cancelled_payload = cancelled_payload[0] if cancelled_payload else {}
    if (
        cancelled_payload.get("originalBillCanceled") is not True
        or cancelled_payload.get("originalBillReady") is not True
        or cancelled_payload.get("originalBillActivityState") != "inactive"
        or float(cancelled_payload.get("originalBillOutgoingActiveCount") or 0) != 2
        or cancelled_payload.get("overLimitRejected") is not True
        or abs(float(cancelled_payload.get("cashAccountBalance") or 0) - 1000) > 0.001
        or abs(float(cancelled_payload.get("cardAccountBalance") or 0) - 1000) > 0.001
    ):
        raise RuntimeError(
            "La cancelación de la nota no conservó su estado nativo, los egresos activos o el cupo: "
            + json.dumps(cancelled_payload, ensure_ascii=False)
        )
    if "El total reintegrado por medio de pago supera el importe cobrado originalmente" not in str(
        cancelled_payload.get("overLimitMessage") or ""
    ):
        raise RuntimeError(
            "El rechazo tras cancelar sólo la nota no provino del límite acumulado: "
            + json.dumps(cancelled_payload, ensure_ascii=False)
        )
    print("UI_CUMULATIVE_REFUNDS_BILL_CANCEL_DOES_NOT_RELEASE_CAP=true")

    # Cancelar los dos egresos nativos libera sólo esos importes; la nota histórica permanece.
    released = context.request.get(
        api_base + "rubrovaTestCumulativeRefundReleaseApi", timeout=60_000
    )
    if released.status != 200:
        raise RuntimeError(
            f"La liberación del cupo por cancelación de egresos respondió HTTP {released.status}: "
            f"{released.text()[:1600]}"
        )
    released_payload = released.json()
    if isinstance(released_payload, list):
        released_payload = released_payload[0] if released_payload else {}
    expected_release = {
        "originalBillOutgoingActiveCount": 0,
        "activeReturnCount": 3,
        "activeReturnAmount": 1250,
        "returnedQuantity": 1,
        "activeCashRefundCount": 2,
        "activeCashRefundAmount": 500,
        "activeCardRefundCount": 3,
        "activeCardRefundAmount": 750,
        "cashAccountBalance": 1000,
        "cardAccountBalance": 1000,
        "onHand": 10,
    }
    for field, expected in expected_release.items():
        try:
            actual = float(released_payload.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(f"La liberación de cupo devolvió un valor no numérico en {field}.") from error
        if abs(actual - expected) > 0.001:
            raise RuntimeError(
                f"La conciliación tras cancelar egresos no coincide en {field}: "
                f"esperado {expected}, recibido {actual}. "
                f"{json.dumps(released_payload, ensure_ascii=False)}"
            )
    if (
        released_payload.get("originalBillCanceled") is not True
        or released_payload.get("originalBillReady") is not True
        or released_payload.get("originalBillActivityState") != "inactive"
    ):
        raise RuntimeError(
            "La cancelación de egresos alteró incorrectamente el estado histórico de la nota: "
            + json.dumps(released_payload, ensure_ascii=False)
        )
    print("UI_CUMULATIVE_REFUNDS_PAYMENT_CANCEL_RELEASES_CAP=true")
    print("UI_CUMULATIVE_REFUNDS_RECONCILED=true")
    print("UI_CUMULATIVE_REFUNDS_FINAL=" + json.dumps(released_payload, ensure_ascii=False))


def verify_cumulative_refunds_persistence(context: Any, url: str) -> None:
    base = application_endpoint_url(url, "exec/Sales.")
    state = fetch_restart_api_payload(
        context,
        base + "rubrovaCumulativeRefundsReconciliationApi",
        "cumulative refunds",
    )
    expected = {
        "sourceInvoiceFound": 1,
        "originalCashPaid": 500,
        "originalCardPaid": 750,
        "originalBillOutgoingActiveCount": 0,
        "activeReturnCount": 3,
        "activeReturnAmount": 1250,
        "returnedQuantity": 1,
        "activeCashRefundCount": 2,
        "activeCashRefundAmount": 500,
        "activeCardRefundCount": 3,
        "activeCardRefundAmount": 750,
        "cashAccountBalance": 1000,
        "cardAccountBalance": 1000,
        "onHand": 10,
    }
    for field, wanted in expected.items():
        try:
            actual = float(state.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(f"El estado de reintegros acumulados no es numérico en {field}.") from error
        if abs(actual - wanted) > 0.001:
            raise RuntimeError(
                f"El reintegro acumulado no sobrevivió al reinicio en {field}: "
                f"esperado {wanted}, recibido {actual}. "
                f"{json.dumps(state, ensure_ascii=False)}"
            )
    if (
        state.get("originalBillCanceled") is not True
        or state.get("originalBillReady") is not True
        or state.get("originalBillActivityState") != "inactive"
    ):
        raise RuntimeError(
            "El estado nativo de cancelación de la nota no sobrevivió al reinicio: "
            + json.dumps(state, ensure_ascii=False)
        )
    print("UI_RESTART_PERSISTENCE_CUMULATIVE_REFUNDS=true")

def verify_partial_returns(context: Any, url: str) -> None:
    """Exercise partial returns, a rejected over-return, refunds and stock receipt in disposable CI data."""
    api_base = application_endpoint_url(url, "exec/Sales.")
    response = context.request.get(
        api_base + "rubrovaTestPartialReturnsApi",
        timeout=60_000,
    )
    if response.status != 200:
        raise RuntimeError(
            "El flujo transaccional de devoluciones parciales respondió "
            f"HTTP {response.status}: {response.text()[:1600]}"
        )
    content_type = response.headers.get("content-type", "")
    response_body = response.text()
    print("UI_PARTIAL_RETURNS_RESPONSE_CONTENT_TYPE=" + content_type)
    print("UI_PARTIAL_RETURNS_RESPONSE_BODY=" + repr(response_body[:2000]))
    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "La API de devoluciones respondió HTTP 200 pero no entregó JSON válido. "
            f"Content-Type={content_type!r}; cuerpo={response_body[:2000]!r}"
        ) from error
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    if not isinstance(payload, dict):
        raise RuntimeError(
            "La API de devoluciones no devolvió un objeto JSON: "
            + repr(payload)[:2000]
        )
    expected = {
        "overReturnRejected": True,
        "returnBillCount": 2,
        "returnAmount": 1250,
        "returnedQuantity": 1,
        "cashRefundPaymentCount": 2,
        "cashRefundPaymentAmount": 1250,
        "sessionCashNet": 0,
        "cashBalance": 0,
        "onHand": 10,
    }
    for field, wanted in expected.items():
        actual = payload.get(field)
        if isinstance(wanted, bool):
            if actual is not wanted:
                raise RuntimeError(
                    f"La devolución parcial no confirmó {field}: esperado {wanted!r}, "
                    f"recibido {actual!r}. Respuesta: {json.dumps(payload, ensure_ascii=False)}"
                )
            continue
        try:
            numeric_actual = float(actual or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(
                f"La conciliación de devoluciones devolvió un valor inválido en {field}: {actual!r}"
            ) from error
        if abs(numeric_actual - wanted) > 0.001:
            raise RuntimeError(
                f"La devolución parcial no quedó conciliada en {field}: esperado {wanted}, "
                f"recibido {numeric_actual}. Respuesta: {json.dumps(payload, ensure_ascii=False)}"
            )

    inventory_response = context.request.get(
        api_base + "rubrovaTestInventoryApi",
        timeout=12_000,
    )
    if inventory_response.status != 200:
        raise RuntimeError(
            "La consulta del inventario después de devolver respondió "
            f"HTTP {inventory_response.status}: {inventory_response.text()[:1200]}"
        )
    inventory = inventory_response.json()
    if isinstance(inventory, list):
        inventory = inventory[0] if inventory else {}
    for field, wanted in {"incomingQuantity": 11, "outgoingQuantity": 1, "onHand": 10}.items():
        try:
            actual = float(inventory.get(field) or 0)
        except (TypeError, ValueError) as error:
            raise RuntimeError(
                f"El ledger de inventario devolvió un valor inválido para {field}: "
                f"{inventory.get(field)!r}"
            ) from error
        if abs(actual - wanted) > 0.001:
            raise RuntimeError(
                f"El recibo de devolución no reingresó el stock en {field}: esperado {wanted}, "
                f"recibido {actual}. Inventario: {json.dumps(inventory, ensure_ascii=False)}"
            )

    print("UI_PARTIAL_RETURNS_RECONCILIATION=" + json.dumps(payload, ensure_ascii=False))
    print("UI_PARTIAL_RETURNS_INVENTORY=" + json.dumps(inventory, ensure_ascii=False))
    print("UI_PARTIAL_RETURNS_OVER_RETURN_REJECTED=true")
    print("UI_PARTIAL_RETURNS_REMAINING_QUANTITY_RECONCILED=true")
    print("UI_PARTIAL_RETURNS_REFUNDS_RECONCILED=true")
    print("UI_PARTIAL_RETURNS_STOCK_REENTERED=true")
    print("UI_PARTIAL_RETURNS_RECONCILED=true")

def _stocktake_api_payload(context: Any, endpoint: str, label: str) -> dict[str, Any]:
    response = context.request.get(endpoint, timeout=20_000)
    if response.status != 200:
        raise RuntimeError(
            f"La prueba de stocktake ({label}) respondió HTTP {response.status}: "
            f"{response.text()[:1200]}"
        )
    try:
        payload = response.json()
    except ValueError as error:
        raise RuntimeError(
            f"La prueba de stocktake ({label}) no devolvió JSON válido: {response.text()[:1200]!r}"
        ) from error
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"La prueba de stocktake ({label}) devolvió {type(payload).__name__}, no un objeto JSON."
        )
    print(f"UI_STOCKTAKE_BARCODE_{label.upper()}_PAYLOAD=" + json.dumps(payload, ensure_ascii=False))
    return payload


def _stocktake_number(payload: dict[str, Any], field: str, label: str) -> float:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise RuntimeError(f"Stocktake {label}.{field} debe ser un número finito; recibido {value!r}.")
    return float(value)


def verify_stocktake_barcode_semantics(context: Any, url: str) -> None:
    """Exercise MyCompany's real barcode quantity helper against disposable, unvalidated data."""
    api_base = application_endpoint_url(url, "exec/Sales.")

    zero = _stocktake_api_payload(
        context, api_base + "rubrovaTestStocktakeBarcodeZeroApi", "zero"
    )
    for field in ("listLineCount", "adjustmentLineCount"):
        actual = _stocktake_number(zero, field, "zero")
        if actual != 1:
            raise RuntimeError(
                f"Stocktake cero: {field} debe ser 1, se obtuvo {actual}. "
                + json.dumps(zero, ensure_ascii=False)
            )
    if zero.get("zeroQuantityPreserved") is not True:
        raise RuntimeError(
            "La captura por barcode perdió el cero en AdjustmentListLine: "
            + json.dumps(zero, ensure_ascii=False)
        )
    if zero.get("adjustmentQuantityIsZero") is not True:
        raise RuntimeError(
            "La cantidad cero no llegó a la línea principal de Adjustment: "
            + json.dumps(zero, ensure_ascii=False)
        )
    if abs(_stocktake_number(zero, "onHand", "zero") - 10.0) > 0.001:
        raise RuntimeError(
            "El conteo descartable alteró el stock físico al guardar cero: "
            + json.dumps(zero, ensure_ascii=False)
        )
    print("UI_STOCKTAKE_BARCODE_ZERO_PRESERVED=true")

    cleared = _stocktake_api_payload(
        context, api_base + "rubrovaTestStocktakeBarcodeNullApi", "null"
    )
    if _stocktake_number(cleared, "listLineCount", "null") != 0:
        raise RuntimeError(
            "Enviar NULL al barcode no eliminó la fila de la hoja de conteo: "
            + json.dumps(cleared, ensure_ascii=False)
        )
    if _stocktake_number(cleared, "adjustmentLineCount", "null") != 1:
        raise RuntimeError(
            "Borrar la hoja eliminó la línea padre nativa en vez de dejarla sin cantidad: "
            + json.dumps(cleared, ensure_ascii=False)
        )
    if cleared.get("adjustmentQuantityIsNull") is not True:
        raise RuntimeError(
            "Enviar NULL al barcode no limpió la cantidad de AdjustmentLine: "
            + json.dumps(cleared, ensure_ascii=False)
        )
    if abs(_stocktake_number(cleared, "onHand", "null") - 10.0) > 0.001:
        raise RuntimeError(
            "El conteo descartable alteró el stock físico al borrar la fila: "
            + json.dumps(cleared, ensure_ascii=False)
        )
    print("UI_STOCKTAKE_BARCODE_NULL_CLEARED=true")

    positive = _stocktake_api_payload(
        context, api_base + "rubrovaTestStocktakeBarcodePositiveApi", "positive"
    )
    for field in ("listLineCount", "adjustmentLineCount"):
        actual = _stocktake_number(positive, field, "positive")
        if actual != 1:
            raise RuntimeError(
                f"Stocktake positivo: {field} debe ser 1, se obtuvo {actual}. "
                + json.dumps(positive, ensure_ascii=False)
            )
    for field in ("listQuantity", "adjustmentLineQuantity"):
        actual = _stocktake_number(positive, field, "positive")
        if abs(actual - 2.0) > 0.001:
            raise RuntimeError(
                f"Stocktake positivo: {field} debe ser 2, se obtuvo {actual}. "
                + json.dumps(positive, ensure_ascii=False)
            )
    if abs(_stocktake_number(positive, "onHand", "positive") - 10.0) > 0.001:
        raise RuntimeError(
            "El conteo descartable alteró el stock físico al guardar cantidad positiva: "
            + json.dumps(positive, ensure_ascii=False)
        )
    print("UI_STOCKTAKE_BARCODE_AGGREGATE_RECONCILED=true")


def verify_stocktake_persistence(context: Any, url: str) -> None:
    base = application_endpoint_url(url, "exec/Sales.")
    state = fetch_restart_api_payload(
        context,
        base + "rubrovaTestStocktakeBarcodeStateApi",
        "stocktake",
    )
    if abs(_stocktake_number(state, "onHand", "restart") - 10.0) > 0.001:
        raise RuntimeError(
            "El conteo pendiente alteró el stock físico tras reiniciar; se esperaba 10 "
            "después de la venta y las devoluciones POS: " + json.dumps(state, ensure_ascii=False)
        )
    for field in ("listLineCount", "adjustmentLineCount"):
        actual = _stocktake_number(state, field, "restart")
        if actual != 1:
            raise RuntimeError(
                f"El conteo no sobrevivió al reinicio en {field}: {actual}. "
                + json.dumps(state, ensure_ascii=False)
            )
    for field in ("listQuantity", "adjustmentLineQuantity"):
        actual = _stocktake_number(state, field, "restart")
        if abs(actual - 2.0) > 0.001:
            raise RuntimeError(
                f"El conteo no sobrevivió al reinicio en {field}: {actual}. "
                + json.dumps(state, ensure_ascii=False)
            )
    print("UI_RESTART_PERSISTENCE_STOCKTAKE=true")

def inspect_page(url: str) -> int:
    screenshot_path = Path(
        os.environ.get("RUBROVA_UI_SCREENSHOT", "/tmp/rubrova-mycompany-ui.png")
    )
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    after_login_screenshot = screenshot_path.with_name(
        screenshot_path.stem + "-after-login" + screenshot_path.suffix
    )
    retail_screenshot = screenshot_path.with_name(
        screenshot_path.stem + "-retail" + screenshot_path.suffix
    )
    pos_screenshot = screenshot_path.with_name(
        screenshot_path.stem + "-pos" + screenshot_path.suffix
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            locale="es-AR",
            viewport={"width": 1440, "height": 1000},
            color_scheme="light",
        )
        page = context.new_page()
        page.set_default_timeout(10_000)
        browser_diagnostics = attach_browser_diagnostics(page)

        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            status = response.status if response else None
            if status is None or status >= 400:
                raise RuntimeError(f"La página inicial respondió HTTP {status}.")

            try:
                page.wait_for_load_state("networkidle", timeout=8_000)
            except PlaywrightTimeoutError:
                # lsFusion may keep a live connection open; DOM readiness is enough.
                pass
            page.wait_for_timeout(1_000)

            print(f"UI_HTTP_STATUS={status}")
            if os.environ.get("RUBROVA_UI_TEST_LOGIN", "false").lower() == "true":
                initial_text = wait_for_application_server(page)
            else:
                initial_text = page.locator("body").inner_text(timeout=10_000)
            initial_text = visible_snapshot(page, "UI_INITIAL")
            initial_lines = {line.strip() for line in initial_text.splitlines()}
            legacy_login_phrases = (
                "Sign in", "LOGIN", "PASSWORD", "Forgot password",
                "Don't have account?", "Sign up", "Run desktop client"
            )
            present_legacy_login = [
                phrase for phrase in legacy_login_phrases if phrase in initial_text
            ]
            if present_legacy_login:
                raise RuntimeError(
                    "La pantalla de acceso conserva textos en inglés: "
                    + ", ".join(present_legacy_login)
                )
            for required_label in (
                "Ingresar", "USUARIO", "CONTRASEÑA",
                "¿Olvidaste tu contraseña?", "Registrarse",
                "Abrir cliente de escritorio"
            ):
                if required_label not in initial_text:
                    raise RuntimeError(
                        f"Falta el texto localizado en la pantalla de acceso: {required_label!r}"
                    )
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"UI_INITIAL_SCREENSHOT={screenshot_path}")

            if os.environ.get("RUBROVA_UI_TEST_LOGIN", "false").lower() == "true":
                final_text = login_to_ephemeral_instance(page)
                print(
                    "UI_LOGIN_STATUS=authenticated:"
                    + os.environ.get("RUBROVA_UI_TEST_USERNAME", "admin")
                )
                home_text = visible_snapshot(page, "UI_AFTER_LOGIN")
                home_lines = {line.strip() for line in home_text.splitlines()}
                legacy_navigation_labels = {
                    "Master data", "Auto theme", "Pin navbar", "Attributes", "Numerators", "Design"
                }
                present_legacy_navigation = sorted(legacy_navigation_labels.intersection(home_lines))
                if present_legacy_navigation:
                    raise RuntimeError(
                        "La navegación general conserva textos en inglés: "
                        + ", ".join(present_legacy_navigation)
                    )
                for required_label in (
                    "Datos maestros", "Atributos", "Numeradores", "Tema automático", "Fijar barra de navegación", "Diseño"
                ):
                    if required_label not in home_lines:
                        raise RuntimeError(
                            f"Falta el texto localizado en la navegación: {required_label!r}"
                        )
                page.screenshot(path=str(after_login_screenshot), full_page=True)
                print(f"UI_HOME_SCREENSHOT={after_login_screenshot}")
                verify_replenishment_source_export(context, url)
                if os.environ.get("RUBROVA_UI_DEMO_MODE", "false").lower() != "true":
                    verify_return_quantity_guard(context, url)
                    verify_stocktake_barcode_semantics(context, url)
                if not final_text.strip():
                    raise RuntimeError("La pantalla posterior al acceso está vacía.")

                if os.environ.get("RUBROVA_UI_STOP_AFTER_LOGIN", "false").lower() == "true":
                    print("UI_LOGIN_AND_LOCAL_NAVIGATION_VERIFIED=true")
                    return 0

                if os.environ.get("RUBROVA_UI_VERIFY_PERSISTED_ONLY", "false").lower() == "true":
                    verify_restarted_persistence(context, url)
                    print("UI_RESTART_PERSISTENCE_VERIFIED=true")
                    return 0

                # El servidor corre sobre PostgreSQL descartable de CI; el turno y sus datos se destruyen al finalizar.
                if not click_exact_link(page, "Comercio", submenu_label="Punto de venta"):
                    page.screenshot(path=str(retail_screenshot), full_page=True)
                    print(f"UI_RETAIL_SCREENSHOT={retail_screenshot}")
                    raise RuntimeError("El menú Comercio no se expandió para mostrar 'Punto de venta'.")

                visible_snapshot(page, "UI_RETAIL_NAVIGATION")
                page.screenshot(path=str(retail_screenshot), full_page=True)
                print(f"UI_RETAIL_SCREENSHOT={retail_screenshot}")

                if not click_exact_link(page, "Punto de venta"):
                    raise RuntimeError("La opción 'Punto de venta' desapareció antes de abrirse.")

                # The isolated demo database seeds a distinct POS name from the CI sales fixture.
                pos_register_name = os.environ.get(
                    "RUBROVA_UI_POS_REGISTER_NAME", "Caja de prueba Rubrova"
                ).strip()
                if not pos_register_name:
                    raise RuntimeError("RUBROVA_UI_POS_REGISTER_NAME no puede estar vacío.")

                # The menu click can return before the GWT form finishes rendering.
                pos_text = wait_until_form_loaded(
                    page,
                    "UI_POS_SCREEN",
                    timeout_seconds=45,
                    register_name=pos_register_name,
                )
                visible_snapshot(page, "UI_POS_SCREEN")
                page.screenshot(path=str(pos_screenshot), full_page=True)
                print(f"UI_POS_SCREENSHOT={pos_screenshot}")
                print("UI_POS_SCREEN_AVAILABLE=true")
                if not pos_text.strip():
                    raise RuntimeError("La pantalla POS se abrió, pero no mostró contenido.")

                select_pos_register(page, pos_register_name)

                markdown_requests = browser_diagnostics["markdown_requests"]
                print(f"UI_MARKDOWN_EXTERNAL_REQUESTS_DURING_POS={len(markdown_requests)}")
                if markdown_requests:
                    raise RuntimeError(
                        "El inicio del POS descargó el visor Markdown externo: "
                        + json.dumps(markdown_requests, ensure_ascii=False)
                    )
                print("UI_MARKDOWN_DEPENDENCIES_LAZY_LOADED=true")

                # Abrir un turno en la base efímera de CI; la venta sintética se confirmará explícitamente más adelante.
                if not click_exact_action(page, "Abrir turno"):
                    raise RuntimeError("El botón 'Abrir turno' no estaba disponible para la prueba aislada.")
                wait_for_session_open(page, timeout_seconds=45)

                demo_mode = os.environ.get("RUBROVA_UI_DEMO_MODE", "false").lower() == "true"
                if demo_mode:
                    # The persistent local demo intentionally loads no CI-only API modules.
                    # Its fixture has one POS; select_pos_register verified its exact unique
                    # value and wait_for_session_open verified the native open-session action.
                    print("UI_POS_SESSION_SELECTION_API=skipped_single_register_demo")
                    print("UI_POS_SESSION_SELECTION_CONFIRMED_BY_UI=true")
                else:
                    # The CI sales fixture has two POS registers, so verify the selected
                    # register against MyCompany's persisted session state before selling.
                    session_api_base = application_endpoint_url(url, "exec/Sales.")
                    session_selection_response = context.request.get(
                        session_api_base + "rubrovaTestPosSessionSelectionApi", timeout=12_000
                    )
                    if session_selection_response.status != 200:
                        raise RuntimeError(
                            "La comprobación de selección de caja respondió HTTP "
                            f"{session_selection_response.status}: {session_selection_response.text()[:1200]}"
                        )
                    session_selection = session_selection_response.json()
                    if isinstance(session_selection, list):
                        session_selection = session_selection[0] if session_selection else {}
                    print("UI_POS_SESSION_SELECTION=" + json.dumps(session_selection, ensure_ascii=False))
                    main_open_sessions = int(session_selection.get("mainOpenSessions") or 0)
                    refund_open_sessions = int(session_selection.get("refundOpenSessions") or 0)
                    if main_open_sessions != 1 or refund_open_sessions != 0:
                        raise RuntimeError(
                            "El turno se abrió en un puesto POS distinto del solicitado: "
                            f"mainOpenSessions={main_open_sessions}, "
                            f"refundOpenSessions={refund_open_sessions}, "
                            f"detalle={json.dumps(session_selection, ensure_ascii=False)}"
                        )
                    print("UI_POS_SESSION_BOUND_TO_REQUESTED_REGISTER=true")
                session_screenshot = screenshot_path.with_name(
                    screenshot_path.stem + "-session" + screenshot_path.suffix
                )
                session_text = visible_snapshot(page, "UI_SESSION_OPEN")
                legacy_pos_labels = {"By order", "Discount, %", "Delete", "Date", "Unknown"}
                session_lines = {line.strip() for line in session_text.splitlines()}
                present_legacy_labels = sorted(legacy_pos_labels.intersection(session_lines))
                if present_legacy_labels:
                    raise RuntimeError(
                        "La pantalla de turno conserva captions en inglés: "
                        + ", ".join(present_legacy_labels)
                    )
                for required_caption in ("Por pedido", "Desc. %", "Eliminar", "Fecha", "Consumidor final", "Nº", "Cant.", "P. c/desc."):
                    if required_caption not in session_lines:
                        raise RuntimeError(
                            f"Falta el caption español requerido en el POS: {required_caption!r}"
                        )
                page.screenshot(path=str(session_screenshot), full_page=True)
                print(f"UI_SESSION_SCREENSHOT={session_screenshot}")

                # Primer paso comercial: buscar el producto ficticio y agregarlo al recibo.
                search_tab = page.get_by_text("Buscar artículos", exact=True)
                search_tab.wait_for(state="visible", timeout=15_000)
                search_tab.click(no_wait_after=True)
                print("UI_ITEM_SEARCH_TAB_CLICKED=true")
                search_text = visible_snapshot(page, "UI_ITEM_SEARCH")
                legacy_search_labels = {"Price (F7)", "Name (full)", "Reference", "Quantity", "Price"}
                search_lines = {line.strip() for line in search_text.splitlines()}
                present_search_labels = sorted(legacy_search_labels.intersection(search_lines))
                if present_search_labels:
                    raise RuntimeError(
                        "La búsqueda del POS conserva captions en inglés: "
                        + ", ".join(present_search_labels)
                    )
                for required_caption in ("Precio (F7)", "Nombre completo", "Referencia", "Cant.", "Precio", "Disp."):
                    if required_caption not in search_lines:
                        raise RuntimeError(
                            f"Falta el caption español en la búsqueda del POS: {required_caption!r}"
                        )

                product_name = (
                    "Producto de demostración Rubrova"
                    if demo_mode
                    else "Producto de prueba Rubrova"
                )
                product_result = page.get_by_text(product_name, exact=True)
                try:
                    product_result.first.wait_for(state="visible", timeout=15_000)
                except PlaywrightTimeoutError as error:
                    print("UI_TEST_PRODUCT_FOUND=false")
                    print(
                        "UI_ITEM_SEARCH_VISIBLE_TEXT="
                        + page.locator("body").inner_text(timeout=5_000)[:5000]
                    )
                    print(
                        "UI_ITEM_SEARCH_INPUTS="
                        + json.dumps(
                            page.locator("input").evaluate_all(
                                """elements => elements.slice(0, 60).map(element => ({
                                    value: element.value || "",
                                    type: element.type || "",
                                    visible: !!(element.offsetWidth || element.offsetHeight),
                                    outerHTML: element.outerHTML.slice(0, 600),
                                    parentText: element.parentElement
                                        ? (element.parentElement.innerText || "").trim().slice(0, 300)
                                        : ""
                                }))"""
                            ),
                            ensure_ascii=False
                        )
                    )
                    raise RuntimeError(
                        "El producto sintético no apareció en la búsqueda del POS; "
                        "no se puede validar el catálogo."
                    ) from error

                search_match_count = product_result.count()
                print(f"UI_TEST_PRODUCT_FOUND=true")
                print(f"UI_TEST_PRODUCT_SEARCH_MATCHES={search_match_count}")
                if search_match_count != 1:
                    raise RuntimeError(
                        "La búsqueda debe devolver exactamente un artículo de prueba; "
                        f"devolvió {search_match_count}."
                    )

                if demo_mode:
                    demo_screenshot = screenshot_path.with_name(
                        screenshot_path.stem + "-demo" + screenshot_path.suffix
                    )
                    print("UI_LOCAL_DEMO_SESSION_OPEN=true")
                    print("UI_LOCAL_DEMO_PRODUCT_FOUND=true")
                    print(f"UI_LOCAL_DEMO_PRODUCT_NAME={product_name}")
                    visible_snapshot(page, "UI_LOCAL_DEMO_PRODUCT")
                    page.screenshot(path=str(demo_screenshot), full_page=True)
                    print(f"UI_LOCAL_DEMO_SCREENSHOT={demo_screenshot}")
                    return 0

                # MyCompany implementa la selección mediante selectPosSearch, expuesta
                # como acción de toolbar "Select (DBLCLK)". Ver el artículo en searchItems
                # no demuestra que se haya creado una línea en el recibo.
                product_result.first.click(no_wait_after=True)
                print("UI_TEST_PRODUCT_ROW_SELECTED=true")
                if not click_exact_action(page, "Select (DBLCLK)"):
                    raise RuntimeError(
                        "El artículo quedó seleccionado en la búsqueda, pero no se pudo "
                        "ejecutar la acción nativa Select (DBLCLK) de MyCompany."
                    )
                print("UI_TEST_PRODUCT_SELECTION_ACTION_CLICKED=true")

                receipt_grid = page.locator('[lsfusion-container="GRID(l)"]')
                try:
                    receipt_grid.wait_for(state="visible", timeout=15_000)
                except PlaywrightTimeoutError as error:
                    print(f"UI_RECEIPT_GRID_MATCH_COUNT={receipt_grid.count()}")
                    visible_snapshot(page, "UI_RECEIPT_GRID_NOT_AVAILABLE")
                    raise RuntimeError(
                        "No apareció el grid de líneas del recibo (GRID(l)); "
                        "el resultado de búsqueda no demuestra una venta."
                    ) from error

                cart_deadline = time.monotonic() + 20
                receipt_rows: list[str] = []
                product_rows: list[str] = []
                receipt_digits = ""
                while time.monotonic() < cart_deadline:
                    receipt_rows = receipt_grid.locator(
                        "tr.data-grid-row:not(.data-grid-column-row)"
                    ).all_inner_texts()
                    product_rows = [row for row in receipt_rows if product_name in row]
                    receipt_digits = "".join(
                        character for row in product_rows for character in row
                        if character.isdigit()
                    )
                    if len(product_rows) == 1 and "1250" in receipt_digits:
                        break
                    page.wait_for_timeout(500)

                print(f"UI_RECEIPT_GRID_MATCH_COUNT={receipt_grid.count()}")
                print(f"UI_RECEIPT_LINE_COUNT={len(receipt_rows)}")
                print(f"UI_RECEIPT_PRODUCT_LINE_COUNT={len(product_rows)}")
                print("UI_RECEIPT_PRODUCT_LINES=" + json.dumps(receipt_rows, ensure_ascii=False))
                if len(product_rows) != 1 or "1250" not in receipt_digits:
                    raise RuntimeError(
                        "El producto no quedó confirmado como una única línea del recibo "
                        "con precio 1250. No se acepta como prueba que siga visible en "
                        "la tabla de búsqueda. "
                        f"Líneas del recibo: {json.dumps(receipt_rows, ensure_ascii=False)}"
                    )

                print("UI_TEST_PRODUCT_ADDED_TO_RECEIPT=true")

                # Leer la configuración efectiva del POS desde el servidor antes de comprobar el cobro.
                api_base = application_endpoint_url(url, "exec/Rubrova.")
                pos_config_response = context.request.get(
                    api_base + "rubrovaTestPosConfigurationApi", timeout=12_000
                )
                if pos_config_response.status != 200:
                    raise RuntimeError(
                        "El diagnóstico de configuración POS respondió HTTP "
                        f"{pos_config_response.status}: {pos_config_response.text()[:1200]}"
                    )
                pos_config_payload = pos_config_response.json()
                if isinstance(pos_config_payload, list):
                    pos_config_payload = pos_config_payload[0] if pos_config_payload else {}
                print("UI_POS_EFFECTIVE_CONFIGURATION=" + json.dumps(pos_config_payload, ensure_ascii=False))

                # 6.x upstream agregó este invariante: cuenta central != cajón de efectivo.
                central_cash_account = str(pos_config_payload.get("centralCashAccountName") or "").strip()
                till_cash_account = str(pos_config_payload.get("cashAccountName") or "").strip()
                if not central_cash_account or not till_cash_account:
                    raise RuntimeError("El POS no informó las dos cuentas de efectivo configuradas.")
                if central_cash_account == till_cash_account:
                    raise RuntimeError(
                        "Configuración inválida: la cuenta central no puede ser también el cajón de efectivo."
                    )
                print("UI_POS_CASH_ACCOUNTS_DISTINCT=true")

                # Abrir la pantalla de cobro y verificar medios disponibles sin confirmar.
                if not click_exact_action(page, "Cobrar (ctrl ENTER)"):
                    raise RuntimeError("No se encontró la acción Cobrar después de agregar el artículo.")
                payment_text = wait_for_payment_dialog(page, timeout_seconds=20)
                payment_text = visible_snapshot(page, "UI_PAYMENT_DIALOG")
                payment_snapshot = screenshot_path.with_name(
                    screenshot_path.stem + "-payment" + screenshot_path.suffix
                )
                page.screenshot(path=str(payment_snapshot), full_page=True)
                print(f"UI_PAYMENT_SCREENSHOT={payment_snapshot}")
                normalized_payment_text = payment_text.casefold()
                if not any(label in normalized_payment_text for label in ("efectivo", "cash")):
                    raise RuntimeError(
                        "La pantalla de cobro se abrió, pero no muestra el medio de pago efectivo. "
                        f"Texto visible: {payment_text.strip()[:3000]}"
                    )
                print("UI_PAYMENT_DIALOG_OPEN=true")
                print("UI_PAYMENT_CASH_METHOD_AVAILABLE=true")

                # Efectivo queda preseleccionado en MyCompany; al confirmar, el módulo original
                # asigna el total pendiente al medio seleccionado y crea el pago vinculado.
                if not click_exact_action(page, "Ok (ctrl ENTER)"):
                    raise RuntimeError("No se encontró la confirmación del diálogo de cobro.")
                print("UI_PAYMENT_CONFIRM_ACTION_CLICKED=true")
                page.get_by_text("Cobrar (ctrl ENTER)", exact=True).wait_for(
                    state="visible", timeout=30_000
                )
                print("UI_PAYMENT_CONFIRMED=true")

                # Estas acciones del fixture están declaradas en NAMESPACE Sales.
                sales_api_base = application_endpoint_url(url, "exec/Sales.")

                # Conciliar la factura y el pago persistidos, no sólo el cierre visual del diálogo.
                sales_payload: dict[str, Any] = {}
                sales_deadline = time.monotonic() + 30
                while time.monotonic() < sales_deadline:
                    sales_response = context.request.get(
                        sales_api_base + "rubrovaTestSalesReconciliationApi", timeout=12_000
                    )
                    if sales_response.status != 200:
                        raise RuntimeError(
                            "La conciliación de la venta respondió HTTP "
                            f"{sales_response.status}: {sales_response.text()[:1200]}"
                        )
                    sales_payload = sales_response.json()
                    if isinstance(sales_payload, list):
                        sales_payload = sales_payload[0] if sales_payload else {}
                    if int(sales_payload.get("salesCount") or 0) == 1:
                        break
                    page.wait_for_timeout(750)

                print("UI_SALE_RECONCILIATION=" + json.dumps(sales_payload, ensure_ascii=False))
                expected_sales = {
                    "salesCount": 1,
                    "paidSalesCount": 1,
                    "invoiceAmount": 1250,
                    "paidAmount": 1250,
                    "cashPaidAmount": 1250,
                    "incomingPaymentCount": 1,
                    "sessionCashPaid": 1250,
                    "cashBalance": 1250,
                }
                for field, expected in expected_sales.items():
                    try:
                        actual = float(sales_payload.get(field) or 0)
                    except (TypeError, ValueError) as error:
                        raise RuntimeError(
                            f"La conciliación devolvió un valor no numérico para {field}: "
                            f"{sales_payload.get(field)!r}"
                        ) from error
                    if abs(actual - expected) > 0.001:
                        raise RuntimeError(
                            f"La venta no quedó conciliada en {field}: "
                            f"esperado {expected}, recibido {actual}. "
                            f"Respuesta: {json.dumps(sales_payload, ensure_ascii=False)}"
                        )
                print("UI_SALE_DOCUMENT_CREATED=true")
                print("UI_SALE_PAYMENT_RECONCILED=true")
                print("UI_SALE_CASH_BALANCE_RECONCILED=true")

                # El despacho minorista original debe descontar una unidad del ledger del depósito.
                inventory_payload: dict[str, Any] = {}
                inventory_deadline = time.monotonic() + 30
                while time.monotonic() < inventory_deadline:
                    inventory_response = context.request.get(
                        sales_api_base + "rubrovaTestInventoryApi", timeout=12_000
                    )
                    if inventory_response.status != 200:
                        raise RuntimeError(
                            "La consulta del inventario respondió HTTP "
                            f"{inventory_response.status}: {inventory_response.text()[:1200]}"
                        )
                    inventory_payload = inventory_response.json()
                    if isinstance(inventory_payload, list):
                        inventory_payload = inventory_payload[0] if inventory_payload else {}
                    try:
                        outgoing = float(inventory_payload.get("outgoingQuantity") or 0)
                        on_hand = float(inventory_payload.get("onHand") or 0)
                    except (TypeError, ValueError):
                        outgoing = on_hand = -1
                    if abs(outgoing - 1) <= 0.001 and abs(on_hand - 9) <= 0.001:
                        break
                    page.wait_for_timeout(750)

                print("UI_SALE_INVENTORY_RECONCILIATION=" + json.dumps(inventory_payload, ensure_ascii=False))
                expected_inventory = {
                    "incomingQuantity": 10,
                    "outgoingQuantity": 1,
                    "onHand": 9,
                }
                for field, expected in expected_inventory.items():
                    try:
                        actual = float(inventory_payload.get(field) or 0)
                    except (TypeError, ValueError) as error:
                        raise RuntimeError(
                            f"El inventario devolvió un valor no numérico para {field}: "
                            f"{inventory_payload.get(field)!r}"
                        ) from error
                    if abs(actual - expected) > 0.001:
                        raise RuntimeError(
                            f"El movimiento de inventario no coincide en {field}: "
                            f"esperado {expected}, recibido {actual}. "
                            f"Respuesta: {json.dumps(inventory_payload, ensure_ascii=False)}"
                        )
                print("UI_SALE_STOCK_DEDUCTED=true")

                # Ejecuta el circuito de crédito nativo y comprueba reintegro y reingreso de stock.
                verify_partial_returns(context, url)
                verify_cumulative_refunds(context, url, browser)

                sale_screenshot = screenshot_path.with_name(
                    screenshot_path.stem + "-sale" + screenshot_path.suffix
                )
                visible_snapshot(page, "UI_SALE_CONFIRMED")
                page.screenshot(path=str(sale_screenshot), full_page=True)
                print(f"UI_SALE_SCREENSHOT={sale_screenshot}")

                # Después del cobro, el POS vuelve a dejar activa la pestaña "By order".
                # El cierre pertenece al panel "Turno"; volver a esa pestaña hace visible
                # la acción original sin llamar al cierre por una API auxiliar.
                session_tab_matches = page.get_by_text("Turno", exact=True)
                visible_session_tabs: list[Any] = []
                session_tab_diagnostics: list[dict[str, Any]] = []
                for index in range(session_tab_matches.count()):
                    candidate = session_tab_matches.nth(index)
                    is_visible = candidate.is_visible()
                    candidate_info = candidate.evaluate(
                        """element => {
                            const ancestors = [];
                            for (let node = element, depth = 0; node && depth < 4; node = node.parentElement, depth++) {
                                ancestors.push({
                                    tag: node.tagName.toLowerCase(),
                                    className: typeof node.className === "string" ? node.className : "",
                                    role: node.getAttribute("role") || "",
                                    lsfusionContainer: node.getAttribute("lsfusion-container") || "",
                                    text: (node.innerText || node.textContent || "").trim().slice(0, 100)
                                });
                            }
                            return {
                                tag: element.tagName.toLowerCase(),
                                className: typeof element.className === "string" ? element.className : "",
                                role: element.getAttribute("role") || "",
                                lsfusionContainer: element.getAttribute("lsfusion-container") || "",
                                ancestors
                            };
                        }"""
                    )
                    session_tab_diagnostics.append({**candidate_info, "visible": is_visible})
                    if is_visible:
                        visible_session_tabs.append(candidate)

                print("UI_SESSION_TAB_TOTAL_MATCHES=" + str(session_tab_matches.count()))
                print("UI_SESSION_TAB_VISIBLE_MATCHES=" + str(len(visible_session_tabs)))
                print("UI_SESSION_TAB_CANDIDATES=" + json.dumps(session_tab_diagnostics, ensure_ascii=False))
                if len(visible_session_tabs) != 1:
                    raise RuntimeError(
                        "Se esperaba un único encabezado visible 'Turno' en el POS después del cobro; "
                        f"aparecieron {len(visible_session_tabs)}. "
                        + page.locator("body").inner_text(timeout=5_000)[:1800]
                    )

                # get_by_text encuentra también el nodo del panel oculto conservado por GWT.
                # Elegimos únicamente el encabezado visible de la pestaña, no el texto oculto.
                session_tab = visible_session_tabs[0]
                session_tab.click(no_wait_after=True)
                print("UI_SESSION_TAB_ACTIVATED=true")

                # The native return action belongs to the selected Invoice row in
                # the "Ventas del turno" grid. Capture the actual lsFusion DOM
                # before attempting to automate that action in a separate change.
                sales_list_tab = page.get_by_text("Ventas del turno", exact=True)
                sales_tab_count = sales_list_tab.count()
                print(f"UI_SESSION_SALES_TAB_MATCH_COUNT={sales_tab_count}")
                if sales_tab_count != 1 or not sales_list_tab.is_visible():
                    visible_snapshot(page, "UI_SESSION_SALES_TAB_NOT_UNIQUE")
                    raise RuntimeError(
                        "No se pudo identificar la pestaña nativa única 'Ventas del turno'. "
                        f"coincidencias={sales_tab_count}"
                    )
                sales_list_tab.click(no_wait_after=True)
                print("UI_SESSION_SALES_TAB_ACTIVATED=true")
                visible_snapshot(page, "UI_SESSION_SALES_LIST")
                sales_grid = page.locator('[lsfusion-container="GRID(si)"]')
                print(f"UI_SESSION_SALES_GRID_MATCH_COUNT={sales_grid.count()}")
                if sales_grid.count() == 1:
                    print(f"UI_SESSION_SALES_GRID_VISIBLE={sales_grid.is_visible()}")
                    sales_rows = sales_grid.locator(
                        "tr.data-grid-row:not(.data-grid-column-row)"
                    )
                    print(f"UI_SESSION_SALES_GRID_ROW_COUNT={sales_rows.count()}")
                    print(
                        "UI_SESSION_SALES_GRID_ROWS="
                        + json.dumps(sales_rows.all_inner_texts(), ensure_ascii=False)
                    )
                    print(
                        "UI_SESSION_SALES_GRID_MARKUP="
                        + sales_grid.evaluate("element => element.outerHTML.slice(0, 12000)")
                    )
                return_action = page.locator(
                    'button[lsfusion-container="PROPERTY(return(s, si))"]'
                )
                print(f"UI_SESSION_RETURN_ACTION_MATCH_COUNT={return_action.count()}")
                if return_action.count() == 1:
                    print(f"UI_SESSION_RETURN_ACTION_VISIBLE={return_action.is_visible()}")
                    print(
                        "UI_SESSION_RETURN_ACTION_MARKUP="
                        + return_action.evaluate("element => element.outerHTML.slice(0, 1500)")
                    )
                print(
                    "UI_SESSION_ACTION_CANDIDATES="
                    + json.dumps(
                        page.locator('button, input[type="submit"], [role="button"]').evaluate_all(
                            """elements => elements.map(element => ({
                                text: (element.innerText || element.value || element.textContent || "").trim(),
                                container: element.getAttribute("lsfusion-container") || "",
                                visible: getComputedStyle(element).display !== "none" &&
                                    getComputedStyle(element).visibility !== "hidden" &&
                                    !!(element.offsetWidth || element.offsetHeight),
                                outerHTML: element.outerHTML.slice(0, 600)
                            }))"""
                        ),
                        ensure_ascii=False,
                    )
                )
                print("UI_RETURN_ACTION_DOM_INSPECTED=true")

                close_button = page.locator('button[lsfusion-container="PROPERTY(close(s))"]')
                try:
                    close_button.wait_for(state="visible", timeout=15_000)
                except PlaywrightTimeoutError as error:
                    visible_snapshot(page, "UI_SESSION_TAB_CLOSE_BUTTON_NOT_VISIBLE")
                    raise RuntimeError(
                        "La pestaña 'Turno' se activó, pero el botón nativo 'Cerrar turno' "
                        "sigue oculto."
                    ) from error
                print("UI_SESSION_CLOSE_BUTTON_VISIBLE=true")

                # Cierre nativo de MyCompany: CONFIRM se muestra como MessageBox GWT,
                # no como window.confirm del navegador. Aceptamos el botón afirmativo real.
                if not click_exact_action(page, "Cerrar turno"):
                    raise RuntimeError("No se encontró la acción nativa 'Cerrar turno' de MyCompany.")
                print("UI_SESSION_CLOSE_ACTION_CLICKED=true")
                close_confirmation_message = accept_ls_fusion_confirmation(page, "Cerrar turno")
                if not close_confirmation_message.startswith("¿Confirma que desea ejecutar la acción"):
                    raise RuntimeError(
                        "La confirmación nativa del servidor no está localizada al español: "
                        f"{close_confirmation_message!r}"
                    )
                print("UI_SESSION_CLOSE_CONFIRMATION=" + close_confirmation_message)

                closed_session_payload: dict[str, Any] = {}
                close_deadline = time.monotonic() + 30
                while time.monotonic() < close_deadline:
                    close_response = context.request.get(
                        sales_api_base + "rubrovaTestSessionCloseApi", timeout=12_000
                    )
                    if close_response.status != 200:
                        raise RuntimeError(
                            "La consulta de cierre de turno respondió HTTP "
                            f"{close_response.status}: {close_response.text()[:1200]}"
                        )
                    closed_session_payload = close_response.json()
                    if isinstance(closed_session_payload, list):
                        closed_session_payload = closed_session_payload[0] if closed_session_payload else {}
                    if (
                        closed_session_payload.get("closingDateTime")
                        and closed_session_payload.get("sessionStatus") == "CLOSED"
                    ):
                        break
                    page.wait_for_timeout(750)

                print("UI_SESSION_CLOSE_RECONCILIATION=" + json.dumps(closed_session_payload, ensure_ascii=False))
                if not closed_session_payload.get("sessionNumber"):
                    raise RuntimeError("No se encontró el turno original después de intentar cerrarlo.")
                if not closed_session_payload.get("openingDateTime"):
                    raise RuntimeError("El turno cerrado no conservó su fecha de apertura.")
                if not closed_session_payload.get("closingDateTime"):
                    raise RuntimeError("El cierre nativo no persistió closingDateTime.")
                if closed_session_payload.get("sessionStatus") != "CLOSED":
                    raise RuntimeError(
                        "El turno sigue abierto después de ejecutar Cerrar turno. "
                        f"Estado informado: {closed_session_payload.get('sessionStatus')!r}"
                    )

                expected_close = {
                    "salesCount": 1,
                    "salesAmount": 1250,
                    "returnsCount": 2,
                    "returnsAmount": 1250,
                    "netAmount": 0,
                    "cashPaid": 0,
                    "cashBalance": 0,
                }
                for field, expected in expected_close.items():
                    try:
                        actual = float(closed_session_payload.get(field) or 0)
                    except (TypeError, ValueError) as error:
                        raise RuntimeError(
                            f"El cierre devolvió un valor no numérico para {field}: "
                            f"{closed_session_payload.get(field)!r}"
                        ) from error
                    if abs(actual - expected) > 0.001:
                        raise RuntimeError(
                            f"El turno no quedó conciliado en {field}: esperado {expected}, "
                            f"recibido {actual}. Respuesta: "
                            f"{json.dumps(closed_session_payload, ensure_ascii=False)}"
                        )

                print("UI_SESSION_CLOSE_TIMESTAMP_PERSISTED=true")
                print("UI_SESSION_CLOSED=true")
                print("UI_SESSION_SALES_RECONCILED=true")
                print("UI_SESSION_CASH_RECONCILED=true")
                print("UI_SESSION_CLOSE_CONFIRMATION_COUNT=1")

                closed_session_screenshot = screenshot_path.with_name(
                    screenshot_path.stem + "-session-closed" + screenshot_path.suffix
                )
                visible_snapshot(page, "UI_SESSION_CLOSED")
                page.screenshot(path=str(closed_session_screenshot), full_page=True)
                print(f"UI_SESSION_CLOSED_SCREENSHOT={closed_session_screenshot}")

                # Ejecutar pruebas de resiliencia sólo contra el simulador local.
                # Las operaciones de prueba no crean ventas, pagos ni movimientos de caja.
                api_base = application_endpoint_url(url, "exec/Rubrova.")
                timeout_started = time.monotonic()
                timeout_response = context.request.get(
                    api_base + "rubrovaTestHttpTimeout", timeout=12_000
                )
                timeout_elapsed = time.monotonic() - timeout_started
                if timeout_response.status != 200:
                    raise RuntimeError(
                        "La prueba de timeout respondió HTTP "
                        f"{timeout_response.status}: {timeout_response.text()[:1200]}"
                    )
                timeout_payload = timeout_response.json()
                if isinstance(timeout_payload, list):
                    timeout_payload = timeout_payload[0] if timeout_payload else {}
                print("UI_INTEGRATION_TIMEOUT_RESPONSE=" + json.dumps(timeout_payload, ensure_ascii=False))
                print(f"UI_INTEGRATION_TIMEOUT_ELAPSED_SECONDS={timeout_elapsed:.3f}")
                if timeout_payload.get("outcome") != "failure-captured":
                    raise RuntimeError(
                        "El timeout del proveedor simulado no quedó capturado por Rubrova."
                    )
                if timeout_payload.get("category") != "TIMEOUT_OR_NETWORK":
                    raise RuntimeError(
                        "La categoría de fallo no fue TIMEOUT_OR_NETWORK: "
                        + str(timeout_payload.get("category"))
                    )
                if timeout_elapsed < 0.75:
                    raise RuntimeError(
                        f"La ruta lenta no demostró el timeout de 1 segundo; terminó demasiado pronto ({timeout_elapsed:.3f}s)."
                    )
                if timeout_elapsed > 4.0:
                    raise RuntimeError(
                        f"El límite de 1 segundo no se respetó; la API tardó {timeout_elapsed:.3f}s."
                    )
                print("UI_INTEGRATION_TIMEOUT_BOUNDARY_PROVEN=true")
                print("UI_INTEGRATION_TIMEOUT_CAPTURED=true")
                timeout_message = str(timeout_payload.get("userMessage") or "")
                if "no respondió a tiempo" not in timeout_message:
                    raise RuntimeError("El timeout no devolvió un mensaje claro en español.")
                print("UI_INTEGRATION_TIMEOUT_MESSAGE=true")

                transient_response = context.request.get(
                    api_base + "rubrovaTestHttpTransientStatus", timeout=12_000
                )
                if transient_response.status != 200:
                    raise RuntimeError(
                        "La prueba HTTP 408 respondió HTTP "
                        f"{transient_response.status}: {transient_response.text()[:1200]}"
                    )
                transient_payload = transient_response.json()
                if isinstance(transient_payload, list):
                    transient_payload = transient_payload[0] if transient_payload else {}
                print("UI_INTEGRATION_408_RESPONSE=" + json.dumps(transient_payload, ensure_ascii=False))
                if (
                    transient_payload.get("category") != "REMOTE_TRANSIENT"
                    or int(transient_payload.get("httpStatus") or 0) != 408
                    or not transient_payload.get("retryable")
                ):
                    raise RuntimeError(
                        "El HTTP 408 no se clasificó como transitorio reintentable: "
                        + json.dumps(transient_payload, ensure_ascii=False)
                    )
                print("UI_INTEGRATION_408_CLASSIFIED=true")

                incident_count = int(transient_payload.get("incidentCount") or 0)
                if incident_count != 1:
                    raise RuntimeError(
                        "La incidencia HTTP 408 no quedó persistida exactamente una vez. "
                        f"Cantidad observada: {incident_count}. "
                        f"Respuesta: {json.dumps(transient_payload, ensure_ascii=False)}"
                    )
                if transient_payload.get("incidentRetryable") is not True:
                    raise RuntimeError(
                        "La incidencia HTTP 408 no conservó safeToRetry=true en PostgreSQL: "
                        + json.dumps(transient_payload, ensure_ascii=False)
                    )
                print("UI_INTEGRATION_408_INCIDENT_PERSISTED=true")

                rate_limit_response = context.request.get(
                    api_base + "rubrovaTestHttpRateLimit", timeout=12_000
                )
                if rate_limit_response.status != 200:
                    raise RuntimeError(
                        "La prueba HTTP 429 respondió HTTP "
                        f"{rate_limit_response.status}: {rate_limit_response.text()[:1200]}"
                    )
                rate_limit_payload = rate_limit_response.json()
                if isinstance(rate_limit_payload, list):
                    rate_limit_payload = rate_limit_payload[0] if rate_limit_payload else {}
                print("UI_INTEGRATION_429_RESPONSE=" + json.dumps(rate_limit_payload, ensure_ascii=False))
                if (
                    rate_limit_payload.get("category") != "RATE_LIMITED"
                    or int(rate_limit_payload.get("httpStatus") or 0) != 429
                    or not rate_limit_payload.get("retryable")
                    or str(rate_limit_payload.get("retryAfter") or "") != "2"
                    or rate_limit_payload.get("incidentRetryAfterPersisted") is not True
                ):
                    raise RuntimeError(
                        "El HTTP 429 no capturó Retry-After mediante HEADERSTO o no lo persistió: "
                        + json.dumps(rate_limit_payload, ensure_ascii=False)
                    )
                print("UI_INTEGRATION_429_CLASSIFIED=true")

                server_error_response = context.request.get(
                    api_base + "rubrovaTestHttpServerError", timeout=12_000
                )
                if server_error_response.status != 200:
                    raise RuntimeError(
                        "La prueba HTTP 503 respondió HTTP "
                        f"{server_error_response.status}: {server_error_response.text()[:1200]}"
                    )
                server_error_payload = server_error_response.json()
                if isinstance(server_error_payload, list):
                    server_error_payload = server_error_payload[0] if server_error_payload else {}
                print("UI_INTEGRATION_503_RESPONSE=" + json.dumps(server_error_payload, ensure_ascii=False))
                if server_error_payload.get("category") != "REMOTE_5XX" or int(server_error_payload.get("httpStatus") or 0) != 503 or not server_error_payload.get("retryable"):
                    raise RuntimeError("El HTTP 503 no se clasificó correctamente.")
                print("UI_INTEGRATION_503_CLASSIFIED=true")

                # Asegurar que los errores definitivos no se clasifiquen como reintentables.
                for status_code, expected_category in (
                    (400, "REMOTE_HTTP_ERROR"),
                    (401, "AUTHENTICATION"),
                    (403, "AUTHORIZATION"),
                    (409, "CONFLICT"),
                ):
                    status_response = context.request.get(
                        api_base + f"rubrovaTestHttp{status_code}", timeout=12_000
                    )
                    if status_response.status != 200:
                        raise RuntimeError(
                            f"La prueba HTTP {status_code} respondió HTTP {status_response.status}: "
                            f"{status_response.text()[:1200]}"
                        )
                    status_payload = status_response.json()
                    if isinstance(status_payload, list):
                        status_payload = status_payload[0] if status_payload else {}
                    print(f"UI_INTEGRATION_{status_code}_RESPONSE=" + json.dumps(status_payload, ensure_ascii=False))
                    if status_payload.get("category") != expected_category:
                        raise RuntimeError(
                            f"El HTTP {status_code} esperaba {expected_category} y obtuvo {status_payload.get('category')}."
                        )
                    if status_payload.get("retryable"):
                        raise RuntimeError(f"El HTTP {status_code} no debe reintentarse automáticamente.")
                    print(f"UI_INTEGRATION_{status_code}_CLASSIFIED=true")

                recovery_response = context.request.get(
                    api_base + "rubrovaTestHttpRecovery", timeout=12_000
                )
                if recovery_response.status != 200:
                    raise RuntimeError(
                        "La prueba de recuperación respondió HTTP "
                        f"{recovery_response.status}: {recovery_response.text()[:1200]}"
                    )
                recovery_payload = recovery_response.json()
                if isinstance(recovery_payload, list):
                    recovery_payload = recovery_payload[0] if recovery_payload else {}
                print("UI_INTEGRATION_RECOVERY_RESPONSE=" + json.dumps(recovery_payload, ensure_ascii=False))
                if recovery_payload.get("outcome") != "success":
                    raise RuntimeError("El proveedor simulado no se recuperó tras el timeout.")
                print("UI_INTEGRATION_RECOVERY_SUCCEEDED=true")

                incident_response = context.request.get(
                    api_base + "rubrovaTestIncidentCountApi", timeout=12_000
                )
                if incident_response.status != 200:
                    raise RuntimeError(
                        "La consulta de incidencias respondió HTTP "
                        f"{incident_response.status}: {incident_response.text()[:1200]}"
                    )
                incident_payload = incident_response.json()
                if isinstance(incident_payload, list):
                    incident_payload = incident_payload[0] if incident_payload else {}
                incident_count = int(incident_payload.get("incidentCount", 0))
                print(f"UI_INTEGRATION_INCIDENT_COUNT={incident_count}")
                if incident_count < 8:
                    raise RuntimeError("No quedaron persistidas las ocho incidencias simuladas (timeout, 400, 401, 403, 408, 409, 429, 503).")
                print("UI_INTEGRATION_INCIDENT_PERSISTED=true")
                item_screenshot = screenshot_path.with_name(
                    screenshot_path.stem + "-item" + screenshot_path.suffix
                )
                visible_snapshot(page, "UI_RECEIPT_WITH_ITEM")
                page.screenshot(path=str(item_screenshot), full_page=True)
                print(f"UI_ITEM_SCREENSHOT={item_screenshot}")

            elif not initial_text.strip():
                raise RuntimeError(
                    "Chromium abrió la URL, pero la interfaz no mostró texto visible."
                )

            return 0
        except Exception as error:
            failure_screenshot = screenshot_path.with_name(
                screenshot_path.stem + "-failure" + screenshot_path.suffix
            )
            print(
                "UI_FAILURE_EXCEPTION="
                + f"{type(error).__name__}: {str(error)[:1600]}"
            )
            emit_browser_diagnostics(
                page,
                browser_diagnostics,
                "UI_FAILURE",
                failure_screenshot,
            )
            raise
        finally:
            context.close()
            browser.close()


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/login"
    try:
        return inspect_page(url)
    except (PlaywrightError, RuntimeError, OSError) as error:
        print(f"ERROR_UI_SMOKE: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
