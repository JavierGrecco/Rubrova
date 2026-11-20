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
            ariaLabel: element.getAttribute("aria-label") || "",
            visible: !!(element.offsetWidth || element.offsetHeight)
        }))"""
    )
    buttons = page.locator("button, input[type=submit]").evaluate_all(
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

    print(f"{label}_TITLE={title}")
    print(f"{label}_URL={page.url}")
    print(f"{label}_BODY_TEXT_LENGTH={len(body_text.strip())}")
    print(f"{label}_VISIBLE_TEXT_BEGIN")
    print(body_text.strip()[:4500])
    print(f"{label}_VISIBLE_TEXT_END")
    print(f"{label}_INPUTS=" + json.dumps(input_data, ensure_ascii=False))
    print(f"{label}_BUTTONS=" + json.dumps(buttons, ensure_ascii=False))
    print(f"{label}_LINKS=" + json.dumps(links, ensure_ascii=False))
    return body_text


def has_server_error(text: str) -> bool:
    return any(marker in text for marker in SERVER_ERROR_MARKERS)


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
    submit_field.click()

    deadline = time.monotonic() + 45
    last_text = ""
    while time.monotonic() < deadline:
        page.wait_for_timeout(1_000)
        last_text = page.locator("body").inner_text(timeout=10_000)
        try:
            login_visible = username_field.is_visible()
        except PlaywrightError:
            login_visible = False

        if not login_visible and not has_server_error(last_text) and last_text.strip():
            # Require the authenticated page to remain stable for another second.
            page.wait_for_timeout(1_000)
            stable_text = page.locator("body").inner_text(timeout=10_000)
            if (
                not page.locator("#username").is_visible()
                and not has_server_error(stable_text)
                and stable_text.strip()
            ):
                return stable_text

    raise RuntimeError(
        "No se pudo completar el acceso a la instancia efímera con "
        f"{username!r}. Texto visible: {last_text.strip()[:1600]}"
    )


def inspect_page(url: str) -> int:
    screenshot_path = Path(
        os.environ.get("RUBROVA_UI_SCREENSHOT", "/tmp/rubrova-mycompany-ui.png")
    )
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    after_login_screenshot = screenshot_path.with_name(
        screenshot_path.stem + "-after-login" + screenshot_path.suffix
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
            initial_text = visible_snapshot(page, "UI_INITIAL")
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"UI_INITIAL_SCREENSHOT={screenshot_path}")

            if os.environ.get("RUBROVA_UI_TEST_LOGIN", "false").lower() == "true":
                if has_server_error(initial_text):
                    raise RuntimeError(
                        "El cliente web aún muestra un error de conexión al servidor de aplicación."
                    )
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
