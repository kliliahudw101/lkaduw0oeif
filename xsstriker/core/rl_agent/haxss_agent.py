from .agents import EscapeAgent, SanitizationAgent
from .reward_system import RewardSystem

class HAXSSAgent:
    """Hierarchical RL Agent coordinating Escape and Sanitization layers."""
    def __init__(self, use_icm=True):
        self.escape_agent = EscapeAgent()
        self.sanitization_agent = SanitizationAgent()
        self.reward_system = RewardSystem()
        self.use_icm = use_icm  # Intrinsic Curiosity Module (simplified for demo)

    def generate_payload(self, context):
        """Level 1: Escape current context, then Level 2: Apply obfuscation."""
        # Level 1: Context Breaking
        base_payload = self.escape_agent.act(context)

        # Level 2: Apply mutation for filter bypass
        final_payload = self.sanitization_agent.obfuscate(base_payload)

        return final_payload

    def update(self, payload, result, context):
        """Update agent policy based on feedback and rewards."""
        reward = self.reward_system.calculate_reward(result)
        # RL update logic (placeholder for PPO/DQN update)
        print(f"[*] Payload updated with reward: {reward}")

        return reward

if __name__ == "__main__":
    haxss = HAXSSAgent()
    payload = haxss.generate_payload({"type": "html"})
    print(f"Generated Payload: {payload}")
    haxss.update(payload, "success", {"type": "html"})
