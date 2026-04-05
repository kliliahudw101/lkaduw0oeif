from playwright.async_api import async_playwright
import asyncio
from .js_hooker import JSHooker
import os

class DOMScanner:
    """Layer 3: Verification-First DOM-based XSS Scanner using Playwright."""
    def __init__(self, headless=True):
        self.headless = headless
        self.hooker = JSHooker()

    async def scan(self, url, parameter, payload, screenshot_path=None):
        """Injects payload and scans for execution using browser events and hooks."""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()

            # Inject JS Hooks for Deep DOM Monitoring
            await page.add_init_script(self.hooker.get_hook_script())

            # Flags for detection
            xss_triggered = False
            sink_hit = False
            sink_details = []

            # Handle console logs (from hooks)
            def on_console(msg):
                nonlocal sink_hit, sink_details
                if "[XStriker-Hook]" in msg.text:
                    # Check if our payload is in the sink args/value
                    if payload in msg.text:
                        sink_hit = True
                        sink_details.append(msg.text)
                        print(f"[!] Sink Execution Detected: {msg.text}")

            page.on("console", on_console)

            # Handle Dialog alerts
            async def on_dialog(dialog):
                nonlocal xss_triggered
                if payload in dialog.message or "1" in dialog.message or str(hash(payload)) in dialog.message:
                     xss_triggered = True
                     print(f"[!] XSS Triggered via alert: {dialog.message}")
                await dialog.accept()

            page.on("dialog", on_dialog)

            # Construct URL with payload
            if "?" in url:
                vuln_url = f"{url}&{parameter}={payload}"
            else:
                vuln_url = f"{url}?{parameter}={payload}"

            print(f"[*] Scanning (Playwright): {vuln_url}")

            try:
                # Load the page and wait for everything to settle
                await page.goto(vuln_url, wait_until="networkidle", timeout=15000)

                # Check for direct reflection in DOM that might indicate execution (if not caught by dialog)
                # Some payloads might not trigger alert but execute other JS

                # Take screenshot on confirmation
                if (xss_triggered or sink_hit) and screenshot_path:
                    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                    await page.screenshot(path=screenshot_path)
                    print(f"[+] Screenshot saved: {screenshot_path}")

                return xss_triggered or sink_hit

            except Exception as e:
                print(f"[!] Browser Error: {e}")
                return False
            finally:
                await browser.close()

if __name__ == "__main__":
    scanner = DOMScanner()
    # asyncio.run(scanner.scan("http://example.com", "q", "<script>alert(1)</script>"))
