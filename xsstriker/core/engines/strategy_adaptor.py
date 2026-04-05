import random
from utils.logger import log_error, log_info

class StrategyAdaptor:
    """System 4: AI-Driven Self-Correction & Strategy Adaptation (StrategyAdaptor)"""
    def __init__(self):
        self.block_patterns = {
            403: "WAF_BLOCK",
            406: "WAF_FILTER",
            501: "PROTOCOL_ERROR",
            429: "RATE_LIMIT"
        }
        self.retry_count = 0
        self.max_retries = 3

    def analyze_failure(self, status_code, response_text, last_payload):
        """Analyzes a failure (e.g., WAF block) and suggests a new strategy."""
        log_info(f"[*] Analyzing failure: Status {status_code} for payload {last_payload}")

        strategy = {
            "action": "mutate",
            "mutation_type": "random_case",
            "evasion_level": 1
        }

        # Case 1: WAF/Filter Block (Status 403 or 406)
        if status_code in [403, 406]:
            log_info("[!] WAF detected! Adapting strategy for evasion.")
            strategy["mutation_type"] = random.choice([
                "double_encode", "hex_entities", "js_unicode", "null_bytes", "comment_injection"
            ])
            strategy["evasion_level"] = 2

            # If common mutations fail, try more advanced ones
            if "blocked" in response_text.lower() or "forbidden" in response_text.lower():
                strategy["mutation_type"] = "svg_wrapper"
                strategy["evasion_level"] = 3

        # Case 2: Rate Limit (Status 429)
        elif status_code == 429:
            log_info("[!] Rate limiting detected! Slowing down and adding delays.")
            strategy["action"] = "delay"
            strategy["delay_seconds"] = 5

        # Case 3: Empty Response or Connection issues
        elif status_code is None or status_code >= 500:
             log_info("[!] Connection/Server error. Reducing concurrency and retrying.")
             strategy["action"] = "retry"
             strategy["concurrency_reduction"] = 0.5

        return strategy

    def adapt_payload(self, payload, strategy, sanitization_agent):
        """Applies the suggested strategy to adapt the payload."""
        if strategy["action"] == "mutate":
             return sanitization_agent.obfuscate(payload, rule=strategy["mutation_type"])
        return payload

if __name__ == "__main__":
    adaptor = StrategyAdaptor()
    # print(adaptor.analyze_failure(403, "Forbidden by WAF", "<script>alert(1)</script>"))
