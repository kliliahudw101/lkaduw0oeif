from playwright.async_api import async_playwright
import asyncio
from .js_hooker import JSHooker
import os
import urllib.parse

class DOMScanner:
    """Layer 3: Advanced Verification Engine using Playwright."""
    def __init__(self, headless=True):
        self.headless = headless
        self.hooker = JSHooker()

    async def scan(self, url, parameter, payload, screenshot_path=None):
        """Injects payload and scans for execution using browser events and hooks."""
        async with async_playwright() as p:
            # Launch browser with extra args for stability
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Inject JS Hooks
            await page.add_init_script(self.hooker.get_hook_script())

            xss_triggered = False
            sink_hit = False

            # Decoded payload for matching in sinks
            decoded_payload = urllib.parse.unquote(payload)

            # Handle console logs (from hooks)
            def on_console(msg):
                nonlocal sink_hit
                if "[XStriker-Hook]" in msg.text:
                    # Check if our payload (raw or decoded) is in the sink
                    if payload in msg.text or decoded_payload in msg.text or "alert(1)" in msg.text:
                        sink_hit = True

            page.on("console", on_console)

            # Handle Dialog alerts
            async def on_dialog(dialog):
                nonlocal xss_triggered
                # Flexible matching for alert content
                if any(ind in dialog.message for ind in ["1", "XSS", "XSStriker"]):
                     xss_triggered = True
                elif payload in dialog.message or decoded_payload in dialog.message:
                     xss_triggered = True
                await dialog.accept()

            page.on("dialog", on_dialog)

            # Construct URL
            parsed = urllib.parse.urlparse(url)
            query = urllib.parse.parse_qs(parsed.query)
            query[parameter] = [payload]
            new_query = urllib.parse.urlencode(query, doseq=True)
            vuln_url = urllib.parse.urlunparse(parsed._replace(query=new_query))

            try:
                # Retry logic for network instability
                for attempt in range(3):
                    try:
                        await page.goto(vuln_url, wait_until="load", timeout=30000)
                        await page.wait_for_load_state("networkidle", timeout=5000)
                        break
                    except Exception as e:
                        if attempt == 2: raise e
                        await asyncio.sleep(2)

                # Final wait for async scripts
                await asyncio.sleep(3)

                # Take screenshot on confirmation
                if (xss_triggered or sink_hit) and screenshot_path:
                    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                    await page.screenshot(path=screenshot_path)

                return xss_triggered or sink_hit

            except Exception as e:
                # Log browser errors but don't stop the whole scan
                from utils.logger import log_error
                log_error(f"Browser error at {vuln_url}: {str(e)}")
                return False
            finally:
                await browser.close()
