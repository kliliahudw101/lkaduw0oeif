import time
import httpx
from bs4 import BeautifulSoup

class StoredXSSDetector:
    """Layer 3: Stored XSS Detection (Site-wide mapping + persistence verification)"""
    def __init__(self, base_url):
        self.base_url = base_url
        self.site_map = set()
        self.visited = set()

    async def build_site_map(self, url=None):
        """Asynchronously maps the entire site."""
        if not url:
            url = self.base_url
        if url in self.visited:
            return
        self.visited.add(url)
        self.site_map.add(url)

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

        async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=headers) as client:
            try:
                response = await client.get(url)

                # Ensure only HTML content is parsed
                content_type = response.headers.get("Content-Type", "").lower()
                if "text/html" not in content_type:
                    return

                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link.get("href")
                    full_url = httpx.URL(url).join(href)
                    if full_url.host == httpx.URL(self.base_url).host:
                        await self.build_site_map(str(full_url))
            except Exception as e:
                print(f"[!] Site mapping error: {e}")

    async def detect(self, injection_url, parameter, payload, signature="xstriker_stored"):
        """1. Injection, 2. Site-wide crawl, 3. Verify persistence."""
        # Step 1: Injection
        print(f"[*] Injecting Stored XSS payload into {injection_url} (parameter: {parameter})")
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                await client.post(injection_url, data={parameter: f"{payload} {signature}"})

                # Step 2 & 3: Scan all pages for the signature
                for page in self.site_map:
                    print(f"[*] Checking page for reflection: {page}")
                    response = await client.get(page)
                    if signature in response.text:
                        print(f"[!] Signature found at reflection point: {page}")

                        # Step 4: Persistence Verification (3 retries with wait)
                        if await self.verify_persistent(page, signature):
                             return {
                                 "type": "Stored XSS",
                                 "injection_point": injection_url,
                                 "reflection_point": page,
                                 "persistence_verified": True,
                                 "payload": payload
                             }
            except Exception as e:
                print(f"[!] Stored XSS detection error: {e}")
        return None

    async def verify_persistent(self, page, signature, retries=3):
        """Re-checks the page multiple times to ensure stability."""
        print(f"[*] Verifying persistence at {page}...")
        for i in range(retries):
            time.sleep(i + 1) # Wait longer each time
            async with httpx.AsyncClient() as client:
                response = await client.get(page)
                if signature not in response.text:
                    print(f"[!] Persistence check failed at retry {i+1}.")
                    return False
        print(f"[+] Persistence verified after {retries} retries.")
        return True

if __name__ == "__main__":
    import asyncio
    # detector = StoredXSSDetector("http://test.com")
    # asyncio.run(detector.build_site_map())
