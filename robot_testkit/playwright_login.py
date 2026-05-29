from __future__ import annotations

import sys


def main() -> int:
    from playwright.sync_api import sync_playwright

    url = sys.argv[1]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

