import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import asyncio

class Crawl4AICrawler:
    """Layer 3: Modern Crawler (Inspired by Crawl4ai)"""
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.input_vectors = []
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    async def crawl(self, url=None, depth=2):
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

                # Check if it is an HTML page to avoid binary files (MZ/PE, etc)
                content_type = response.headers.get("Content-Type", "").lower()
                if "text/html" not in content_type:
                    return self.input_vectors

                soup = BeautifulSoup(response.text, "html.parser")

                # Extract input vectors (forms)
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

                # Extract URL parameters as input vectors
                query_params = parse_qs(urlparse(url).query)
                if query_params:
                    self.input_vectors.append({
                        "url": url,
                        "method": "get",
                        "params": [{"name": k, "type": "url_param"} for k in query_params.keys()],
                        "type": "url_param"
                    })

                # Continue crawling on same domain (Recursion)
                tasks = []
                for link in soup.find_all("a", href=True):
                    href = link.get("href")
                    full_url = urljoin(url, href)
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        tasks.append(self.crawl(full_url, depth - 1))

                if tasks:
                    await asyncio.gather(*tasks)

            except Exception as e:
                print(f"[!] Crawl error at {url}: {e}")

        return self.input_vectors

if __name__ == "__main__":
    crawler = Crawl4AICrawler("http://example.com")
    # asyncio.run(crawler.crawl())
