#!/usr/bin/env python3
"""Read-only browser inspection for the isolated MyCompany runtime smoke test."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def inspect_page(url: str) -> int:
    screenshot_path = Path(
        os.environ.get("RUBROVA_UI_SCREENSHOT", "/tmp/rubrova-mycompany-ui.png")
    )
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

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
            page.wait_for_timeout(2_000)

            title = page.title()
            body_text = page.locator("body").inner_text(timeout=10_000)
            input_data: list[dict[str, Any]] = page.locator("input").evaluate_all(
                """elements => elements.slice(0, 30).map(element => ({
                    type: element.type || "",
                    name: element.name || "",
                    id: element.id || "",
                    placeholder: element.placeholder || "",
                    ariaLabel: element.getAttribute("aria-label") || "",
                    visible: !!(element.offsetWidth || element.offsetHeight)
                }))"""
            )
            buttons = page.locator("button").evaluate_all(
                """elements => elements.slice(0, 40).map(element => ({
                    text: (element.innerText || element.textContent || "").trim(),
                    ariaLabel: element.getAttribute("aria-label") || "",
                    visible: !!(element.offsetWidth || element.offsetHeight)
                }))"""
            )
            links = page.locator("a").evaluate_all(
                """elements => elements.slice(0, 30).map(element => ({
                    text: (element.innerText || element.textContent || "").trim(),
                    href: element.getAttribute("href") || ""
                }))"""
            )

            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"UI_HTTP_STATUS={status}")
            print(f"UI_FINAL_URL={page.url}")
            print(f"UI_TITLE={title}")
            print(f"UI_BODY_TEXT_LENGTH={len(body_text.strip())}")
            print("UI_VISIBLE_TEXT_BEGIN")
            print(body_text.strip()[:3500])
            print("UI_VISIBLE_TEXT_END")
            print("UI_INPUTS=" + json.dumps(input_data, ensure_ascii=False))
            print("UI_BUTTONS=" + json.dumps(buttons, ensure_ascii=False))
            print("UI_LINKS=" + json.dumps(links, ensure_ascii=False))
            print(f"UI_SCREENSHOT={screenshot_path}")

            if not body_text.strip() and not input_data and not buttons:
                raise RuntimeError("Chromium abrió la URL, pero la interfaz no mostró contenido ni controles.")
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
