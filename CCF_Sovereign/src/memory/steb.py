"""
Short-Term Episodic Buffer (STEB)
The Hippocampus analog - stores high-surprise sequences for consolidation during sleep.
"""
import torch
import zstandard as zstd
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Episode:
    """A single high-surprise memory episode"""
    token_ids: torch.Tensor
    surprise: float
    timestamp: float
    hidden_state: torch.Tensor = None

class STEB:
    """Short-Term Episodic Buffer - Hippocampal memory for consolidation"""

    def __init__(self, max_episodes: int = 512, surprise_threshold: float = 2.5):
        self.max_episodes = max_episodes
        self.surprise_threshold = surprise_threshold
        self.buffer = deque(maxlen=max_episodes)
        self.compressor = zstd.ZstdCompressor(level=3)

    def push(self, episode: Episode):
        """Store high-surprise episode for later consolidation"""
        if episode.surprise > self.surprise_threshold:
            self.buffer.append(episode)
            print(f"[STEB] Stored episode (surprise={episode.surprise:.2f}, buffer={len(self.buffer)}/{self.max_episodes})")

    def sample_batch(self, batch_size: int = 16) -> List[Episode]:
        """Sample random episodes for replay during sleep"""
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        import random
        indices = random.sample(range(len(self.buffer)), batch_size)
        return [self.buffer[i] for i in indices]

    def clear(self):
        """Clear buffer after consolidation"""
        self.buffer.clear()
        print("[STEB] Buffer cleared after consolidation")

    def __len__(self):
        return len(self.buffer)
