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
    selector = 'button, input[type="submit"], [role="button"]'
    controls = page.locator(selector).evaluate_all(
        """elements => elements.map((element, index) => {
            const style = getComputedStyle(element);
            return {
                index,
                tag: element.tagName.toLowerCase(),
                text: (element.innerText || element.value || element.textContent || "").trim(),
                visible: style.display !== "none" && style.visibility !== "hidden" &&
                    !!(element.offsetWidth || element.offsetHeight),
                outerHTML: element.outerHTML.slice(0, 700)
            };
        })"""
    )
    matches = [control for control in controls if control["visible"] and control["text"] == label]
    if not matches:
        print(f"UI_ACTION_{label.upper().replace(' ', '_')}_FOUND=false")
        print(
            f"UI_ACTION_{label.upper().replace(' ', '_')}_DIAGNOSTIC="
            + json.dumps(controls, ensure_ascii=False)
        )
        return False
    index = int(matches[0]["index"])
    print(
        f"UI_ACTION_{label.upper().replace(' ', '_')}_TARGET="
        + json.dumps(matches[0], ensure_ascii=False)
    )
    page.locator(selector).nth(index).click(no_wait_after=True)
    print(f"UI_ACTION_{label.upper().replace(' ', '_')}_CLICKED=true")
    return True


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


def wait_for_exact_link(page: Any, label: str, timeout_seconds: int = 12) -> int | None:
    deadline = time.monotonic() + timeout_seconds
    last_links: list[dict[str, Any]] = []

    while time.monotonic() < deadline:
        last_links = page.locator("a").evaluate_all(
            """elements => elements.map((element, index) => ({
                index,
                text: (element.innerText || element.textContent || "").trim(),
                visible: getComputedStyle(element).display !== "none" &&
                    getComputedStyle(element).visibility !== "hidden" &&
                    !!(element.offsetWidth || element.offsetHeight),
                href: element.getAttribute("href") || "",
                className: typeof element.className === "string" ? element.className : "",
                role: element.getAttribute("role") || "",
                ariaLabel: element.getAttribute("aria-label") || "",
                title: element.getAttribute("title") || "",
                outerHTML: element.outerHTML.slice(0, 700),
                parentHTML: element.parentElement ? element.parentElement.outerHTML.slice(0, 1000) : ""
            }))"""
        )
        matches = [
            link for link in last_links
            if link["visible"] and link["text"] == label
        ]
        if matches:
            print(
                f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_TARGET="
                + json.dumps(matches[0], ensure_ascii=False)
            )
            return int(matches[0]["index"])
        page.wait_for_timeout(250)

    print(f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_FOUND=false")
    print(
        f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_DIAGNOSTIC="
        + json.dumps(last_links, ensure_ascii=False)
    )
    return None


def click_exact_link(page: Any, label: str) -> bool:
    index = wait_for_exact_link(page, label)
    if index is None:
        return False
    link = page.locator("a").nth(index)
    link.scroll_into_view_if_needed()
    link.click(no_wait_after=True)
    page.wait_for_timeout(1_000)
    print(f"UI_NAV_LINK_{label.upper().replace(' ', '_')}_FOUND=true")
    return True


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
                if not click_exact_link(page, "Comercio"):
                    raise RuntimeError("No se pudo seleccionar el módulo Comercio.")

                # The submenu is loaded asynchronously by the lsFusion navigator.
                if wait_for_exact_link(page, "Punto de venta", timeout_seconds=12) is None:
                    visible_snapshot(page, "UI_RETAIL_NAVIGATION_FAILED")
                    page.screenshot(path=str(retail_screenshot), full_page=True)
                    print(f"UI_RETAIL_SCREENSHOT={retail_screenshot}")
                    raise RuntimeError("El menú Comercio no mostró la opción 'Punto de venta'.")

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

                # Crear un turno únicamente en la base efímera de CI; no se registra ninguna venta.
                if not click_exact_action(page, "Abrir turno"):
                    raise RuntimeError("El botón 'Abrir turno' no estaba disponible para la prueba aislada.")
                wait_for_session_open(page, timeout_seconds=45)
                session_screenshot = screenshot_path.with_name(
                    screenshot_path.stem + "-session" + screenshot_path.suffix
                )
                visible_snapshot(page, "UI_SESSION_OPEN")
                page.screenshot(path=str(session_screenshot), full_page=True)
                print(f"UI_SESSION_SCREENSHOT={session_screenshot}")

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
