import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class QNetwork(nn.Module):
    """Deep Q-Network for RL Agent policy."""
    def __init__(self, state_dim, action_dim):
        super(QNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )

    def forward(self, x):
        return self.fc(x)

class HAXSSAgent:
    """Hierarchical RL Agent coordinating Escape and Sanitization layers (PPO/DQN style)."""
    def __init__(self, state_dim=47, use_icm=True):
        from .agents import EscapeAgent, SanitizationAgent
        from .reward_system import RewardSystem

        self.escape_agent = EscapeAgent()
        self.sanitization_agent = SanitizationAgent()
        self.reward_system = RewardSystem()

        self.state_dim = state_dim
        self.action_dim_esc = len(self.escape_agent.rules)
        self.action_dim_san = len(self.sanitization_agent.mutations)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Policy Networks
        self.q_esc = QNetwork(state_dim, self.action_dim_esc).to(self.device)
        self.q_san = QNetwork(state_dim, self.action_dim_san).to(self.device)

        self.optimizer_esc = optim.Adam(self.q_esc.parameters(), lr=1e-3)
        self.optimizer_san = optim.Adam(self.q_san.parameters(), lr=1e-3)

        self.epsilon = 0.1  # Exploration rate
        self.gamma = 0.99   # Discount factor

    def _get_state_vector(self, context):
        """Encodes context into a 47-feature vector (Placeholder for actual encoding)."""
        state = np.zeros(self.state_dim)
        # Simple encoding for demo
        if context.get("type") == "html": state[0] = 1
        elif context.get("type") == "attribute": state[1] = 1
        elif context.get("type") == "script": state[2] = 1
        return torch.FloatTensor(state).to(self.device)

    def generate_payload(self, context):
        """Select actions using epsilon-greedy policy."""
        state = self._get_state_vector(context)

        # Escape layer action
        if random.random() < self.epsilon:
            esc_idx = random.randint(0, self.action_dim_esc - 1)
        else:
            with torch.no_grad():
                esc_idx = torch.argmax(self.q_esc(state)).item()

        esc_rule = self.escape_agent.rules[esc_idx]
        base_payload = self.escape_agent.act(esc_rule)

        # Sanitization layer action
        if random.random() < self.epsilon:
            san_idx = random.randint(0, self.action_dim_san - 1)
        else:
            with torch.no_grad():
                san_idx = torch.argmax(self.q_san(state)).item()

        san_rule = self.sanitization_agent.mutations[san_idx]
        final_payload = self.sanitization_agent.obfuscate(base_payload, san_rule)

        # Store indices for update
        self.last_esc_idx = esc_idx
        self.last_san_idx = san_idx
        self.last_state = state

        return final_payload

    def update(self, payload, result, context):
        """Update Q-networks based on feedback (Deep Q-Learning update)."""
        reward = self.reward_system.calculate_reward(result)
        reward_tensor = torch.FloatTensor([reward]).to(self.device)

        # Simplified DQN update for demo
        # Update Escape Policy
        q_val_esc = self.q_esc(self.last_state)[self.last_esc_idx]
        loss_esc = nn.MSELoss()(q_val_esc, reward_tensor)
        self.optimizer_esc.zero_grad()
        loss_esc.backward()
        self.optimizer_esc.step()

        # Update Sanitization Policy
        q_val_san = self.q_san(self.last_state)[self.last_san_idx]
        loss_san = nn.MSELoss()(q_val_san, reward_tensor)
        self.optimizer_san.zero_grad()
        loss_san.backward()
        self.optimizer_san.step()

        print(f"[*] HAXSS Update - Reward: {reward}, Loss (Esc/San): {loss_esc.item():.4f}/{loss_san.item():.4f}")
        return reward

if __name__ == "__main__":
    haxss = HAXSSAgent()
    payload = haxss.generate_payload({"type": "html"})
    haxss.update(payload, "success", {"type": "html"})
