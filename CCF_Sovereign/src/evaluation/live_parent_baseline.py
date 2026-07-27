"""
Live no-training parent baseline for CCF evidence runs.

The command in this module loads a real parent checkpoint, creates a shadow
manifest, runs deterministic parent-only generation on outreach-safe prompts,
and writes raw JSON evidence to an ignored local path.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import torch

from .shadow_baseline import BaselineRunResult, run_no_training_parent_baseline
from .shadow_manifest import (
    BenchmarkCase,
    ShadowCycleManifest,
    create_shadow_cycle_manifest,
)

CCF_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = CCF_ROOT.parent
SRC_ROOT = CCF_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

try:  # Supports tests that put CCF_Sovereign/src on sys.path.
    from core.config import SovereignConfig
    from substrate.model import CCFSubstrate
    from substrate.tokenizer import SimpleTokenizer
except ModuleNotFoundError:  # Supports python -m src.evaluation.live_parent_baseline.
    from src.core.config import SovereignConfig
    from src.substrate.model import CCFSubstrate
    from src.substrate.tokenizer import SimpleTokenizer


LIVE_BASELINE_CYCLE_ID = "shadow-001-parent-baseline"
LIVE_BASELINE_RUN_ID = "parent-baseline-001"

DEFAULT_CHECKPOINT_PATH = (
    CCF_ROOT / "checkpoints" / "primus_council_trained.pt"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "docs"
    / "defense_evidence"
    / "local_runs"
    / LIVE_BASELINE_CYCLE_ID
)


DEFAULT_BENCHMARK_CASES: tuple[BenchmarkCase, ...] = (
    BenchmarkCase(
        case_id="cognitive-sovereignty-definition",
        prompt=(
            "User: In one concise paragraph, define cognitive sovereignty for "
            "a defense engineer.\n\nAssistant:"
        ),
        expected_contains=("sovereignty",),
        protected=True,
        tags=("outreach-safe", "governance"),
    ),
    BenchmarkCase(
        case_id="uncontrolled-learning-risk",
        prompt=(
            "User: Name one risk of uncontrolled online learning in an "
            "autonomous system.\n\nAssistant:"
        ),
        expected_contains=("risk",),
        protected=True,
        tags=("outreach-safe", "safety"),
    ),
    BenchmarkCase(
        case_id="audit-log-value",
        prompt=(
            "User: State why audit logs matter for adaptive software.\n\n"
            "Assistant:"
        ),
        expected_contains=("audit",),
        protected=True,
        tags=("outreach-safe", "evidence"),
    ),
)


@dataclass(frozen=True)
class LiveBaselineArtifacts:
    manifest: ShadowCycleManifest
    result: BaselineRunResult
    manifest_path: Path
    result_path: Path
    metadata_path: Path
    device: str
    checkpoint_metadata: dict

    def summary(self) -> dict:
        return {
            "cycle_id": self.manifest.cycle_id,
            "run_id": self.result.run_id,
            "device": self.device,
            "manifest_path": str(self.manifest_path),
            "result_path": str(self.result_path),
            "metadata_path": str(self.metadata_path),
            "manifest_sha256": self.manifest.manifest_sha256(),
            "result_sha256": self.result.result_sha256(),
            "parent": self.manifest.parent.to_dict(),
            "aggregate": self.result.aggregate(),
            "checkpoint_metadata": self.checkpoint_metadata,
        }


def build_live_parent_manifest(
    checkpoint_path: Path = DEFAULT_CHECKPOINT_PATH,
    cycle_id: str = LIVE_BASELINE_CYCLE_ID,
    benchmark_cases: tuple[BenchmarkCase, ...] = DEFAULT_BENCHMARK_CASES,
    root: Path = REPO_ROOT,
) -> ShadowCycleManifest:
    return create_shadow_cycle_manifest(
        cycle_id=cycle_id,
        parent_checkpoint=checkpoint_path,
        training_inputs=(),
        benchmark_cases=benchmark_cases,
        root=root,
        notes=(
            "Live no-training parent baseline. No training inputs, candidate "
            "artifact, promotion, or mutation are permitted in this run."
        ),
    )


def select_device(requested: str) -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")
    if requested not in {"cpu", "cuda"}:
        raise ValueError(f"unsupported device: {requested}")
    return torch.device(requested)


def load_checkpoint_payload(path: Path, device: torch.device) -> tuple[dict, str]:
    try:
        return torch.load(path, map_location=device, weights_only=True), "weights_only"
    except TypeError:
        return torch.load(path, map_location=device), "legacy_pickle"


def load_parent_model(
    checkpoint_path: Path,
    device: torch.device,
) -> tuple[CCFSubstrate, SimpleTokenizer, dict]:
    checkpoint, load_mode = load_checkpoint_payload(checkpoint_path, device)
    if not isinstance(checkpoint, dict):
        raise TypeError(
            f"checkpoint payload must be dict, got {type(checkpoint).__name__}"
        )
    if "model_state_dict" not in checkpoint:
        raise KeyError("checkpoint missing required key: model_state_dict")

    config = SovereignConfig()
    tokenizer = SimpleTokenizer()
    model = CCFSubstrate(config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    metadata = {
        "checkpoint_load_mode": load_mode,
        "training_turns": checkpoint.get("training_turns"),
        "epochs": checkpoint.get("epochs"),
        "tokenizer_backend": getattr(tokenizer, "backend", "unknown"),
        "tokenizer_local_files_only": getattr(
            tokenizer,
            "local_files_only",
            None,
        ),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
    }
    return model, tokenizer, metadata


def extract_assistant_response(decoded: str, prompt: str) -> str:
    marker = "Assistant:"
    if marker in decoded:
        return decoded.rsplit(marker, 1)[-1].strip()
    if decoded.startswith(prompt):
        return decoded[len(prompt):].strip()
    return decoded.strip()


def generate_greedy_response(
    model: CCFSubstrate,
    tokenizer: SimpleTokenizer,
    prompt: str,
    max_new_tokens: int = 64,
) -> str:
    device = next(model.parameters()).device
    encoded = tokenizer.encode(prompt)
    generated = encoded.tolist() if isinstance(encoded, torch.Tensor) else list(encoded)
    eos_token_id = (
        tokenizer.tokenizer.eos_token_id
        if getattr(tokenizer, "tokenizer", None) is not None
        else None
    )

    with torch.no_grad():
        for _ in range(max_new_tokens):
            input_tensor = torch.tensor(
                [generated],
                dtype=torch.long,
                device=device,
            )
            logits, _, _ = model(input_tensor, compute_surprise=False)
            next_token = int(torch.argmax(logits[0, -1, :]).item())
            if eos_token_id is not None and next_token == eos_token_id:
                break
            if len(generated) > 10 and generated[-1] == generated[-2] == next_token:
                break
            generated.append(next_token)

    decoded = tokenizer.decode(torch.tensor(generated, dtype=torch.long))
    return extract_assistant_response(decoded, prompt)


def run_live_parent_baseline(
    checkpoint_path: Path = DEFAULT_CHECKPOINT_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    cycle_id: str = LIVE_BASELINE_CYCLE_ID,
    run_id: str = LIVE_BASELINE_RUN_ID,
    max_new_tokens: int = 64,
    device_request: str = "auto",
) -> LiveBaselineArtifacts:
    checkpoint_path = checkpoint_path.resolve()
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"parent checkpoint not found: {checkpoint_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    result_path = output_dir / "parent_baseline.json"
    metadata_path = output_dir / "run_metadata.json"

    manifest = build_live_parent_manifest(
        checkpoint_path=checkpoint_path,
        cycle_id=cycle_id,
    )
    manifest.save(manifest_path)

    device = select_device(device_request)
    model, tokenizer, checkpoint_metadata = load_parent_model(checkpoint_path, device)

    def responder(prompt: str) -> str:
        return generate_greedy_response(
            model,
            tokenizer,
            prompt,
            max_new_tokens=max_new_tokens,
        )

    result = run_no_training_parent_baseline(
        manifest,
        responder,
        output_path=result_path,
        run_id=run_id,
    )

    artifacts = LiveBaselineArtifacts(
        manifest=manifest,
        result=result,
        manifest_path=manifest_path,
        result_path=result_path,
        metadata_path=metadata_path,
        device=str(device),
        checkpoint_metadata=checkpoint_metadata,
    )
    metadata_path.write_text(
        json.dumps(
            {
                "created_at_utc": datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat(),
                "max_new_tokens": max_new_tokens,
                "summary": artifacts.summary(),
            },
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return artifacts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the live no-training CCF parent baseline."
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=DEFAULT_CHECKPOINT_PATH,
        help="Path to the ignored local parent checkpoint.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Ignored local directory for raw manifest/result artifacts.",
    )
    parser.add_argument("--cycle-id", default=LIVE_BASELINE_CYCLE_ID)
    parser.add_argument("--run-id", default=LIVE_BASELINE_RUN_ID)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    artifacts = run_live_parent_baseline(
        checkpoint_path=args.checkpoint,
        output_dir=args.output_dir,
        cycle_id=args.cycle_id,
        run_id=args.run_id,
        max_new_tokens=args.max_new_tokens,
        device_request=args.device,
    )
    print(json.dumps(artifacts.summary(), ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
