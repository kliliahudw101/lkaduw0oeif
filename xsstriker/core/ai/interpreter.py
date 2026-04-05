import torch
import torch.nn.functional as F

class AttentionInterpreter:
    """Layer 1: Explainable AI (Highlighting malicious tokens)."""
    def __init__(self, classifier):
        self.classifier = classifier
        self.tokenizer = classifier.tokenizer

    def interpret(self, text):
        """Highlights the tokens that most contribute to the XSS label."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        input_ids = inputs['input_ids'].to(self.classifier.device)
        attention_mask = inputs['attention_mask'].to(self.classifier.device)

        # Simple interpretation using attention or gradient
        # (For this demo, we'll use a simplified saliency map approach)
        self.classifier.model.eval()

        # Get embeddings to track gradients
        embeddings = self.classifier.model.distilroberta.get_input_embeddings()(input_ids)
        embeddings.retain_grad()

        # Forward pass
        logits = self.classifier.model(input_ids, attention_mask=attention_mask)
        target_score = logits[0, 1] # Score for XSS label

        # Backward pass
        self.classifier.model.zero_grad()
        target_score.backward()

        # Calculate importance (saliency)
        saliency = torch.norm(embeddings.grad, dim=2).squeeze(0) # [seq_len]
        saliency = saliency / saliency.sum()

        # Map saliency to tokens
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids[0])
        token_importance = []
        for token, score in zip(tokens, saliency.tolist()):
            if token not in [self.tokenizer.pad_token, self.tokenizer.cls_token, self.tokenizer.sep_token]:
                token_importance.append({"token": token, "importance": round(score, 4)})

        # Sort by importance
        token_importance.sort(key=lambda x: x["importance"], reverse=True)

        return {
            "explanation": "Tokens identified as malicious",
            "top_tokens": token_importance[:10]
        }

if __name__ == "__main__":
    # Mock initialization
    pass
