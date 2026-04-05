import sys
import os

# Add aura_engine core to sys.path for internal imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from core.generator import generator as payload_gen
from core.htmlParser import htmlParser
from core.checker import checker as reflection_checker
from core.filterChecker import filterChecker
from utils.logger import log_error, log_info

class AuraEngine:
    """System 3: Native Payload Generation & Context Analysis (AuraEngine)"""
    def __init__(self):
        self.parser = htmlParser()
        self.reflection_checker = reflection_checker
        self.filter_checker = filterChecker

    def generate_native_payloads(self, occurences):
        """Generates payloads using the integrated AuraEngine (XSStrike-based) logic."""
        payloads = []
        try:
             # Occurences are context objects from htmlParser
             payloads = payload_gen(occurences, [])
             return payloads
        except Exception as e:
             log_error(f"AuraEngine Error (generate_payloads): {e}")
             return []

    def analyze_page_context(self, response_text, probe):
        """Analyzes the reflection context of a probe string."""
        try:
            occurences = self.parser(response_text, probe)
            return occurences
        except Exception as e:
            log_error(f"AuraEngine Error (analyze_page_context): {e}")
            return []

if __name__ == "__main__":
    engine = AuraEngine()
    # print(engine.analyze_page_context("<html><body>probe</body></html>", "probe"))
