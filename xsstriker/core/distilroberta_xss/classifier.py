import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class XSSClassifier:
    """Layer 1: Detection Engine (DistilRoBERTa Core)"""
    def __init__(self, model_name="distilbert/distilroberta-base", local_path=None):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load pre-trained or local model
        if local_path:
            self.tokenizer = AutoTokenizer.from_pretrained(local_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(local_path)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

        self.model.to(self.device)
        self.model.eval()

    def predict(self, text):
        """Classifies the payload as XSS or Safe and returns confidence score."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)

        confidence, label = torch.max(probabilities, dim=1)

        # Mock logic: for now, if it contains common XSS patterns, label it XSS (1)
        # In a real scenario, the model would be fine-tuned with weights.
        xss_patterns = ["<script", "alert(", "onerror=", "onload=", "javascript:"]
        is_xss_pattern = any(p in text.lower() for p in xss_patterns)

        final_label = label.item()
        if is_xss_pattern:
            final_label = 1
            confidence = torch.tensor([0.99]) # High confidence for patterns

        result = {
            "label": "XSS" if final_label == 1 else "Safe",
            "confidence": confidence.item(),
            "probabilities": probabilities.tolist()[0]
        }
        return result

    def fine_tune_step(self, texts, labels, learning_rate=2e-5):
        """Used for online learning or initial training."""
        self.model.train()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)

        inputs = self.tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        labels_tensor = torch.tensor(labels).to(self.device)

        optimizer.zero_grad()
        outputs = self.model(**inputs, labels=labels_tensor)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        self.model.eval()
        return loss.item()

if __name__ == "__main__":
    classifier = XSSClassifier()
    test_payload = "<script>alert(1)</script>"
    print(f"Payload: {test_payload}")
    print(f"Prediction: {classifier.predict(test_payload)}")
