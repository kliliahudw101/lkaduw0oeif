import httpx

class WAFFingerprinter:
    """Layer 3: WAF Identification (Cloudflare, AWS, etc.) using HTTP headers."""
    def __init__(self):
        self.waf_signatures = {
            "Cloudflare": ["__cfduid", "cf-ray", "cloudflare"],
            "AWS WAF": ["x-amzn-requestid", "awswaf"],
            "Akamai": ["akamai-x-cache", "akamai-ghost"],
            "Sucuri": ["x-sucuri-id", "sucuri-cloudproxy"],
            "ModSecurity": ["mod_security", "modsecurity"]
        }

    async def identify(self, url):
        """Identifies WAF presence and type."""
        print(f"[*] Identifying WAF on {url}...")
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                headers = response.headers
                server = headers.get("server", "").lower()

                # Check for signatures in headers
                for waf, sigs in self.waf_signatures.items():
                    for sig in sigs:
                        if sig in str(headers).lower() or sig in server:
                            print(f"[!] WAF DETECTED: {waf}")
                            return waf

                # Trigger WAF check by sending a blocked-like request
                blocked_response = await client.get(f"{url}?q=<script>alert(1)</script>")
                if blocked_response.status_code in [403, 406, 501]:
                     # Analyze block page content
                     if "cloudflare" in blocked_response.text.lower():
                         return "Cloudflare"
                     return "Generic WAF"

                return "No WAF"
            except Exception as e:
                print(f"[!] Fingerprint error: {e}")
                return "Unknown"

if __name__ == "__main__":
    import asyncio
    # fingerprinter = WAFFingerprinter()
    # asyncio.run(fingerprinter.identify("http://example.com"))
