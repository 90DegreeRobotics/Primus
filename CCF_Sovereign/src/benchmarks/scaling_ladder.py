"""Empirical Primus scaling ladder for one 12 GB CUDA card.

This is a throughput and memory experiment, not a capability experiment. The
Council corpus is intentionally reused only to measure the current training
harness at approximately 5M, 15M, 50M, and 150M parameters. Its loss curve must
not be interpreted as evidence of generalization or world-model quality.
"""
from __future__ import annotations

import argparse
import gc
import json
import math
import random
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator

import torch
import torch.nn as nn
import torch.nn.functional as F
from tokenizers import Tokenizer
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.trainers import BpeTrainer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from substrate.mamba_custom import MambaBackbone
from training.candidate_run import CandidateRun, sha256_file


@dataclass(frozen=True)
class LadderRung:
    name: str
    target_parameters: int
    model_dim: int
    layers: int
    d_state: int = 16
    d_conv: int = 4
    expand: int = 2


RUNGS = (
    LadderRung("5m", 5_000_000, model_dim=256, layers=11),
    LadderRung("15m", 15_000_000, model_dim=384, layers=16),
    LadderRung("50m", 50_000_000, model_dim=640, layers=20),
    LadderRung("150m", 150_000_000, model_dim=896, layers=30),
)
RUNG_BY_NAME = {rung.name: rung for rung in RUNGS}
SPECIAL_TOKENS = ("<pad>", "<unk>", "<bos>", "<eos>")


class TiedLadderModel(nn.Module):
    """Small-vocabulary Mamba LM with no 4096→512 bottleneck.

    The output projection is tied to the token embedding through ``F.linear``;
    there is no second vocabulary-sized parameter matrix.
    """

    def __init__(self, rung: LadderRung, vocab_size: int):
        super().__init__()
        self.rung = rung
        self.vocab_size = int(vocab_size)
        self.embedding = nn.Embedding(self.vocab_size, rung.model_dim)
        self.backbone = MambaBackbone(
            model_dim=rung.model_dim,
            internal_dim=rung.model_dim,
            n_layers=rung.layers,
            d_state=rung.d_state,
            d_conv=rung.d_conv,
            expand=rung.expand,
            dropout=0.0,
        )

    @property
    def tied_weight(self) -> torch.Tensor:
        return self.embedding.weight

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        hidden = self.embedding(token_ids)
        hidden, _ = self.backbone(hidden, return_field_state=False)
        return F.linear(hidden, self.embedding.weight)


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def format_training_text(turn: dict) -> str:
    return (
        f"User: {turn.get('prompt', '')}\n\n"
        f"Assistant: {turn.get('response', '')}"
    )


def load_corpus(jsonl_path: Path) -> list[str]:
    texts = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                texts.append(format_training_text(json.loads(line)))
    if not texts:
        raise RuntimeError(f"training corpus is empty: {jsonl_path}")
    return texts


def train_small_bpe(
    texts: Iterable[str],
    *,
    vocab_size: int,
) -> Tokenizer:
    tokenizer = Tokenizer(BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=False)
    tokenizer.decoder = ByteLevelDecoder()
    trainer = BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=2,
        special_tokens=list(SPECIAL_TOKENS),
        show_progress=False,
    )
    tokenizer.train_from_iterator(texts, trainer=trainer)
    return tokenizer


def tokenize_corpus(tokenizer: Tokenizer, texts: Iterable[str]) -> list[int]:
    bos = tokenizer.token_to_id("<bos>")
    eos = tokenizer.token_to_id("<eos>")
    if bos is None or eos is None:
        raise RuntimeError("trained tokenizer is missing BOS/EOS tokens")
    token_ids = []
    for text in texts:
        token_ids.append(bos)
        token_ids.extend(tokenizer.encode(text).ids)
        token_ids.append(eos)
    return token_ids


