"""Explicitly promote one completed Primus candidate checkpoint.

Promotion is intentionally separate from training. It requires the candidate
run manifest, an exact candidate checkpoint digest, and an unchanged frozen
parent boundary. The previous live parent is preserved in the frozen directory.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from training.candidate_run import (
    CANDIDATE_ROOT_RELATIVE_PATH,
    CandidateSafetyError,
    EXPECTED_PARENT_SHA256,
    PARENT_RELATIVE_PATH,
    RUN_MANIFEST_NAME,
    _validate_candidate_id,
    atomic_write_json,
    relative_display,
    sha256_file,
    utc_now,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Atomically promote one completed, hash-verified candidate."
    )
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument(
        "--expected-candidate-sha256",
        required=True,
        help="Exact SHA-256 printed from the completed run manifest.",
    )
    return parser.parse_args(argv)


def promote_candidate(
    project_root: Path,
    candidate_id: str,
    expected_candidate_sha256: str,
) -> Path:
    project_root = project_root.resolve()
    repo_root = project_root.parent.resolve()
    candidate_id = _validate_candidate_id(candidate_id)
    candidate_dir = (
        project_root / CANDIDATE_ROOT_RELATIVE_PATH / candidate_id
    ).resolve()
    manifest_path = candidate_dir / RUN_MANIFEST_NAME
    if not manifest_path.is_file():
        raise CandidateSafetyError(
            f"candidate run manifest is missing: {manifest_path}"
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed":
        raise CandidateSafetyError(
            f"candidate is not completed: {manifest.get('status')}"
        )
    latest = manifest.get("latest_checkpoint")
    if not latest:
        raise CandidateSafetyError("candidate has no checkpoint to promote")

    checkpoint_path = (repo_root / latest["path"]).resolve()
    if not checkpoint_path.is_relative_to(candidate_dir):
        raise CandidateSafetyError(
            "manifest checkpoint escapes the candidate directory"
        )
    actual_candidate_hash = sha256_file(checkpoint_path)
    manifest_candidate_hash = str(latest["sha256"]).lower()
    expected_candidate_hash = expected_candidate_sha256.lower()
    if actual_candidate_hash != manifest_candidate_hash:
        raise CandidateSafetyError(
            "candidate checkpoint no longer matches its run manifest"
        )
    if actual_candidate_hash != expected_candidate_hash:
        raise CandidateSafetyError(
            "candidate checkpoint does not match the operator-supplied hash"
        )

    parent_path = (project_root / PARENT_RELATIVE_PATH).resolve()
    parent_hash = sha256_file(parent_path)
    if parent_hash != EXPECTED_PARENT_SHA256:
        raise CandidateSafetyError(
            "live parent changed before promotion; refusing atomic replacement"
        )

    frozen_dir = (project_root / "checkpoints" / "frozen").resolve()
    frozen_dir.mkdir(parents=True, exist_ok=True)
    preserved_parent = frozen_dir / f"pre_promotion_{parent_hash[:12]}.pt"
    if not preserved_parent.exists():
        shutil.copy2(parent_path, preserved_parent)
        if sha256_file(preserved_parent) != parent_hash:
            raise CandidateSafetyError(
                "failed to verify preserved pre-promotion parent"
            )

    staged_parent = parent_path.with_name(parent_path.name + ".promoting")
    shutil.copy2(checkpoint_path, staged_parent)
    if sha256_file(staged_parent) != actual_candidate_hash:
        raise CandidateSafetyError("staged promotion copy failed verification")
    os.replace(staged_parent, parent_path)

    manifest["promotion"] = {
        "permitted_as_training_side_effect": False,
        "performed": True,
        "performed_at_utc": utc_now(),
        "promoted_sha256": actual_candidate_hash,
        "parent_path": relative_display(parent_path, repo_root),
        "preserved_parent_path": relative_display(
            preserved_parent,
            repo_root,
        ),
    }
    atomic_write_json(manifest_path, manifest)
    return parent_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    promoted = promote_candidate(
        ROOT,
        args.candidate_id,
        args.expected_candidate_sha256,
    )
    print(f"Promoted candidate {args.candidate_id} to {promoted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
