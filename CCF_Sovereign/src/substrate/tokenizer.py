"""
Simple tokenizer wrapper for MVP
"""
import torch

class SimpleTokenizer:
    """Minimal tokenizer for MVP - wraps a basic GPT-2 tokenizer"""

    def __init__(self):
        try:
            from transformers import AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
            self.vocab_size = self.tokenizer.vocab_size
        except Exception as e:
            print(f"[Tokenizer] Warning: Could not load GPT-2 tokenizer: {e}")
            print("[Tokenizer] Using fallback character-level tokenizer")
            self.tokenizer = None
            self.vocab_size = 256  # Byte-level fallback

    def encode(self, text: str) -> torch.Tensor:
        """Convert text to token IDs"""
        if self.tokenizer:
            return torch.tensor(self.tokenizer.encode(text), dtype=torch.long)
        else:
            # Fallback: byte-level encoding
            return torch.tensor([ord(c) % 256 for c in text], dtype=torch.long)

    def decode(self, token_ids: torch.Tensor) -> str:
        """Convert token IDs back to text"""
        if self.tokenizer:
            return self.tokenizer.decode(token_ids.tolist())
        else:
            # Fallback: byte-level decoding
            return ''.join([chr(int(t)) for t in token_ids])
