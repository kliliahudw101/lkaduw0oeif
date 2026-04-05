import torch
import torch.nn as nn
from transformers import AutoTokenizer
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
import os
from .model import HybridXSSModel

class XSSDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        label = self.labels[item]
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )
        return {
            'text': text,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class XSSClassifier:
    """Layer 1: Enhanced Detection Engine (Hybrid AI Architecture)"""
    def __init__(self, model_name="distilroberta-base", local_path=None):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Load Hybrid Model
        # Note: 'MISSING' or 'UNEXPECTED' warnings are expected when loading
        # a base pre-trained model into a custom architecture.
        # They disappear after the first --train or --update-cves call.
        self.model = HybridXSSModel(model_name=model_name)

        if local_path and os.path.exists(local_path):
            try:
                state_dict = torch.load(os.path.join(local_path, "pytorch_model.bin"), map_location=self.device)
                self.model.load_state_dict(state_dict)
                print(f"[*] Loaded local model from {local_path}")
            except Exception as e:
                print(f"[!] Error loading local model: {e}")

        self.model.to(self.device)
        self.model.eval()

    def predict(self, text):
        """Classifies the payload as XSS (1) or Safe (0)."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)

        with torch.no_grad():
            logits = self.model(input_ids, attention_mask=attention_mask)
            probabilities = torch.softmax(logits, dim=1)

        confidence, label = torch.max(probabilities, dim=1)

        # Heuristic override for safety if not fully trained
        xss_indicators = ["<script", "alert(", "onerror", "onload", "javascript:", "eval("]
        if any(ind in text.lower() for ind in xss_indicators):
            if label.item() == 0: # If AI missed it
                 return {"label": "XSS", "confidence": 0.99, "ai_label": 0}

        return {
            "label": "XSS" if label.item() == 1 else "Safe",
            "confidence": confidence.item(),
            "probabilities": probabilities.tolist()[0]
        }

    def train_from_scratch(self, train_texts, train_labels, epochs=5, batch_size=16, lr=2e-5):
        """Fine-tuning logic for 1.8M dataset or custom payloads."""
        if not train_texts:
            print("[!] No data provided for training. Skipping.")
            return

        print(f"[*] Starting fine-tuning hybrid model on {len(train_texts)} samples...")
        train_dataset = XSSDataset(train_texts, train_labels, self.tokenizer)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        optimizer = AdamW(self.model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()
        self.model.train()

        for epoch in range(epochs):
            total_loss = 0
            for batch in train_loader:
                optimizer.zero_grad()
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                logits = self.model(input_ids, attention_mask=attention_mask)
                loss = criterion(logits, labels)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            print(f"Epoch {epoch+1}/{epochs} - Loss: {total_loss/len(train_loader):.4f}")

        self.model.eval()
        print("[+] Training complete.")

    def save_model(self, path="xstriker_model"):
        os.makedirs(path, exist_ok=True)
        torch.save(self.model.state_dict(), os.path.join(path, "pytorch_model.bin"))
        self.tokenizer.save_pretrained(path)
        print(f"[+] Model saved to {path}")

if __name__ == "__main__":
    classifier = XSSClassifier()
    # Example training call
    # classifier.train_from_scratch(["<script>alert(1)</script>", "hello world"], [1, 0])
