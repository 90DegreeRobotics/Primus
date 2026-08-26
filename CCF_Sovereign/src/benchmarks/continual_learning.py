"""
Phase I continual-learning benchmark:

Baseline continual learner (train through tasks with no sleep metabolism)
    vs
NeuroCognica lifecycle learner (WAKE accumulate → SLEEP consolidate/validate/seal)

Measures retention, forgetting, adaptation, memory growth, contradictions, seal integrity.

This is the fundable falsifiable experiment — substrate-independent.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from core.config import SovereignConfig
from lifecycles.sleep_architecture import SleepArchitecture
from memory.canonical import CanonicalMemory
from memory.forever_law import ForeverLawCodex
from memory.saturation import SaturationMonitor
from memory.steb import Episode, STEB
from substrate.model import CCFSubstrate


@dataclass(frozen=True)
class Task:
    name: str
    sequences: tuple[tuple[int, ...], ...]


def make_tasks(vocab: int, seq_len: int = 8) -> list[Task]:
    """
    Two disjoint synthetic tasks with stable patterns.

    Task A: ascending modular runs
    Task B: descending modular runs
    """
    a_seqs = []
    b_seqs = []
    for i in range(16):
        start = (i * 3) % max(vocab - seq_len - 1, 1)
        a = tuple((start + j) % (vocab - 1) + 1 for j in range(seq_len))
        b_start = (vocab - 2 - start) % max(vocab - seq_len - 1, 1)
        b = tuple((b_start - j) % (vocab - 1) + 1 for j in range(seq_len))
        a_seqs.append(a)
        b_seqs.append(b)
    return [
        Task(name="task_A_ascend", sequences=tuple(a_seqs)),
        Task(name="task_B_descend", sequences=tuple(b_seqs)),
    ]


def tiny_config(data_root: str) -> SovereignConfig:
    return SovereignConfig(
        MODEL_DIM=64,
        STATE_DIM=32,
        NUM_LAYERS=2,
        VOCAB_SIZE=128,
        MAMBA_D_STATE=8,
        MAMBA_D_CONV=2,
        MAMBA_EXPAND=2,
        MAMBA_DROPOUT=0.0,
        HRR_DIM=64,
        GALORE_RANK=8,
        SLEEP_LEARNING_RATE=1e-3,
        HEBBIAN_LEARNING_RATE=1e-3,
        MIN_SURPRISE_THRESHOLD=0.01,
        IDLE_TIMEOUT_MINUTES=0,
        NREM_EPOCHS=2,
        NREM_KEEP_FRACTION=0.8,
        NREM_FAST_WEIGHT_DECAY=0.6,
        REM_MAX_CANDIDATES=2,
        REM_GENERATE_TOKENS=8,
        REM_MAX_SEED_TOKENS=16,
        REM_TEMPERATURE=0.8,
        VALIDATE_PROMOTE_THRESHOLD=0.45,
        VALIDATE_REJECT_THRESHOLD=0.25,
        VALIDATE_TRAIN_PROMOTED=True,
        SATURATION_SOFT_THRESHOLD=0.2,
        SATURATION_HARD_THRESHOLD=0.5,
        SATURATION_STEB_SOFT_FILL=0.3,
        SATURATION_STEB_HARD_FILL=0.8,
        STEB_MAX_EPISODES=64,
        DATA_ROOT=data_root,
        FORCE_SLEEP_ON_HARD_SATURATION=True,
    )


def sequence_nll(model: CCFSubstrate, seq: tuple[int, ...], device: str) -> float:
    tokens = torch.tensor(seq, dtype=torch.long, device=device)
    model.eval()
    with torch.no_grad():
        logits, _, _ = model(tokens.unsqueeze(0), compute_surprise=False)
        loss = F.cross_entropy(
            logits[:, :-1, :].reshape(-1, logits.size(-1)),
            tokens[1:].reshape(-1),
        )
    return float(loss.item())


def mean_task_nll(model: CCFSubstrate, task: Task, device: str) -> float:
    values = [sequence_nll(model, seq, device) for seq in task.sequences]
    return sum(values) / max(len(values), 1)


def train_on_sequence(model: CCFSubstrate, seq: tuple[int, ...], device: str, lr: float) -> float:
    tokens = torch.tensor(seq, dtype=torch.long, device=device)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    optimizer.zero_grad()
    logits, _, _ = model(tokens.unsqueeze(0), compute_surprise=False)
    loss = F.cross_entropy(
        logits[:, :-1, :].reshape(-1, logits.size(-1)),
        tokens[1:].reshape(-1),
    )
    loss.backward()
    optimizer.step()
    return float(loss.item())


def contradiction_rate(model: CCFSubstrate, tasks: list[Task], device: str, threshold: float = 4.0) -> float:
    """Fraction of sequences with very high NLL after learning — unresolved conflict proxy."""
    total = 0
    bad = 0
    for task in tasks:
        for seq in task.sequences:
            nll = sequence_nll(model, seq, device)
            total += 1
            if nll > threshold:
                bad += 1
    return bad / max(total, 1)


def run_baseline(config: SovereignConfig, tasks: list[Task], device: str) -> dict[str, Any]:
    torch.manual_seed(0)
    model = CCFSubstrate(config).to(device)
    t0 = time.time()

    # Learn task A then task B with continuous overwrite (no sleep metabolism).
    for seq in tasks[0].sequences:
        train_on_sequence(model, seq, device, lr=config.SLEEP_LEARNING_RATE)
    nll_a_after_a = mean_task_nll(model, tasks[0], device)

    for seq in tasks[1].sequences:
        train_on_sequence(model, seq, device, lr=config.SLEEP_LEARNING_RATE)
    nll_a_after_b = mean_task_nll(model, tasks[0], device)
    nll_b_after_b = mean_task_nll(model, tasks[1], device)

    forgetting = nll_a_after_b - nll_a_after_a
    return {
        "learner": "baseline_continual_overwrite",
        "nll_a_after_a": nll_a_after_a,
        "nll_a_after_b": nll_a_after_b,
        "nll_b_after_b": nll_b_after_b,
        "forgetting_a": forgetting,
        "retention_a": math.exp(-nll_a_after_b),
        "adaptation_b": math.exp(-nll_b_after_b),
        "contradiction_rate": contradiction_rate(model, tasks, device),
        "forever_law_events": 0,
        "integrity_valid": None,
        "cycles": 0,
        "elapsed_sec": time.time() - t0,
    }


def run_lifecycle(config: SovereignConfig, tasks: list[Task], device: str, work_dir: Path) -> dict[str, Any]:
    torch.manual_seed(0)
    work_dir.mkdir(parents=True, exist_ok=True)
    model = CCFSubstrate(config).to(device)
    steb = STEB(max_episodes=config.STEB_MAX_EPISODES, surprise_threshold=config.MIN_SURPRISE_THRESHOLD)
    codex = ForeverLawCodex(work_dir / "forever_law")
    canonical = CanonicalMemory(work_dir / "canonical")
    architecture = SleepArchitecture(
        config=config,
        mind=model,
        steb=steb,
        codex=codex,
        canonical=canonical,
        saturation_monitor=SaturationMonitor(config),
        tokenizer=None,
    )

    t0 = time.time()
    cycles = 0

    def ingest_task(task: Task):
        nonlocal cycles
        for idx, seq in enumerate(task.sequences):
            tokens = torch.tensor(seq, dtype=torch.long)
            # Surprise proxy: use current NLL as wake surprise.
            surprise = sequence_nll(model, seq, device)
            episode = Episode(
                token_ids=tokens,
                surprise=max(surprise, config.MIN_SURPRISE_THRESHOLD + 0.1),
                timestamp=time.time(),
                text=f"{task.name}:{idx}",
            )
            steb.push(episode)
            architecture.record_wake_episode(episode, text=episode.text)
            # Light wake plasticity / acquisition step (not full overwrite of all params).
            with torch.no_grad():
                embeds = model.embeddings(tokens.unsqueeze(0).to(device))
                pre = embeds[:, :-1, :].reshape(-1, embeds.size(-1))
                post = embeds[:, 1:, :].reshape(-1, embeds.size(-1))
                if pre.size(0):
                    model.apply_hebbian_update(pre, post, learning_rate=config.HEBBIAN_LEARNING_RATE)

            sat = architecture.measure_saturation()
            # Sleep on hard saturation or real episodic pressure — not every
            # single surprise spike. Soft saturation alone waits for batching.
            batch_pressure = len(steb) >= max(8, config.STEB_MAX_EPISODES // 8)
            if sat.should_sleep_hard or batch_pressure:
                architecture.run_cycle(force=False)
                cycles += 1

        # End-of-task sleep boundary.
        if len(steb) > 0:
            architecture.run_cycle(force=False)
            cycles += 1

    ingest_task(tasks[0])
    nll_a_after_a = mean_task_nll(model, tasks[0], device)
    ingest_task(tasks[1])
    nll_a_after_b = mean_task_nll(model, tasks[0], device)
    nll_b_after_b = mean_task_nll(model, tasks[1], device)

    integrity = codex.verify_full_chain()
    forgetting = nll_a_after_b - nll_a_after_a
    return {
        "learner": "neurocognica_sleep_architecture_v0_1",
        "nll_a_after_a": nll_a_after_a,
        "nll_a_after_b": nll_a_after_b,
        "nll_b_after_b": nll_b_after_b,
        "forgetting_a": forgetting,
        "retention_a": math.exp(-nll_a_after_b),
        "adaptation_b": math.exp(-nll_b_after_b),
        "contradiction_rate": contradiction_rate(model, tasks, device),
        "forever_law_events": len(codex),
        "canonical_beliefs": len(canonical),
        "integrity_valid": integrity.valid,
        "merkle_root": integrity.merkle_root,
        "cycles": cycles,
        "elapsed_sec": time.time() - t0,
    }


def compare(baseline: dict[str, Any], lifecycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "forgetting_delta": baseline["forgetting_a"] - lifecycle["forgetting_a"],
        "retention_delta": lifecycle["retention_a"] - baseline["retention_a"],
        "adaptation_delta": lifecycle["adaptation_b"] - baseline["adaptation_b"],
        "contradiction_delta": baseline["contradiction_rate"] - lifecycle["contradiction_rate"],
        "lifecycle_wins_forgetting": lifecycle["forgetting_a"] < baseline["forgetting_a"],
        "lifecycle_integrity_valid": lifecycle["integrity_valid"] is True,
        "lifecycle_has_audit_trail": lifecycle["forever_law_events"] > 0,
    }


def main():
    parser = argparse.ArgumentParser(description="CCF Sleep Architecture continual-learning benchmark")
    parser.add_argument(
        "--out",
        type=str,
        default=str(ROOT / "data" / "benchmarks" / "continual_learning_latest.json"),
    )
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    work = out_path.parent / f"run_{int(time.time())}"

    config = tiny_config(data_root=str(work))
    tasks = make_tasks(config.VOCAB_SIZE)

    print(f"[Benchmark] device={device}")
    print("[Benchmark] Running baseline continual overwrite...")
    baseline = run_baseline(config, tasks, device)
    print("[Benchmark] Running NeuroCognica sleep lifecycle...")
    lifecycle = run_lifecycle(config, tasks, device, work)
    summary = compare(baseline, lifecycle)

    payload = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "device": device,
        "baseline": baseline,
        "lifecycle": lifecycle,
        "comparison": summary,
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"[Benchmark] Wrote {out_path}")

    if not summary["lifecycle_integrity_valid"]:
        raise SystemExit("FAIL: lifecycle Forever Law integrity invalid")
    if not summary["lifecycle_has_audit_trail"]:
        raise SystemExit("FAIL: lifecycle produced no audit trail")


if __name__ == "__main__":
    main()
