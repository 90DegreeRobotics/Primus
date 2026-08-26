"""CCF Sovereign candidate-training entry point.

Every run is isolated beneath ``checkpoints/candidates/<candidate_id>`` and
refuses to start unless the frozen parent and corpus manifest hashes match the
August 26 evidence boundary. This script never promotes a candidate.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from core.config import SovereignConfig
from substrate.model import CCFSubstrate
from substrate.tokenizer import SimpleTokenizer
from training.candidate_run import CandidateRun


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train an isolated, evidence-bound Primus candidate."
    )
    parser.add_argument(
        "--candidate-id",
        required=True,
        help="Unique run identifier; an existing destination is rejected.",
    )
    parser.add_argument("--seed", type=int, default=20260826)
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Defaults to 15 on CUDA and 5 on CPU.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Gradient-accumulation sequence count; defaults to 4/2.",
    )
    parser.add_argument(
        "--max-seq-len",
        type=int,
        default=None,
        help="Defaults to 256 on CUDA and 128 on CPU.",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=5,
        help="Checkpoint interval in epochs; the final epoch is always saved.",
    )
    args = parser.parse_args(argv)
    for name in ("epochs", "batch_size", "max_seq_len", "save_every"):
        value = getattr(args, name)
        if value is not None and value <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    return args


def resolve_device(requested: str) -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")
    return torch.device(requested)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_training_data(jsonl_path: Path) -> list[dict]:
    """Load conversation turns from JSONL."""
    turns = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                turns.append(json.loads(line))
    return turns


def prepare_conversation_batch(
    turns: list[dict],
    tokenizer: SimpleTokenizer,
    max_length: int = 512,
) -> list[torch.Tensor]:
    """Convert conversation turns into bounded training sequences."""
    sequences = []
    for turn in turns:
        prompt = turn.get("prompt", "")
        response = turn.get("response", "")
        text = f"User: {prompt}\n\nAssistant: {response}"
        tokens = tokenizer.encode(text)
        if len(tokens) > max_length:
            tokens = tokens[:max_length]
        sequences.append(torch.as_tensor(tokens, dtype=torch.long).clone())
    return sequences


def train_epoch(
    model: CCFSubstrate,
    sequences: list[torch.Tensor],
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    *,
    batch_size: int = 4,
    use_amp: bool = True,
    scheduler: torch.optim.lr_scheduler.LRScheduler | None = None,
) -> tuple[float, int, float]:
    """Train one epoch and return loss, prediction-token count, and seconds."""
    model.train()
    total_loss = 0.0
    num_valid = 0
    prediction_tokens = 0
    started = time.perf_counter()
    scaler = (
        torch.amp.GradScaler("cuda")
        if use_amp and device.type == "cuda"
        else None
    )
    permutation = torch.randperm(len(sequences)).tolist()
    current_lr = optimizer.param_groups[0]["lr"]
    print(
        f"\n[Training] {len(sequences)} sequences, "
        f"accum={batch_size}, lr={current_lr:.2e}"
    )
    print(
        f"[Training] Mixed precision: "
        f"{'Enabled' if scaler else 'Disabled'}"
    )

    optimizer.zero_grad()
    accumulated_loss = 0.0
    accumulated_count = 0

    for index, sequence_index in enumerate(permutation):
        sequence = sequences[sequence_index]
        if len(sequence) < 2:
            continue
        sequence = sequence.to(device)
        prediction_tokens += int(sequence.numel() - 1)

        if scaler:
            with torch.amp.autocast("cuda"):
                logits, _, _ = model(
                    sequence.unsqueeze(0),
                    compute_surprise=False,
                )
                loss = F.cross_entropy(
                    logits[:, :-1, :].reshape(-1, logits.size(-1)),
                    sequence[1:].reshape(-1),
                ) / batch_size
            scaler.scale(loss).backward()
        else:
            logits, _, _ = model(
                sequence.unsqueeze(0),
                compute_surprise=False,
            )
            loss = F.cross_entropy(
                logits[:, :-1, :].reshape(-1, logits.size(-1)),
                sequence[1:].reshape(-1),
            ) / batch_size
            loss.backward()

        loss_value = loss.item() * batch_size
        if math.isfinite(loss_value):
            accumulated_loss += loss_value
            accumulated_count += 1

        should_step = (
            (index + 1) % batch_size == 0
            or (index + 1) == len(sequences)
        )
        if should_step:
            if scaler:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            optimizer.zero_grad()
            if scheduler is not None:
                scheduler.step()
            if accumulated_count > 0:
                total_loss += accumulated_loss / accumulated_count
                num_valid += 1
            accumulated_loss = 0.0
            accumulated_count = 0

        if (index + 1) % 80 == 0 or index == 0:
            progress = ((index + 1) / len(sequences)) * 100
            print(
                f"  [{progress:5.1f}%] Seq {index + 1}/"
                f"{len(sequences)}: Loss = {loss_value:.4f}"
            )

    elapsed = time.perf_counter() - started
    average_loss = total_loss / num_valid if num_valid else 0.0
    return average_loss, prediction_tokens, elapsed


def build_optimizer(
    model: CCFSubstrate,
    config: SovereignConfig,
) -> torch.optim.Optimizer:
    try:
        from galore_torch import GaLoreAdamW

        print("[Optimizer] Using GaLore for efficient training")
        return GaLoreAdamW(
            model.parameters(),
            lr=config.SLEEP_LEARNING_RATE,
            rank=config.GALORE_RANK,
        )
    except ImportError:
        print(
            f"[Optimizer] AdamW "
            f"(lr={config.TRAINING_LEARNING_RATE})"
        )
        return torch.optim.AdamW(
            model.parameters(),
            lr=config.TRAINING_LEARNING_RATE,
            weight_decay=0.01,
        )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    seed_everything(args.seed)
    device = resolve_device(args.device)
    epochs = args.epochs or (15 if device.type == "cuda" else 5)
    batch_size = args.batch_size or (4 if device.type == "cuda" else 2)
    max_sequence_length = args.max_seq_len or (
        256 if device.type == "cuda" else 128
    )

    print("=" * 70)
    print("  CCF SOVEREIGN - ISOLATED CANDIDATE TRAINING")
    print("  Candidate output only; parent promotion is impossible here.")
    print("=" * 70)
    print(f"[Config] Candidate: {args.candidate_id}")
    print(f"[Config] Seed: {args.seed}")
    print(f"[Config] Device: {device}")
    if device.type == "cuda":
        print(f"[Config] GPU: {torch.cuda.get_device_name(0)}")
        memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"[Config] VRAM: {memory:.1f} GB")
        torch.cuda.reset_peak_memory_stats(0)

    run: CandidateRun | None = None
    try:
        run = CandidateRun.create(
            project_root=ROOT,
            candidate_id=args.candidate_id,
            seed=args.seed,
        )
        print(f"[Safety] Candidate directory: {run.candidate_dir}")
        print("[Safety] Parent and corpus hashes verified")

        config = SovereignConfig()
        turns = load_training_data(run.training_data_path)
        tokenizer = SimpleTokenizer()
        model = CCFSubstrate(config).to(device)
        sequences = prepare_conversation_batch(
            turns,
            tokenizer,
            max_length=max_sequence_length,
        )
        print(f"[Data] Loaded {len(turns)} conversation turns")
        print(
            f"[Prep] Created {len(sequences)} sequences "
            f"(max length: {max_sequence_length})"
        )
        print(f"[Model] Dimension: {config.MODEL_DIM}")
        print(
            f"[Model] Parameters: "
            f"{sum(parameter.numel() for parameter in model.parameters()):,}"
        )

        optimizer = build_optimizer(model, config)
        steps_per_epoch = math.ceil(len(sequences) / batch_size)
        total_steps = epochs * steps_per_epoch
        warmup_epochs = min(2, epochs)
        warmup_steps = warmup_epochs * steps_per_epoch

        def lr_lambda(step: int) -> float:
            if step < warmup_steps:
                return step / max(1, warmup_steps)
            progress = (step - warmup_steps) / max(
                1,
                total_steps - warmup_steps,
            )
            return 0.1 + 0.9 * 0.5 * (
                1 + math.cos(math.pi * progress)
            )

        scheduler = torch.optim.lr_scheduler.LambdaLR(
            optimizer,
            lr_lambda,
        )
        run.mark_training_started(
            config=config.__dict__,
            turns=len(turns),
            epochs=epochs,
            batch_size=batch_size,
            max_sequence_length=max_sequence_length,
            device=str(device),
        )

        print(
            f"[Training] Starting {epochs} epochs; accum={batch_size}; "
            f"warmup={warmup_epochs} epoch(s)"
        )
        for epoch in range(1, epochs + 1):
            print(f"\n{'=' * 70}")
            print(f"  EPOCH {epoch}/{epochs}")
            print(f"{'=' * 70}")
            average_loss, prediction_tokens, elapsed = train_epoch(
                model,
                sequences,
                optimizer,
                device,
                batch_size=batch_size,
                scheduler=scheduler,
            )
            tokens_per_second = prediction_tokens / max(elapsed, 1e-9)
            peak_vram_gb = 0.0
            if device.type == "cuda":
                peak_vram_gb = (
                    torch.cuda.max_memory_reserved(0) / 1e9
                )
                print(f"[GPU] Peak reserved: {peak_vram_gb:.2f} GB")
            print(
                f"[Epoch {epoch}] loss={average_loss:.4f}, "
                f"tokens/s={tokens_per_second:.1f}"
            )

            should_save = (
                epoch % args.save_every == 0 or epoch == epochs
            )
            if should_save:
                checkpoint_path = run.save_checkpoint(
                    {
                        "model_state_dict": model.state_dict(),
                        "config": config.__dict__,
                        "training_turns": len(turns),
                        "epochs": epoch,
                        "candidate_id": args.candidate_id,
                        "seed": args.seed,
                    },
                    epoch=epoch,
                    metrics={
                        "average_loss": average_loss,
                        "prediction_tokens": prediction_tokens,
                        "elapsed_seconds": elapsed,
                        "tokens_per_second": tokens_per_second,
                        "peak_vram_gb": peak_vram_gb,
                    },
                )
                print(f"[Save] Isolated checkpoint: {checkpoint_path}")

        run.mark_completed()
        print("\n" + "=" * 70)
        print("  CANDIDATE TRAINING COMPLETE")
        print("=" * 70)
        print(f"Manifest: {run.manifest_path}")
        print(f"Candidate output: {run.candidate_dir}")
        print("No promotion was performed; no capability claim is implied.")
        return 0
    except BaseException as error:
        if run is not None:
            run.mark_failed(error)
        print(f"\n[FAILED] {type(error).__name__}: {error}")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