def fixed_blocks(token_ids: list[int], sequence_length: int) -> torch.Tensor:
    width = sequence_length + 1
    usable = (len(token_ids) // width) * width
    if usable < width:
        raise RuntimeError("tokenized corpus is shorter than one training block")
    return torch.tensor(token_ids[:usable], dtype=torch.long).view(-1, width)


def iter_batches(
    blocks: torch.Tensor,
    *,
    batch_size: int,
    epochs: int,
    seed: int,
    max_steps: int | None,
) -> Iterator[torch.Tensor]:
    yielded = 0
    for epoch in range(epochs):
        generator = torch.Generator().manual_seed(seed + epoch)
        order = torch.randperm(len(blocks), generator=generator)
        for start in range(0, len(order), batch_size):
            if max_steps is not None and yielded >= max_steps:
                return
            selection = order[start : start + batch_size]
            if len(selection) < batch_size:
                continue
            yielded += 1
            yield blocks[selection]


def batch_probe_sizes(max_batch_size: int) -> list[int]:
    sizes = []
    value = 1
    while value <= max_batch_size:
        sizes.append(value)
        value *= 2
    if sizes and sizes[-1] != max_batch_size:
        sizes.append(max_batch_size)
    return sorted(set(sizes))


def synchronize(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def clear_device(device: torch.device) -> None:
    gc.collect()
    if device.type == "cuda":
        torch.cuda.empty_cache()


def train_rung(
    rung: LadderRung,
    *,
    vocab_size: int,
    blocks: torch.Tensor,
    batch_size: int,
    epochs: int,
    seed: int,
    max_steps: int | None,
    learning_rate: float,
    device: torch.device,
    candidate_run: CandidateRun,
    tokenizer_sha256: str,
    probe_max_batch_size: int,
) -> dict:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    model = TiedLadderModel(rung, vocab_size).to(device)
    parameters = parameter_count(model)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=0.01,
    )
    scaler = torch.amp.GradScaler("cuda") if device.type == "cuda" else None
    candidate_run.mark_training_started(
        config={
            "experiment": "ccf_scaling_ladder_v1",
            "rung": asdict(rung),
            "actual_parameters": parameters,
            "vocab_size": vocab_size,
            "tied_embedding_head": True,
            "internal_dim_equals_model_dim": True,
            "tokenizer_sha256": tokenizer_sha256,
            "learning_rate": learning_rate,
        },
        turns=int(len(blocks)),
        epochs=epochs,
        batch_size=batch_size,
        max_sequence_length=int(blocks.shape[1] - 1),
        device=str(device),
    )

    total_loss = 0.0
    total_tokens = 0
    completed_steps = 0
    started = time.perf_counter()
    oom = False
    oom_message = None
    try:
        for batch in iter_batches(
            blocks,
            batch_size=batch_size,
            epochs=epochs,
            seed=seed,
            max_steps=max_steps,
        ):
            batch = batch.to(device, non_blocking=True)
            inputs = batch[:, :-1]
            targets = batch[:, 1:]
            optimizer.zero_grad(set_to_none=True)
            if scaler:
                with torch.amp.autocast("cuda"):
                    logits = model(inputs)
                    loss = F.cross_entropy(
                        logits.reshape(-1, logits.size(-1)),
                        targets.reshape(-1),
                    )
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                logits = model(inputs)
                loss = F.cross_entropy(
                    logits.reshape(-1, logits.size(-1)),
                    targets.reshape(-1),
                )
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            completed_steps += 1
            total_tokens += int(targets.numel())
            total_loss += float(loss.detach().cpu())
            if completed_steps == 1 or completed_steps % 50 == 0:
                print(
                    f"[{rung.name}] step={completed_steps} "
                    f"loss={float(loss.detach().cpu()):.4f}"
                )
        synchronize(device)
    except torch.cuda.OutOfMemoryError as error:
        oom = True
        oom_message = str(error)
        synchronize(device)

    elapsed = time.perf_counter() - started
    peak_reserved_gb = 0.0
    peak_allocated_gb = 0.0
    if device.type == "cuda":
        peak_reserved_gb = torch.cuda.max_memory_reserved(device) / 1e9
        peak_allocated_gb = torch.cuda.max_memory_allocated(device) / 1e9

    probe_results = []
    if not oom and completed_steps > 0:
        model.eval()
        probe_source = blocks[0, :-1]
        for probe_batch in batch_probe_sizes(probe_max_batch_size):
            clear_device(device)
            if device.type == "cuda":
                torch.cuda.reset_peak_memory_stats(device)
            try:
                probe = probe_source.unsqueeze(0).repeat(probe_batch, 1).to(device)
                with torch.no_grad():
                    with torch.amp.autocast(
                        "cuda",
                        enabled=device.type == "cuda",
                    ):
                        _ = model(probe)
                synchronize(device)
                probe_results.append(
                    {
                        "batch_size": probe_batch,
                        "status": "ok",
                        "peak_reserved_gb": (
                            torch.cuda.max_memory_reserved(device) / 1e9
                            if device.type == "cuda"
                            else 0.0
                        ),
                    }
                )
            except torch.cuda.OutOfMemoryError as error:
                probe_results.append(
                    {
                        "batch_size": probe_batch,
                        "status": "oom",
                        "error": str(error),
                    }
                )
                break

    result = {
        "rung": asdict(rung),
        "actual_parameters": parameters,
        "parameter_error_fraction": (
            parameters - rung.target_parameters
        ) / rung.target_parameters,
        "vocab_size": vocab_size,
        "sequence_length": int(blocks.shape[1] - 1),
        "batch_size": batch_size,
        "epochs": epochs,
        "max_steps": max_steps,
        "completed_steps": completed_steps,
        "prediction_tokens": total_tokens,
        "elapsed_seconds": elapsed,
        "tokens_per_second": total_tokens / max(elapsed, 1e-9),
        "mean_training_loss": (
            total_loss / completed_steps if completed_steps else None
        ),
        "peak_reserved_gb": peak_reserved_gb,
        "peak_allocated_gb": peak_allocated_gb,
        "status": "oom" if oom else "completed",
        "oom_message": oom_message,
        "inference_batch_probe": probe_results,
        "interpretation": (
            "Harness and hardware measurement only. The corpus is far too "
            "small for a capability or scaling-law claim."
        ),
    }

    if oom:
        candidate_run.mark_failed(
            RuntimeError(f"CUDA OOM after {completed_steps} steps: {oom_message}")
        )
    else:
        checkpoint = candidate_run.save_checkpoint(
            {
                "model_state_dict": model.state_dict(),
                "rung": asdict(rung),
                "actual_parameters": parameters,
                "vocab_size": vocab_size,
                "seed": seed,
                "experiment": "ccf_scaling_ladder_v1",
            },
            epoch=epochs,
            metrics=result,
        )
        candidate_run.mark_completed()
        result["checkpoint_path"] = str(checkpoint)
        result["checkpoint_sha256"] = sha256_file(checkpoint)

    del optimizer
    del model
    clear_device(device)
    return result


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-prefix",
        required=True,
        help="Unique prefix used for all candidate IDs and local evidence.",
    )
    parser.add_argument(
        "--rungs",
        default="5m,15m,50m,150m",
        help="Comma-separated subset of 5m,15m,50m,150m.",
    )
    parser.add_argument("--vocab-size", type=int, default=2048)
    parser.add_argument("--sequence-length", type=int, default=256)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--seed", type=int, default=20260826)
    parser.add_argument("--probe-max-batch-size", type=int, default=32)
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Construct each model on CPU and print exact parameter counts.",
    )
    args = parser.parse_args(argv)
    if args.vocab_size < len(SPECIAL_TOKENS) + 256:
        parser.error("--vocab-size is too small for byte-level coverage")
    for name in (
        "sequence_length",
        "batch_size",
        "epochs",
        "probe_max_batch_size",
    ):
        if getattr(args, name) <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    if args.max_steps is not None and args.max_steps <= 0:
        parser.error("--max-steps must be positive")
    selected = [item.strip() for item in args.rungs.split(",") if item.strip()]
    unknown = [item for item in selected if item not in RUNG_BY_NAME]
    if unknown:
        parser.error(f"unknown rung(s): {', '.join(unknown)}")
    args.selected_rungs = [RUNG_BY_NAME[item] for item in selected]
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.describe:
        for rung in args.selected_rungs:
            model = TiedLadderModel(rung, args.vocab_size)
            print(
                f"{rung.name}: target={rung.target_parameters:,} "
                f"actual={parameter_count(model):,} "
                f"D={rung.model_dim} L={rung.layers}"
            )
            del model
        return 0

    if not torch.cuda.is_available():
        raise RuntimeError("the scaling ladder requires CUDA")
    device = torch.device("cuda")
    corpus_path = ROOT / "training" / "training_data" / "council_turns.jsonl"
    texts = load_corpus(corpus_path)
    tokenizer = train_small_bpe(texts, vocab_size=args.vocab_size)
    output_dir = (
        ROOT.parent
        / "docs"
        / "defense_evidence"
        / "local_runs"
        / args.run_prefix
    )
    output_dir.mkdir(parents=True, exist_ok=False)
    tokenizer_path = output_dir / "tokenizer.json"
    tokenizer.save(str(tokenizer_path))
    tokenizer_hash = sha256_file(tokenizer_path)
    token_ids = tokenize_corpus(tokenizer, texts)
    blocks = fixed_blocks(token_ids, args.sequence_length)

    summary = {
        "experiment": "ccf_scaling_ladder_v1",
        "run_prefix": args.run_prefix,
        "created_at_epoch_seconds": time.time(),
        "code_commit": None,
        "device": torch.cuda.get_device_name(0),
        "cuda_total_memory_gb": (
            torch.cuda.get_device_properties(0).total_memory / 1e9
        ),
        "tokenizer": {
            "requested_vocab_size": args.vocab_size,
            "actual_vocab_size": tokenizer.get_vocab_size(),
            "sha256": tokenizer_hash,
            "path": str(tokenizer_path),
        },
        "corpus": {
            "turns": len(texts),
            "tokens": len(token_ids),
            "blocks": len(blocks),
            "sequence_length": args.sequence_length,
            "sha256": sha256_file(corpus_path),
        },
        "settings": {
            "batch_size": args.batch_size,
            "epochs": args.epochs,
            "max_steps": args.max_steps,
            "learning_rate": args.learning_rate,
            "seed": args.seed,
            "probe_max_batch_size": args.probe_max_batch_size,
        },
        "results": [],
        "interpretation_warning": (
            "This ladder validates harness behavior and measures hardware. "
            "Its loss curve is not evidence of capability or generalization."
        ),
    }

    for rung_index, rung in enumerate(args.selected_rungs):
        candidate_id = f"{args.run_prefix}-{rung.name}"
        print("=" * 78)
        print(
            f"RUNG {rung.name}: target={rung.target_parameters:,}, "
            f"D={rung.model_dim}, L={rung.layers}"
        )
        print("=" * 78)
        candidate_run = CandidateRun.create(
            project_root=ROOT,
            candidate_id=candidate_id,
            seed=args.seed + rung_index,
        )
        summary["code_commit"] = candidate_run.manifest["code_commit"]
        result = train_rung(
            rung,
            vocab_size=tokenizer.get_vocab_size(),
            blocks=blocks,
            batch_size=args.batch_size,
            epochs=args.epochs,
            seed=args.seed + rung_index,
            max_steps=args.max_steps,
            learning_rate=args.learning_rate,
            device=device,
            candidate_run=candidate_run,
            tokenizer_sha256=tokenizer_hash,
            probe_max_batch_size=args.probe_max_batch_size,
        )
        summary["results"].append(result)
        write_json(output_dir / "scaling_ladder.json", summary)
        if result["status"] == "oom":
            print(
                f"[{rung.name}] OOM reached; stopping larger rungs because "
                "the current scan ceiling has been observed."
            )
            break

    write_json(output_dir / "scaling_ladder.json", summary)
    print(f"Evidence: {output_dir / 'scaling_ladder.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
