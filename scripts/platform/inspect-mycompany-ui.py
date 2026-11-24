#!/usr/bin/env python3
"""Read-only browser inspection for the isolated MyCompany runtime smoke test."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


SERVER_ERROR_MARKERS = (
    "AppServerNotAvailableDispatchException",
    "Application server [",
    "Connection refused",
    "NotBoundException",
)


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


def wait_until_form_loaded(page: Any, label: str, timeout_seconds: int = 45) -> str:
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
        register_selected = "Caja de prueba Rubrova" in searchable
        open_session_available = "Abrir turno" in searchable

        if not is_loading and register_selected and open_session_available:
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
        f"{label} no mostró el puesto 'Caja de prueba Rubrova' y la acción 'Abrir turno' "
        f"en {timeout_seconds}s. Último texto visible: {last_text.strip()[:1600]}"
    )


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
            visible_snapshot(page, "UI_INITIAL")
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"UI_INITIAL_SCREENSHOT={screenshot_path}")

            if os.environ.get("RUBROVA_UI_TEST_LOGIN", "false").lower() == "true":
                final_text = login_to_ephemeral_instance(page)
                print(
                    "UI_LOGIN_STATUS=authenticated:"
                    + os.environ.get("RUBROVA_UI_TEST_USERNAME", "admin")
                )
                visible_snapshot(page, "UI_AFTER_LOGIN")
                page.screenshot(path=str(after_login_screenshot), full_page=True)
                print(f"UI_HOME_SCREENSHOT={after_login_screenshot}")
                if not final_text.strip():
                    raise RuntimeError("La pantalla posterior al acceso está vacía.")

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

                # The menu click can return before the GWT form finishes rendering.
                pos_text = wait_until_form_loaded(page, "UI_POS_SCREEN", timeout_seconds=45)
                visible_snapshot(page, "UI_POS_SCREEN")
                page.screenshot(path=str(pos_screenshot), full_page=True)
                print(f"UI_POS_SCREENSHOT={pos_screenshot}")
                print("UI_POS_SCREEN_AVAILABLE=true")
                if not pos_text.strip():
                    raise RuntimeError("La pantalla POS se abrió, pero no mostró contenido.")

                # Abrir un turno en la base efímera de CI; la venta sintética se confirmará explícitamente más adelante.
                if not click_exact_action(page, "Abrir turno"):
                    raise RuntimeError("El botón 'Abrir turno' no estaba disponible para la prueba aislada.")
                wait_for_session_open(page, timeout_seconds=45)
                session_screenshot = screenshot_path.with_name(
                    screenshot_path.stem + "-session" + screenshot_path.suffix
                )
                visible_snapshot(page, "UI_SESSION_OPEN")
                page.screenshot(path=str(session_screenshot), full_page=True)
                print(f"UI_SESSION_SCREENSHOT={session_screenshot}")

                # Primer paso comercial: buscar el producto ficticio y agregarlo al recibo.
                search_tab = page.get_by_text("Buscar artículos", exact=True)
                search_tab.wait_for(state="visible", timeout=15_000)
                search_tab.click(no_wait_after=True)
                print("UI_ITEM_SEARCH_TAB_CLICKED=true")
                visible_snapshot(page, "UI_ITEM_SEARCH")

                product_name = "Producto de prueba Rubrova"
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
                api_base = url.rstrip("/") + "/exec/Rubrova."
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
                sales_api_base = url.rstrip("/") + "/exec/Sales."

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

                sale_screenshot = screenshot_path.with_name(
                    screenshot_path.stem + "-sale" + screenshot_path.suffix
                )
                visible_snapshot(page, "UI_SALE_CONFIRMED")
                page.screenshot(path=str(sale_screenshot), full_page=True)
                print(f"UI_SALE_SCREENSHOT={sale_screenshot}")

                # Cierre nativo de MyCompany: CONFIRM se muestra como MessageBox GWT,
                # no como window.confirm del navegador. Aceptamos el botón afirmativo real.
                if not click_exact_action(page, "Cerrar turno"):
                    raise RuntimeError("No se encontró la acción nativa 'Cerrar turno' de MyCompany.")
                print("UI_SESSION_CLOSE_ACTION_CLICKED=true")
                close_confirmation_message = accept_ls_fusion_confirmation(page, "Cerrar turno")
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
                    if closed_session_payload.get("closingDateTime") and not closed_session_payload.get("opened"):
                        break
                    page.wait_for_timeout(750)

                print("UI_SESSION_CLOSE_RECONCILIATION=" + json.dumps(closed_session_payload, ensure_ascii=False))
                if not closed_session_payload.get("sessionNumber"):
                    raise RuntimeError("No se encontró el turno original después de intentar cerrarlo.")
                if not closed_session_payload.get("openingDateTime"):
                    raise RuntimeError("El turno cerrado no conservó su fecha de apertura.")
                if not closed_session_payload.get("closingDateTime"):
                    raise RuntimeError("El cierre nativo no persistió closingDateTime.")
                if closed_session_payload.get("opened") is not False:
                    raise RuntimeError("El turno sigue abierto después de ejecutar Cerrar turno.")

                expected_close = {
                    "salesCount": 1,
                    "salesAmount": 1250,
                    "returnsCount": 0,
                    "returnsAmount": 0,
                    "netAmount": 1250,
                    "cashPaid": 1250,
                    "cashBalance": 1250,
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
                api_base = url.rstrip("/") + "/exec/Rubrova."
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
        finally:
            context.close()
            browser.close()


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/"
    try:
        return inspect_page(url)
    except (PlaywrightError, RuntimeError, OSError) as error:
        print(f"ERROR_UI_SMOKE: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
