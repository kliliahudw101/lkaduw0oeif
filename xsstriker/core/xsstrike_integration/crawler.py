import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawl4AICrawler:
    """Layer 3: Modern Crawler (Inspired by Crawl4ai)"""
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.input_vectors = []

    async def crawl(self, url=None):
        """Asynchronous crawling using httpx."""
        if not url:
            url = self.base_url

        if url in self.visited:
            return

        self.visited.add(url)
        print(f"[*] Crawling: {url}")

        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract input vectors (forms, etc.)
                for form in soup.find_all("form"):
                    action = form.get("action")
                    method = form.get("method", "get").lower()
                    inputs = []
                    for it in form.find_all(["input", "textarea", "select"]):
                        name = it.get("name")
                        if name:
                            inputs.append({"name": name, "type": it.get("type", "text")})

                    self.input_vectors.append({
                        "url": urljoin(url, action),
                        "method": method,
                        "params": inputs,
                        "type": "form"
                    })

                # Continue crawling on same domain
                for link in soup.find_all("a", href=True):
                    href = link.get("href")
                    full_url = urljoin(url, href)
                    if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                        # Async recursion can be complex, for this demo we'll use a queue approach in a real app
                        pass

            except Exception as e:
                print(f"[!] Crawl error: {e}")

        return self.input_vectors

if __name__ == "__main__":
    import asyncio
    crawler = Crawl4AICrawler("http://example.com")
    # asyncio.run(crawler.crawl())
