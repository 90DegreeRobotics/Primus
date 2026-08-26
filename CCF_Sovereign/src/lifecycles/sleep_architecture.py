"""
NeuroCognica Sleep Architecture v0.1 — substrate-independent cognitive metabolism.

WAKE accumulate → SATURATE → seal T0 → NREM → REM → VALIDATE → seal T1 → WAKE

Dreams never become memory directly. Validation against sealed source events is mandatory.
Failures are recorded, not hidden.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Any, Optional
from uuid import uuid4

import torch
import torch.nn.functional as F

from core.config import SovereignConfig, SystemState
from memory.canonical import CanonicalMemory
from memory.forever_law import ForeverLawCodex
from memory.saturation import SaturationMonitor, SaturationReport
from memory.steb import Episode, STEB


@dataclass
class DreamCandidate:
    candidate_id: str
    token_ids: torch.Tensor
    text: str
    source_event_ids: list[str]
    source_episode_surprises: list[float]
    dream_event_id: Optional[str] = None
    validation_score: float = 0.0
    decision: str = "pending"  # pending|promoted|rejected|uncertain
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class SleepPhaseReport:
    phase: str
    success: bool
    metrics: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "success": self.success,
            "metrics": dict(self.metrics),
            "error": self.error,
        }


@dataclass
class SleepCycleReport:
    cycle_id: str
    saturation: dict[str, Any]
    t0: Optional[dict[str, Any]]
    nrem: SleepPhaseReport
    rem: SleepPhaseReport
    validate: SleepPhaseReport
    t1: Optional[dict[str, Any]]
    integrity_valid: bool
    integrity: dict[str, Any]
    candidates: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "saturation": self.saturation,
            "t0": self.t0,
            "nrem": self.nrem.to_dict(),
            "rem": self.rem.to_dict(),
            "validate": self.validate.to_dict(),
            "t1": self.t1,
            "integrity_valid": self.integrity_valid,
            "integrity": self.integrity,
            "candidates": list(self.candidates),
        }


class SleepArchitecture:
    """
    Orchestrates one full consolidation cycle against a living CCF mind.
    """

    def __init__(
        self,
        config: SovereignConfig,
        mind: torch.nn.Module,
        steb: STEB,
        codex: ForeverLawCodex,
        canonical: CanonicalMemory,
        saturation_monitor: Optional[SaturationMonitor] = None,
        tokenizer=None,
    ):
        self.config = config
        self.mind = mind
        self.steb = steb
        self.codex = codex
        self.canonical = canonical
        self.saturation = saturation_monitor or SaturationMonitor(config)
        self.tokenizer = tokenizer
        self.current_state = SystemState.AWAKE
        self.last_cycle: Optional[SleepCycleReport] = None
        self.episode_event_ids: list[str] = []

    def record_wake_episode(self, episode: Episode, text: str = "") -> str:
        """Append immutable wake evidence for a stored STEB episode."""
        token_ids = episode.token_ids.detach().flatten().to(dtype=torch.long).tolist()
        outcome = self.codex.append(
            archetype="wake",
            event_type="episodic_observation",
            content={
                "surprise": float(episode.surprise),
                "timestamp": float(episode.timestamp),
                "token_ids": token_ids,
                "text": text or episode.text,
                "token_count": len(token_ids),
            },
            layer=1,
        )
        episode.forever_law_event_id = outcome.event_id
        self.episode_event_ids.append(outcome.event_id)
        self.saturation.observe_surprise(float(episode.surprise))
        return outcome.event_id

    def measure_saturation(self) -> SaturationReport:
        return self.saturation.measure(self.steb, self.mind)

    def run_cycle(self, force: bool = False) -> SleepCycleReport:
        """
        Execute NREM → REM → VALIDATE → SEAL.

        Raises no silent failures: phase errors are captured in the report and
        sealed into Forever Law.
        """
        cycle_id = str(uuid4())
        sat = self.measure_saturation()
        if not force and len(self.steb) == 0:
            raise RuntimeError("Cannot run sleep cycle with empty STEB and force=False")

        self.codex.append(
            archetype="sleep_architecture",
            event_type="sleep_cycle_started",
            content={"cycle_id": cycle_id, "saturation": sat.to_dict(), "force": force},
            layer=1,
        )

        t0_anchor = self.codex.seal_boundary(
            boundary="T0",
            extra={"cycle_id": cycle_id, "phase": "pre_consolidation"},
        )

        # Snapshot episodes before NREM may clear STEB.
        episodes = list(self.steb.buffer)

        nrem = self._run_nrem(cycle_id, episodes)
        rem, candidates = self._run_rem(cycle_id, episodes)
        validate = self._run_validate(cycle_id, candidates, episodes)

        t1_anchor = self.codex.seal_boundary(
            boundary="T1",
            extra={
                "cycle_id": cycle_id,
                "phase": "post_consolidation",
                "nrem_success": nrem.success,
                "rem_success": rem.success,
                "validate_success": validate.success,
            },
        )

        integrity = self.codex.verify_full_chain()
        report = SleepCycleReport(
            cycle_id=cycle_id,
            saturation=sat.to_dict(),
            t0=t0_anchor.to_dict(),
            nrem=nrem,
            rem=rem,
            validate=validate,
            t1=t1_anchor.to_dict(),
            integrity_valid=integrity.valid,
            integrity=integrity.to_dict(),
            candidates=[
                {
                    "candidate_id": c.candidate_id,
                    "decision": c.decision,
                    "validation_score": c.validation_score,
                    "source_event_ids": c.source_event_ids,
                    "dream_event_id": c.dream_event_id,
                    "text": c.text,
                    "evidence": c.evidence,
                }
                for c in candidates
            ],
        )
        self.last_cycle = report
        self.codex.append(
            archetype="sleep_architecture",
            event_type="sleep_cycle_completed",
            content=report.to_dict(),
            layer=1,
        )
        self.current_state = SystemState.AWAKE
        # Clear wake episode ID cursor for the next day after a completed cycle.
        if nrem.success:
            self.episode_event_ids.clear()
        return report

    def _build_optimizer(self):
        try:
            from galore_torch import GaLoreAdamW

            return (
                GaLoreAdamW(
                    self.mind.backbone.parameters(),
                    lr=self.config.SLEEP_LEARNING_RATE,
                    rank=self.config.GALORE_RANK,
                ),
                "GaLoreAdamW",
            )
        except ImportError:
            return (
                torch.optim.AdamW(
                    self.mind.backbone.parameters(),
                    lr=self.config.SLEEP_LEARNING_RATE,
                    weight_decay=0.0,
                ),
                "AdamW",
            )

    def _run_nrem(self, cycle_id: str, episodes: list[Episode]) -> SleepPhaseReport:
        self.current_state = SystemState.NREM
        self.codex.append(
            archetype="sleep_architecture",
            event_type="nrem_started",
            content={"cycle_id": cycle_id, "episode_count": len(episodes)},
            layer=1,
        )
        try:
            if not episodes:
                return SleepPhaseReport(
                    phase="NREM",
                    success=False,
                    metrics={"optimized_steps": 0},
                    error="No episodes available for NREM consolidation",
                )

            device = next(self.mind.parameters()).device
            optimizer, optimizer_name = self._build_optimizer()
            # Prefer high-surprise / non-redundant episodes for hard consolidation.
            ranked = sorted(episodes, key=lambda ep: float(ep.surprise), reverse=True)
            keep_n = max(1, int(ceil(len(ranked) * self.config.NREM_KEEP_FRACTION)))
            consolidate = ranked[:keep_n]
            weakened = ranked[keep_n:]

            optimized_steps = 0
            total_loss = 0.0
            self.mind.train()
            for epoch in range(int(self.config.NREM_EPOCHS)):
                for ep in consolidate:
                    token_ids = ep.token_ids.to(device=device, dtype=torch.long).flatten()
                    if token_ids.numel() < 2:
                        continue
                    optimizer.zero_grad()
                    logits, _, _ = self.mind(token_ids.unsqueeze(0), compute_surprise=False)
                    loss = F.cross_entropy(
                        logits[:, :-1, :].reshape(-1, logits.size(-1)),
                        token_ids[1:].reshape(-1),
                    )
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(
                        self.mind.parameters(),
                        float(self.config.GRADIENT_CLIP_NORM),
                    )
                    optimizer.step()
                    optimized_steps += 1
                    total_loss += float(loss.item())

            prune_metrics = self._nrem_prune_fast_weights()
            if optimized_steps > 0:
                self.steb.clear()

            metrics = {
                "optimizer": optimizer_name,
                "optimized_steps": optimized_steps,
                "mean_loss": (total_loss / optimized_steps) if optimized_steps else None,
                "consolidated_episodes": len(consolidate),
                "weakened_episodes": len(weakened),
                "epochs": int(self.config.NREM_EPOCHS),
                **prune_metrics,
            }
            success = optimized_steps > 0
            self.codex.append(
                archetype="sleep_architecture",
                event_type="nrem_completed",
                content={"cycle_id": cycle_id, "success": success, "metrics": metrics},
                layer=1,
            )
            return SleepPhaseReport(phase="NREM", success=success, metrics=metrics)
        except Exception as exc:
            self.codex.append(
                archetype="sleep_architecture",
                event_type="nrem_failed",
                content={"cycle_id": cycle_id, "error": str(exc)},
                layer=1,
            )
            return SleepPhaseReport(phase="NREM", success=False, error=str(exc))

    def _nrem_prune_fast_weights(self) -> dict[str, Any]:
        """Decay fast weights toward identity — structural regularization."""
        if not hasattr(self.mind, "fast_weights"):
            return {"fast_weight_prune": False}
        decay = float(self.config.NREM_FAST_WEIGHT_DECAY)
        with torch.no_grad():
            w = self.mind.fast_weights.weight
            identity = torch.eye(w.shape[0], device=w.device, dtype=w.dtype)
            before = torch.norm(w - identity, p="fro").item()
            w.mul_(decay).add_(identity, alpha=(1.0 - decay))
            after = torch.norm(w - identity, p="fro").item()
        return {
            "fast_weight_prune": True,
            "fast_weight_decay": decay,
            "fast_weight_drift_before": before,
            "fast_weight_drift_after": after,
        }

    def _run_rem(
        self,
        cycle_id: str,
        episodes: list[Episode],
    ) -> tuple[SleepPhaseReport, list[DreamCandidate]]:
        self.current_state = SystemState.REM
        self.codex.append(
            archetype="sleep_architecture",
            event_type="rem_started",
            content={"cycle_id": cycle_id, "episode_count": len(episodes)},
            layer=1,
        )
        candidates: list[DreamCandidate] = []
        try:
            if len(episodes) < 1:
                report = SleepPhaseReport(
                    phase="REM",
                    success=False,
                    error="No episodes available for REM recombination",
                )
                return report, candidates

            device = next(self.mind.parameters()).device
            self.mind.eval()
            max_candidates = int(self.config.REM_MAX_CANDIDATES)
            gen_tokens = int(self.config.REM_GENERATE_TOKENS)

            def _src(ep: Episode) -> list[str]:
                return [ep.forever_law_event_id] if ep.forever_law_event_id else []

            # Pairwise recombination of high-surprise episodes.
            ranked = sorted(episodes, key=lambda ep: float(ep.surprise), reverse=True)
            pairs: list[tuple[Episode, Episode, list[str]]] = []
            for i in range(len(ranked)):
                for j in range(i + 1, len(ranked)):
                    src_ids = list(dict.fromkeys(_src(ranked[i]) + _src(ranked[j])))
                    pairs.append((ranked[i], ranked[j], src_ids))
                    if len(pairs) >= max_candidates:
                        break
                if len(pairs) >= max_candidates:
                    break
            if not pairs:
                # Single-episode hypothesis: continue from the strongest memory.
                pairs = [(ranked[0], ranked[0], _src(ranked[0]))]

            for left, right, src_ids in pairs:
                seed = self._recombine_tokens(left.token_ids, right.token_ids).to(device)
                generated = self._generate_continuation(seed, gen_tokens)
                text = self._decode(generated)
                candidate = DreamCandidate(
                    candidate_id=str(uuid4()),
                    token_ids=generated.detach().cpu(),
                    text=text,
                    source_event_ids=list(src_ids),
                    source_episode_surprises=[float(left.surprise), float(right.surprise)],
                )
                dream_event = self.codex.append(
                    archetype="rem",
                    event_type="dream_candidate",
                    content={
                        "cycle_id": cycle_id,
                        "candidate_id": candidate.candidate_id,
                        "token_ids": generated.detach().cpu().tolist(),
                        "text": text,
                        "source_event_ids": candidate.source_event_ids,
                        "source_episode_surprises": candidate.source_episode_surprises,
                    },
                    causation=list(src_ids),
                    layer=2,
                )
                candidate.dream_event_id = dream_event.event_id
                candidates.append(candidate)

            metrics = {"candidates_generated": len(candidates)}
            self.codex.append(
                archetype="sleep_architecture",
                event_type="rem_completed",
                content={"cycle_id": cycle_id, "metrics": metrics},
                layer=1,
            )
            return SleepPhaseReport(phase="REM", success=True, metrics=metrics), candidates
        except Exception as exc:
            self.codex.append(
                archetype="sleep_architecture",
                event_type="rem_failed",
                content={"cycle_id": cycle_id, "error": str(exc)},
                layer=1,
            )
            return SleepPhaseReport(phase="REM", success=False, error=str(exc)), candidates

    def _recombine_tokens(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        a_ids = a.detach().flatten().to(dtype=torch.long)
        b_ids = b.detach().flatten().to(dtype=torch.long)
        # Interleave prefixes then append suffixes — structural recombination, not copy.
        a_head = a_ids[: max(1, a_ids.numel() // 2)]
        b_head = b_ids[: max(1, b_ids.numel() // 2)]
        merged = []
        for i in range(max(a_head.numel(), b_head.numel())):
            if i < a_head.numel():
                merged.append(int(a_head[i].item()))
            if i < b_head.numel():
                merged.append(int(b_head[i].item()))
        if not merged:
            merged = a_ids.tolist() or b_ids.tolist() or [0]
        # Cap seed length for stable generation.
        max_seed = int(self.config.REM_MAX_SEED_TOKENS)
        return torch.tensor(merged[:max_seed], dtype=torch.long)

    def _generate_continuation(self, seed: torch.Tensor, num_tokens: int) -> torch.Tensor:
        device = next(self.mind.parameters()).device
        tokens = seed.flatten().to(device=device, dtype=torch.long)
        if tokens.numel() == 0:
            tokens = torch.tensor([0], device=device, dtype=torch.long)
        generated = [int(t) for t in tokens.tolist()]
        hidden = None
        temperature = float(self.config.REM_TEMPERATURE)
        with torch.no_grad():
            current = tokens.unsqueeze(0)
            for _ in range(num_tokens):
                logits, hidden, _ = self.mind(current, hidden, compute_surprise=False)
                next_logits = logits[0, -1, :] / max(temperature, 1e-5)
                probs = F.softmax(next_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                tok = int(next_token.item())
                generated.append(tok)
                current = next_token.view(1, 1)
        return torch.tensor(generated, dtype=torch.long)

    def _decode(self, token_ids: torch.Tensor) -> str:
        if self.tokenizer is None:
            return ",".join(str(int(t)) for t in token_ids.tolist())
        try:
            return self.tokenizer.decode(token_ids.cpu())
        except Exception:
            return ",".join(str(int(t)) for t in token_ids.tolist())

    def _run_validate(
        self,
        cycle_id: str,
        candidates: list[DreamCandidate],
        source_episodes: list[Episode],
    ) -> SleepPhaseReport:
        self.current_state = SystemState.VALIDATE
        self.codex.append(
            archetype="sleep_architecture",
            event_type="validate_started",
            content={"cycle_id": cycle_id, "candidate_count": len(candidates)},
            layer=1,
        )
        try:
            promoted = rejected = uncertain = 0
            device = next(self.mind.parameters()).device
            self.mind.eval()

            for candidate in candidates:
                score, evidence = self._score_candidate(candidate, source_episodes, device)
                candidate.validation_score = score
                candidate.evidence = evidence
                promote_thr = float(self.config.VALIDATE_PROMOTE_THRESHOLD)
                reject_thr = float(self.config.VALIDATE_REJECT_THRESHOLD)

                if score >= promote_thr:
                    candidate.decision = "promoted"
                    promoted += 1
                    self.canonical.promote(
                        text=candidate.text,
                        token_ids=candidate.token_ids.tolist(),
                        confidence=score,
                        source_event_ids=candidate.source_event_ids,
                        dream_event_id=candidate.dream_event_id,
                        evidence=evidence,
                        status="promoted",
                    )
                    # Optional: consolidate promoted dream into slow weights once.
                    if self.config.VALIDATE_TRAIN_PROMOTED:
                        self._train_on_tokens(candidate.token_ids.to(device), steps=1)
                elif score <= reject_thr:
                    candidate.decision = "rejected"
                    rejected += 1
                else:
                    candidate.decision = "uncertain"
                    uncertain += 1
                    self.canonical.promote(
                        text=candidate.text,
                        token_ids=candidate.token_ids.tolist(),
                        confidence=score,
                        source_event_ids=candidate.source_event_ids,
                        dream_event_id=candidate.dream_event_id,
                        evidence=evidence,
                        status="uncertain",
                    )

                self.codex.append(
                    archetype="validate",
                    event_type="dream_validation",
                    content={
                        "cycle_id": cycle_id,
                        "candidate_id": candidate.candidate_id,
                        "decision": candidate.decision,
                        "validation_score": candidate.validation_score,
                        "evidence": candidate.evidence,
                        "source_event_ids": candidate.source_event_ids,
                        "dream_event_id": candidate.dream_event_id,
                    },
                    causation=[candidate.dream_event_id] if candidate.dream_event_id else [],
                    layer=1,
                )

            metrics = {
                "promoted": promoted,
                "rejected": rejected,
                "uncertain": uncertain,
                "total": len(candidates),
            }
            self.codex.append(
                archetype="sleep_architecture",
                event_type="validate_completed",
                content={"cycle_id": cycle_id, "metrics": metrics},
                layer=1,
            )
            return SleepPhaseReport(phase="VALIDATE", success=True, metrics=metrics)
        except Exception as exc:
            self.codex.append(
                archetype="sleep_architecture",
                event_type="validate_failed",
                content={"cycle_id": cycle_id, "error": str(exc)},
                layer=1,
            )
            return SleepPhaseReport(phase="VALIDATE", success=False, error=str(exc))

    def _score_candidate(
        self,
        candidate: DreamCandidate,
        source_episodes: list[Episode],
        device: torch.device,
    ) -> tuple[float, dict[str, Any]]:
        """
        Score a dream against sealed source evidence.

        Higher score = lower mean NLL on source episodes under a model briefly
        conditioned by the dream tokens (compatibility), minus gibberish penalty.
        """
        if not source_episodes:
            return 0.0, {"reason": "no_source_episodes"}

        # Baseline source NLL under current mind.
        baseline_nlls = []
        dream_conditioned_nlls = []
        with torch.no_grad():
            for ep in source_episodes:
                tokens = ep.token_ids.to(device=device, dtype=torch.long).flatten()
                if tokens.numel() < 2:
                    continue
                baseline_nlls.append(self._sequence_nll(tokens))
                # Condition by prepending a short dream prefix.
                prefix = candidate.token_ids.to(device=device, dtype=torch.long).flatten()
                prefix = prefix[: int(self.config.VALIDATE_CONDITION_PREFIX)]
                conditioned = torch.cat([prefix, tokens], dim=0)
                # Measure NLL only on the source suffix region.
                dream_conditioned_nlls.append(
                    self._sequence_nll(conditioned, loss_start=prefix.numel())
                )

        if not baseline_nlls:
            return 0.0, {"reason": "no_valid_source_tokens"}

        baseline = sum(baseline_nlls) / len(baseline_nlls)
        conditioned = sum(dream_conditioned_nlls) / len(dream_conditioned_nlls)
        improvement = baseline - conditioned  # positive = dream helps explain sources

        # Gibberish / collapse penalty: repeated tokens and extreme self-NLL.
        dream_tokens = candidate.token_ids.flatten()
        uniq = len(set(int(t) for t in dream_tokens.tolist())) if dream_tokens.numel() else 0
        diversity = uniq / max(dream_tokens.numel(), 1)
        dream_nll = self._sequence_nll(dream_tokens.to(device)) if dream_tokens.numel() >= 2 else 99.0

        # Map improvement into [0,1] with diversity gate.
        raw = torch.sigmoid(torch.tensor(improvement * float(self.config.VALIDATE_SCORE_SCALE)))
        score = float(raw.item()) * (0.5 + 0.5 * diversity)
        if dream_nll > float(self.config.VALIDATE_MAX_DREAM_NLL):
            score *= 0.5

        evidence = {
            "baseline_source_nll": baseline,
            "dream_conditioned_source_nll": conditioned,
            "improvement": improvement,
            "dream_nll": dream_nll,
            "token_diversity": diversity,
            "score": score,
        }
        return score, evidence

    def _sequence_nll(self, token_ids: torch.Tensor, loss_start: int = 0) -> float:
        token_ids = token_ids.flatten().to(dtype=torch.long)
        if token_ids.numel() < 2:
            return 99.0
        logits, _, _ = self.mind(token_ids.unsqueeze(0), compute_surprise=False)
        # logits[t] predicts token[t+1]
        pred = logits[0, :-1, :]
        target = token_ids[1:]
        if loss_start > 0:
            # Skip predictions whose target index is inside the prefix.
            # target index i corresponds to token i+1.
            start = max(loss_start - 1, 0)
            pred = pred[start:]
            target = target[start:]
        if target.numel() == 0:
            return 99.0
        return float(F.cross_entropy(pred, target).item())

    def _train_on_tokens(self, token_ids: torch.Tensor, steps: int = 1) -> None:
        device = next(self.mind.parameters()).device
        token_ids = token_ids.to(device=device, dtype=torch.long).flatten()
        if token_ids.numel() < 2:
            return
        optimizer, _ = self._build_optimizer()
        self.mind.train()
        for _ in range(steps):
            optimizer.zero_grad()
            logits, _, _ = self.mind(token_ids.unsqueeze(0), compute_surprise=False)
            loss = F.cross_entropy(
                logits[:, :-1, :].reshape(-1, logits.size(-1)),
                token_ids[1:].reshape(-1),
            )
            loss.backward()
            optimizer.step()
