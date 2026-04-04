import requests
from bs4 import BeautifulSoup
import re

class ContextAnalysis:
    """Layer 3: Context Analysis (XSStrike-style)"""
    def __init__(self, probe="d3v_probe"):
        self.probe = probe

    def analyze_context(self, url, parameter, method="get"):
        """Identifies how a probe string is reflected in the DOM."""
        try:
            params = {parameter: self.probe}
            if method == "get":
                response = requests.get(url, params=params, timeout=5)
            else:
                response = requests.post(url, data=params, timeout=5)

            html = response.text
            contexts = []

            # Simple Context analysis logic
            if self.probe in html:
                soup = BeautifulSoup(html, "html.parser")

                # Check for reflection in text nodes (HTML)
                for element in soup.find_all(string=re.compile(self.probe)):
                    contexts.append({"type": "html", "tag": element.parent.name})

                # Check for reflection in attributes
                for element in soup.find_all(True):
                    for attr, value in element.attrs.items():
                        if self.probe in str(value):
                            contexts.append({"type": "attribute", "tag": element.name, "attr": attr})

                # Check for reflection in scripts
                for script in soup.find_all("script"):
                    if self.probe in script.string:
                        contexts.append({"type": "script", "tag": "script"})

            return contexts
        except Exception as e:
            print(f"[!] Error analyzing context: {e}")
            return []

if __name__ == "__main__":
    analyzer = ContextAnalysis()
    results = analyzer.analyze_context("http://example.com/search", "q")
    print(f"Context results: {results}")
