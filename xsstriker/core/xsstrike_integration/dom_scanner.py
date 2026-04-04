from playwright.async_api import async_playwright
import asyncio

class DOMScanner:
    """Layer 3: DOM-based XSS Scanner using Playwright (Chromium)"""
    def __init__(self, headless=True):
        self.headless = headless

    async def scan(self, url, parameter, payload):
        """Injects payload and scans the DOM using Playwright DevTools Protocol."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            # Construct URL with payload
            if "?" in url:
                vuln_url = f"{url}&{parameter}={payload}"
            else:
                vuln_url = f"{url}?{parameter}={payload}"

            print(f"[*] Scanning DOM (Playwright): {vuln_url}")

            # Capture dialog alerts (XSS Trigger success)
            xss_triggered = False
            page.on("dialog", lambda dialog: self.on_dialog(dialog))

            try:
                # Intercept the dialog by setting a variable
                def on_dialog(dialog):
                    nonlocal xss_triggered
                    xss_triggered = True
                    print(f"[!] XSS Triggered: {dialog.message}")
                    dialog.accept()

                page.on("dialog", on_dialog)

                await page.goto(vuln_url, wait_until="networkidle", timeout=10000)

                # Check for specific DOM reflections or sink executions
                content = await page.content()
                if payload in content:
                    print(f"[*] Payload reflected in DOM content.")

                # Take screenshot on possible trigger
                if xss_triggered:
                    await page.screenshot(path="reports/dom_xss_trigger.png")

                return xss_triggered

            except Exception as e:
                print(f"[!] DOM Scan error: {e}")
                return False
            finally:
                await browser.close()

    def on_dialog(self, dialog):
        print(f"[!] Dialog detected: {dialog.message}")
        dialog.dismiss()

if __name__ == "__main__":
    scanner = DOMScanner()
    # asyncio.run(scanner.scan("http://example.com", "q", "<script>alert(1)</script>"))
