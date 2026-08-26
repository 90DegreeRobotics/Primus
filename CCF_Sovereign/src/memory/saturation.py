"""
Saturation detection for NeuroCognica Sleep Architecture v0.1.

Sleep is triggered by measurable pressure, not mythology.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

import torch
import torch.nn.functional as F

from core.config import SovereignConfig
from memory.steb import STEB


@dataclass(frozen=True)
class SaturationReport:
    steb_fill_ratio: float
    mean_surprise: float
    surprise_entropy: float
    fast_weight_drift: float
    novelty_rate: float
    conflict_score: float
    composite: float
    soft_threshold: float
    hard_threshold: float
    should_sleep_soft: bool
    should_sleep_hard: bool
    reasons: tuple[str, ...]

    @property
    def should_sleep(self) -> bool:
        return self.should_sleep_soft or self.should_sleep_hard

    def to_dict(self) -> dict:
        return {
            "steb_fill_ratio": self.steb_fill_ratio,
            "mean_surprise": self.mean_surprise,
            "surprise_entropy": self.surprise_entropy,
            "fast_weight_drift": self.fast_weight_drift,
            "novelty_rate": self.novelty_rate,
            "conflict_score": self.conflict_score,
            "composite": self.composite,
            "soft_threshold": self.soft_threshold,
            "hard_threshold": self.hard_threshold,
            "should_sleep_soft": self.should_sleep_soft,
            "should_sleep_hard": self.should_sleep_hard,
            "should_sleep": self.should_sleep,
            "reasons": list(self.reasons),
        }


def _entropy_from_values(values: Sequence[float], bins: int = 16) -> float:
    if not values:
        return 0.0
    tensor = torch.tensor(list(values), dtype=torch.float32)
    if tensor.numel() == 1:
        return 0.0
    hist = torch.histc(tensor, bins=bins, min=float(tensor.min()), max=float(tensor.max()) + 1e-6)
    probs = hist / hist.sum().clamp_min(1e-8)
    probs = probs[probs > 0]
    return float(-(probs * probs.log()).sum().item())


def _fast_weight_drift(mind: torch.nn.Module) -> float:
    if not hasattr(mind, "fast_weights"):
        return 0.0
    weight = mind.fast_weights.weight.detach()
    identity = torch.eye(weight.shape[0], device=weight.device, dtype=weight.dtype)
    return float(torch.norm(weight - identity, p="fro").item())


def _conflict_score(steb: STEB, max_pairs: int = 32) -> float:
    """
    Approximate representational conflict among recent episodes.

    High cosine similarity between token-id histograms of episodes that have
    very different surprise magnitudes is treated as pressure (crowding).
    """
    episodes = list(steb.buffer)
    if len(episodes) < 2:
        return 0.0

    vectors = []
    surprises = []
    for ep in episodes[-max_pairs:]:
        ids = ep.token_ids.detach().flatten().to(dtype=torch.long)
        if ids.numel() == 0:
            continue
        # Compact bag-of-tokens signature in a fixed hash space.
        bins = torch.zeros(64, dtype=torch.float32)
        hashed = ids % 64
        bins.scatter_add_(0, hashed.cpu(), torch.ones_like(hashed, dtype=torch.float32).cpu())
        bins = F.normalize(bins, dim=0)
        vectors.append(bins)
        surprises.append(float(ep.surprise))

    if len(vectors) < 2:
        return 0.0

    mat = torch.stack(vectors)
    sim = mat @ mat.T
    conflict = 0.0
    count = 0
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            surprise_gap = abs(surprises[i] - surprises[j])
            # Similar token signatures with large surprise gap → interference pressure.
            conflict += float(sim[i, j].item()) * (1.0 + surprise_gap)
            count += 1
    return conflict / max(count, 1)


class SaturationMonitor:
    """Compute measurable saturation from STEB + model state."""

    def __init__(self, config: SovereignConfig):
        self.config = config
        self._surprise_window: list[float] = []
        self._window_limit = int(getattr(config, "SATURATION_SURPRISE_WINDOW", 128))

    def observe_surprise(self, surprise: float) -> None:
        self._surprise_window.append(float(surprise))
        if len(self._surprise_window) > self._window_limit:
            self._surprise_window = self._surprise_window[-self._window_limit :]

    def measure(self, steb: STEB, mind: Optional[torch.nn.Module] = None) -> SaturationReport:
        fill = len(steb) / max(steb.max_episodes, 1)
        surprises = [float(ep.surprise) for ep in steb.buffer] or list(self._surprise_window)
        mean_surprise = float(sum(surprises) / len(surprises)) if surprises else 0.0
        surprise_entropy = _entropy_from_values(surprises)
        drift = _fast_weight_drift(mind) if mind is not None else 0.0
        novelty = 0.0
        if self._surprise_window:
            thr = float(self.config.MIN_SURPRISE_THRESHOLD)
            novelty = sum(1 for s in self._surprise_window if s > thr) / len(self._surprise_window)
        conflict = _conflict_score(steb)

        # Weighted composite in [0, ~2+]. Tunable via config weights.
        w_fill = float(self.config.SATURATION_W_FILL)
        w_surprise = float(self.config.SATURATION_W_SURPRISE)
        w_entropy = float(self.config.SATURATION_W_ENTROPY)
        w_drift = float(self.config.SATURATION_W_DRIFT)
        w_novelty = float(self.config.SATURATION_W_NOVELTY)
        w_conflict = float(self.config.SATURATION_W_CONFLICT)

        composite = (
            w_fill * fill
            + w_surprise * min(mean_surprise / max(self.config.MIN_SURPRISE_THRESHOLD, 1e-6), 3.0) / 3.0
            + w_entropy * min(surprise_entropy / 3.0, 1.0)
            + w_drift * min(drift / max(self.config.SATURATION_DRIFT_NORM, 1e-6), 1.0)
            + w_novelty * novelty
            + w_conflict * min(conflict / max(self.config.SATURATION_CONFLICT_NORM, 1e-6), 1.0)
        )

        soft = float(self.config.SATURATION_SOFT_THRESHOLD)
        hard = float(self.config.SATURATION_HARD_THRESHOLD)
        reasons = []
        if fill >= self.config.SATURATION_STEB_SOFT_FILL:
            reasons.append(f"steb_fill={fill:.2f}")
        if mean_surprise >= self.config.MIN_SURPRISE_THRESHOLD * 1.5:
            reasons.append(f"mean_surprise={mean_surprise:.2f}")
        if drift >= self.config.SATURATION_DRIFT_SOFT:
            reasons.append(f"fast_weight_drift={drift:.3f}")
        if novelty >= self.config.SATURATION_NOVELTY_SOFT:
            reasons.append(f"novelty_rate={novelty:.2f}")
        if conflict >= self.config.SATURATION_CONFLICT_SOFT:
            reasons.append(f"conflict={conflict:.3f}")
        if composite >= soft:
            reasons.append(f"composite={composite:.3f}>={soft:.3f}")

        should_soft = composite >= soft or fill >= self.config.SATURATION_STEB_SOFT_FILL
        should_hard = composite >= hard or fill >= self.config.SATURATION_STEB_HARD_FILL

        return SaturationReport(
            steb_fill_ratio=fill,
            mean_surprise=mean_surprise,
            surprise_entropy=surprise_entropy,
            fast_weight_drift=drift,
            novelty_rate=novelty,
            conflict_score=conflict,
            composite=composite,
            soft_threshold=soft,
            hard_threshold=hard,
            should_sleep_soft=should_soft,
            should_sleep_hard=should_hard,
            reasons=tuple(reasons),
        )
