import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import asyncio
import re

class Crawl4AICrawler:
    """Layer 3: Modern Crawler with XSStrike-style features."""
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.input_vectors = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.common_params = ["id", "q", "s", "query", "search", "p", "page", "lang", "redirect", "url", "next"]

    async def discover_hidden_params(self, url):
        """Attempts to find hidden parameters by brute-forcing common ones."""
        print(f"[*] Discovering hidden parameters for: {url}")
        found_params = []
        async with httpx.AsyncClient(timeout=5, follow_redirects=True, headers=self.headers) as client:
            # Baseline request
            try:
                baseline_resp = await client.get(url)
                baseline_len = len(baseline_resp.text)

                for param in self.common_params:
                    # Test if adding param changes response
                    test_url = f"{url}{'&' if '?' in url else '?'}{param}=xsstriker_test"
                    resp = await client.get(test_url)
                    if len(resp.text) != baseline_len or "xsstriker_test" in resp.text:
                        print(f"[+] Found hidden parameter: {param}")
                        found_params.append({"name": param, "type": "hidden_param"})
            except Exception as e:
                print(f"[!] Hidden param discovery error: {e}")
        return found_params

    async def crawl(self, url=None, depth=2, discover_hidden=False):
        """Asynchronous recursive crawling using httpx."""
        if not url:
            url = self.base_url

        if url in self.visited or depth == 0:
            return self.input_vectors

        self.visited.add(url)
        print(f"[*] Crawling: {url}")

        async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=self.headers) as client:
            try:
                response = await client.get(url)

                content_type = response.headers.get("Content-Type", "").lower()
                if "text/html" not in content_type:
                    return self.input_vectors

                soup = BeautifulSoup(response.text, "html.parser")

                # 1. Extract forms
                for form in soup.find_all("form"):
                    action = form.get("action")
                    method = form.get("method", "get").lower()
                    inputs = []
                    for it in form.find_all(["input", "textarea", "select"]):
                        name = it.get("name")
                        if name:
                            inputs.append({"name": name, "type": it.get("type", "text")})

                    self.input_vectors.append({
                        "url": urljoin(url, action or ""),
                        "method": method,
                        "params": inputs,
                        "type": "form"
                    })

                # 2. Extract URL parameters
                query_params = parse_qs(urlparse(url).query)
                if query_params:
                    self.input_vectors.append({
                        "url": url,
                        "method": "get",
                        "params": [{"name": k, "type": "url_param"} for k in query_params.keys()],
                        "type": "url_param"
                    })

                # 3. Hidden parameter discovery
                if discover_hidden:
                    hidden = await self.discover_hidden_params(url)
                    if hidden:
                        self.input_vectors.append({
                            "url": url,
                            "method": "get",
                            "params": hidden,
                            "type": "hidden_param"
                        })

                # 4. Find JS files
                for script in soup.find_all("script", src=True):
                    js_url = urljoin(url, script.get("src"))
                    if urlparse(js_url).netloc == urlparse(self.base_url).netloc:
                         # Potentially analyze JS files here for sinks/sources
                         pass

                # Recursion
                tasks = []
                for link in soup.find_all("a", href=True):
                    href = link.get("href")
                    full_url = urljoin(url, href)
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        tasks.append(self.crawl(full_url, depth - 1, discover_hidden))

                if tasks:
                    await asyncio.gather(*tasks)

            except Exception as e:
                print(f"[!] Crawl error at {url}: {e}")

        # De-duplicate vectors
        unique_vectors = []
        seen = set()
        for v in self.input_vectors:
            v_key = (v['url'], v['method'], tuple(sorted([p['name'] for p in v['params']])))
            if v_key not in seen:
                seen.add(v_key)
                unique_vectors.append(v)

        return unique_vectors

if __name__ == "__main__":
    crawler = Crawl4AICrawler("http://example.com")
    # asyncio.run(crawler.crawl())
