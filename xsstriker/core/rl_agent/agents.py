import random

class EscapeAgent:
    """Level 1 RL Agent: Escape current context."""
    def __init__(self):
        self.rules = [
            '"><',
            "'",
            '</script>',
            'javascript:',
            'data:',
            '#',
            ';'
        ]

    def act(self, context=None):
        """Chooses a context-breaking action based on the identified context."""
        if not context:
            return random.choice(self.rules)

        # Simple heuristic mapping for RL demo
        if context.get("type") == "html":
            return '"><'
        elif context.get("type") == "attribute":
            return "'"
        elif context.get("type") == "script":
            return '</script>'

        return random.choice(self.rules)

class SanitizationAgent:
    """Level 2 RL Agent: Bypass filters/sanitization."""
    def __init__(self):
        self.mutations = [
            "double_url",
            "hex",
            "html_entity",
            "case_swap",
            "null_byte",
            "string_from_char_code",
            "comment_insertion",
            "eval_obfuscation"
        ]

    def obfuscate(self, payload):
        """Applies mutation techniques for filter bypass."""
        mutation = random.choice(self.mutations)
        if mutation == "double_url":
            import urllib.parse
            return urllib.parse.quote(urllib.parse.quote(payload))
        elif mutation == "hex":
            return "".join(f"\\x{ord(c):02x}" for c in payload)
        elif mutation == "case_swap":
            return "".join(c.upper() if random.choice([True, False]) else c.lower() for c in payload)

        return payload

if __name__ == "__main__":
    ea = EscapeAgent()
    sa = SanitizationAgent()
    print(f"Escape action: {ea.act()}")
    print(f"Obfuscated payload: {sa.obfuscate('<script>alert(1)</script>')}")
