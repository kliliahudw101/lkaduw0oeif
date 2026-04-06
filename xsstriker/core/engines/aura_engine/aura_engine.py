import sys
import os

# Add the current directory and its 'core' subdirectory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
if os.path.join(current_dir, 'core') not in sys.path:
    sys.path.append(os.path.join(current_dir, 'core'))

# Internal XSStrike-based imports (AuraEngine refactored core)
from generator import generator as payload_gen
from htmlParser import htmlParser
from checker import checker as reflection_checker
from filterChecker import filterChecker
from utils.logger import log_error, log_info

class AuraEngine:
    """System 3: Native Payload Generation & Context Analysis (AuraEngine)"""
    def __init__(self):
        # Functions in XSStrike are direct, not classes
        self.parser = htmlParser
        self.reflection_checker = reflection_checker
        self.filter_checker = filterChecker

    def generate_native_payloads(self, occurences, response):
        """Generates payloads using the integrated AuraEngine (XSStrike-based) logic."""
        payloads = []
        try:
             # Occurences are context objects from htmlParser
             # XSStrike generator takes (occurences, response)
             payloads = payload_gen(occurences, response)
             return payloads
        except Exception as e:
             log_error(f"AuraEngine Error (generate_payloads): {e}")
             return []

    def analyze_page_context(self, response_obj):
        """Analyzes the reflection context of a probe string."""
        try:
            # XSStrike htmlParser takes (response_obj, encoding)
            occurences = self.parser(response_obj, None)
            return occurences
        except Exception as e:
            log_error(f"AuraEngine Error (analyze_page_context): {e}")
            return []

if __name__ == "__main__":
    engine = AuraEngine()
    # print(engine.analyze_page_context(response_obj))
