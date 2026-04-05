import re
import numpy as np
import random

class SecurityFeatureEnsemble:
    """Layer 1: Security Feature Engineering (Handcrafted Features)."""
    def __init__(self):
        self.keywords = [
            "script", "alert", "onerror", "onload", "eval", "javascript",
            "src", "href", "document", "cookie", "window", "prompt", "confirm"
        ]

    def calculate_entropy(self, text):
        """Calculates Shannon entropy of the string."""
        if not text:
            return 0
        probabilities = [text.count(c) / len(text) for c in set(text)]
        entropy = -sum(p * np.log2(p) for p in probabilities)
        return entropy

    def extract_features(self, text):
        """Extracts 14 handcrafted security features."""
        features = {}
        features["length"] = len(text)
        features["entropy"] = self.calculate_entropy(text)
        features["special_chars"] = len(re.findall(r'[\"\';<>=()&%#]', text)) / max(len(text), 1)
        features["tags_count"] = len(re.findall(r'<.*?>', text))
        features["scripts_count"] = text.lower().count("<script")
        features["alert_count"] = text.lower().count("alert")
        features["onerror_count"] = text.lower().count("onerror")
        features["url_encoding"] = text.count("%")
        features["hex_encoding"] = text.count("\\x")
        features["unicode_encoding"] = text.count("\\u")
        features["keyword_matches"] = sum(1 for kw in self.keywords if kw in text.lower())
        features["double_quote_count"] = text.count('"')
        features["single_quote_count"] = text.count("'")
        features["bracket_count"] = text.count("<") + text.count(">")

        return features

class PayloadAugmentor:
    """Layer 1: Data Augmentation for synthetic training data."""
    def __init__(self):
        self.char_map = {
            'a': ['A', '&#97;', '\\u0061'],
            's': ['S', '&#115;', '\\u0073'],
            'e': ['E', '&#101;', '\\u0065']
        }

    def augment(self, payload):
        """Applies character substitutions for augmentation."""
        augmented = list(payload)
        for i, char in enumerate(augmented):
            if char in self.char_map and random.random() > 0.8:
                augmented[i] = random.choice(self.char_map[char])
        return "".join(augmented)

if __name__ == "__main__":
    ensemble = SecurityFeatureEnsemble()
    print(f"Features: {ensemble.extract_features('<script>alert(1)</script>')}")
    augmentor = PayloadAugmentor()
    print(f"Augmented: {augmentor.augment('alert(1)')}")
