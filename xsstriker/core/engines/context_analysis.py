import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

class ContextAnalysis:
    """Layer 3: Enhanced Context Analysis (XSStrike-style)"""
    def __init__(self, probe="xsstriker_probe"):
        self.probe = probe

    def analyze_context(self, url, parameter, method="get"):
        """Identifies how a probe string is reflected in the DOM and what characters are escaped."""
        try:
            # Step 1: Basic reflection check
            params = {parameter: self.probe}
            if method == "get":
                response = requests.get(url, params=params, timeout=10)
            else:
                response = requests.post(url, data=params, timeout=10)

            html = response.text
            contexts = []

            if self.probe in html:
                soup = BeautifulSoup(html, "html.parser")

                # Reflection in text (HTML)
                for element in soup.find_all(string=re.compile(self.probe)):
                    contexts.append({
                        "type": "html",
                        "tag": element.parent.name,
                        "location": "text"
                    })

                # Reflection in attributes
                for element in soup.find_all(True):
                    for attr, value in element.attrs.items():
                        if self.probe in str(value):
                            contexts.append({
                                "type": "attribute",
                                "tag": element.name,
                                "attr": attr,
                                "location": "attribute"
                            })

                # Reflection in scripts
                for script in soup.find_all("script"):
                    if script.string and self.probe in script.string:
                        contexts.append({
                            "type": "script",
                            "tag": "script",
                            "location": "script"
                        })

            # Step 2: Filtering check (what chars are allowed?)
            char_probe = "< > ' \" ( ) { } ;"
            params[parameter] = char_probe
            if method == "get":
                f_response = requests.get(url, params=params, timeout=10)
            else:
                f_response = requests.post(url, data=params, timeout=10)

            filtered_html = f_response.text
            allowed_chars = []
            for char in char_probe.split():
                if char in filtered_html:
                    allowed_chars.append(char)

            for ctx in contexts:
                ctx["allowed_chars"] = allowed_chars

            return contexts
        except Exception as e:
            print(f"[!] Error analyzing context: {e}")
            return []

if __name__ == "__main__":
    analyzer = ContextAnalysis()
    # results = analyzer.analyze_context("http://example.com/search", "q")
    # print(f"Context results: {results}")
