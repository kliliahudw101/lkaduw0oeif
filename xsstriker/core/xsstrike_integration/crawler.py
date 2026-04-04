import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

class SimpleCrawler:
    """Layer 3: XSStrike Integration (Crawler)"""
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.input_vectors = []

    def crawl(self, url=None):
        """Discovers input points (forms and URL parameters)."""
        if not url:
            url = self.base_url

        if url in self.visited:
            return

        self.visited.add(url)
        print(f"[*] Crawling: {url}")

        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            # Find forms
            for form in soup.find_all("form"):
                action = form.get("action")
                method = form.get("method", "get").lower()
                inputs = []
                for input_tag in form.find_all(["input", "textarea", "select"]):
                    name = input_tag.get("name")
                    if name:
                        inputs.append({"name": name, "type": input_tag.get("type", "text")})

                self.input_vectors.append({
                    "url": urljoin(url, action),
                    "method": method,
                    "params": inputs,
                    "type": "form"
                })

            # Extract URL parameters
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            if query_params:
                self.input_vectors.append({
                    "url": url,
                    "method": "get",
                    "params": [{"name": k, "type": "url_param"} for k in query_params.keys()],
                    "type": "url_param"
                })

            # Recursively crawl links on the same domain
            for link in soup.find_all("a", href=True):
                href = link.get("href")
                full_url = urljoin(url, href)
                if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                    self.crawl(full_url)

        except Exception as e:
            print(f"[!] Error crawling {url}: {e}")

        return self.input_vectors

if __name__ == "__main__":
    crawler = SimpleCrawler("http://example.com")
    vectors = crawler.crawl()
    print(f"Found {len(vectors)} input vectors.")
