class RewardSystem:
    """Layer 2: Reward calculation system based on fuzzing results."""
    def __init__(self):
        self.rewards = {
            "success": 10,      # XSS triggered (alert executed)
            "bypass": 5,        # Filter/WAF bypass detected
            "escape": 1,        # Successful context escape
            "failure": -2,      # Invalid syntax or filter block
            "neutral": 0
        }

    def calculate_reward(self, status):
        """Returns reward based on the result of a payload attempt."""
        return self.rewards.get(status, self.rewards["neutral"])

if __name__ == "__main__":
    rs = RewardSystem()
    print(f"Reward for success: {rs.calculate_reward('success')}")
    print(f"Reward for failure: {rs.calculate_reward('failure')}")
