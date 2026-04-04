import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig

class HybridXSSModel(nn.Module):
    """
    Advanced Hybrid Architecture:
    DistilRoBERTa (Context) + 1D-CNN (Character Patterns) + Context Gating
    """
    def __init__(self, model_name="distilroberta-base", num_labels=2):
        super(HybridXSSModel, self).__init__()
        self.config = AutoConfig.from_pretrained(model_name)
        self.distilroberta = AutoModel.from_pretrained(model_name)

        # 1D-CNN for character-level feature extraction (catches obfuscation)
        self.cnn = nn.Sequential(
            nn.Conv1d(in_channels=self.config.hidden_size, out_channels=256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(in_channels=256, out_channels=128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveMaxPool1d(1) # Flatten to 128
        )

        # Security Feature Ensemble (Handcrafted features)
        self.security_head = nn.Sequential(
            nn.Linear(128 + self.config.hidden_size, 256),
            nn.Dropout(0.2),
            nn.ReLU(),
            nn.Linear(256, num_labels)
        )

    def forward(self, input_ids, attention_mask):
        # 1. Transformer context embeddings
        outputs = self.distilroberta(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = outputs.last_hidden_state # [batch, seq, hidden]

        # 2. CNN path (transpose for Conv1d: [batch, hidden, seq])
        cnn_input = last_hidden_state.transpose(1, 2)
        cnn_features = self.cnn(cnn_input).squeeze(-1) # [batch, 128]

        # 3. Global context (CLS token)
        cls_embeddings = last_hidden_state[:, 0, :] # [batch, hidden]

        # 4. Concatenate features
        combined = torch.cat((cls_embeddings, cnn_features), dim=1)

        # 5. Final classification
        logits = self.security_head(combined)
        return logits

if __name__ == "__main__":
    model = HybridXSSModel()
    print("Hybrid AI Model initialized successfully.")
