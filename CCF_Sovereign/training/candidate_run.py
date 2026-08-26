"""Fail-closed candidate training paths and evidence manifests.

Training code may write only beneath ``checkpoints/candidates/<candidate_id>``.
The frozen parent is read for integrity verification and is never a training
output. Promotion is implemented separately in ``promote_candidate.py``.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


EXPECTED_PARENT_SHA256 = (
    "5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b"
)
EXPECTED_CORPUS_MANIFEST_SHA256 = (
    "8bfe4837c1c65e801396a21ddf133d8eddcd424b71a6feadfb5419b0712874fa"
)
PARENT_RELATIVE_PATH = Path("checkpoints") / "primus_council_trained.pt"
FROZEN_PARENT_RELATIVE_PATH = (
    Path("checkpoints") / "frozen" / "parent_5e36cc9a_2026-08-26.pt"
)
CORPUS_MANIFEST_RELATIVE_PATH = (
    Path("training") / "training_data" / "council_turns.manifest.json"
)
TRAINING_DATA_RELATIVE_PATH = (
    Path("training") / "training_data" / "council_turns.jsonl"
)
CANDIDATE_ROOT_RELATIVE_PATH = Path("checkpoints") / "candidates"
RUN_MANIFEST_NAME = "run.manifest.json"
CANDIDATE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class CandidateSafetyError(RuntimeError):
    """Raised when a candidate run would violate an integrity boundary."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_display(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def git_commit(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status(repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(path.name + ".tmp")
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        indent=2,
        sort_keys=True,
    ) + "\n"
    with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)


def atomic_torch_save(payload: dict[str, Any], path: Path) -> None:
    import torch

    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(path.name + ".tmp")
    torch.save(payload, temp_path)
    os.replace(temp_path, path)


def _validate_candidate_id(candidate_id: str) -> str:
    if not CANDIDATE_ID_RE.fullmatch(candidate_id):
        raise CandidateSafetyError(
            "candidate_id must match ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
        )
    return candidate_id


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


@dataclass
class CandidateRun:
    project_root: Path
    candidate_id: str
    seed: int
    expected_parent_sha256: str
    expected_corpus_manifest_sha256: str
    candidate_dir: Path
    manifest_path: Path
    parent_path: Path
    frozen_parent_path: Path
    corpus_manifest_path: Path
    training_data_path: Path
    repo_root: Path
    manifest: dict[str, Any]

    @classmethod
    def create(
        cls,
        project_root: Path,
        candidate_id: str,
        seed: int,
        *,
        expected_parent_sha256: str = EXPECTED_PARENT_SHA256,
        expected_corpus_manifest_sha256: str = EXPECTED_CORPUS_MANIFEST_SHA256,
        require_clean_repo: bool = True,
    ) -> "CandidateRun":
        project_root = project_root.resolve()
        repo_root = project_root.parent.resolve()
        candidate_id = _validate_candidate_id(candidate_id)
        candidate_root = (project_root / CANDIDATE_ROOT_RELATIVE_PATH).resolve()
        candidate_dir = (candidate_root / candidate_id).resolve()

        if not _is_relative_to(candidate_dir, candidate_root):
            raise CandidateSafetyError("candidate path escapes the candidate root")
        if candidate_dir.exists():
            raise CandidateSafetyError(
                f"candidate destination already exists: {candidate_dir}"
            )
        if require_clean_repo:
            status = git_status(repo_root)
            if status:
                raise CandidateSafetyError(
                    "candidate training requires a clean repository; "
                    f"git status is:\n{status}"
                )

        parent_path = (project_root / PARENT_RELATIVE_PATH).resolve()
        frozen_parent_path = (
            project_root / FROZEN_PARENT_RELATIVE_PATH
        ).resolve()
        corpus_manifest_path = (
            project_root / CORPUS_MANIFEST_RELATIVE_PATH
        ).resolve()
        training_data_path = (
            project_root / TRAINING_DATA_RELATIVE_PATH
        ).resolve()

        run = cls(
            project_root=project_root,
            candidate_id=candidate_id,
            seed=int(seed),
            expected_parent_sha256=expected_parent_sha256.lower(),
            expected_corpus_manifest_sha256=(
                expected_corpus_manifest_sha256.lower()
            ),
            candidate_dir=candidate_dir,
            manifest_path=candidate_dir / RUN_MANIFEST_NAME,
            parent_path=parent_path,
            frozen_parent_path=frozen_parent_path,
            corpus_manifest_path=corpus_manifest_path,
            training_data_path=training_data_path,
            repo_root=repo_root,
            manifest={},
        )
        run.verify_frozen_inputs()

        candidate_dir.mkdir(parents=True, exist_ok=False)
        (candidate_dir / "checkpoints").mkdir()
        run.manifest = run._initial_manifest()
        run._save_manifest()
        return run

    def _file_evidence(self, path: Path) -> dict[str, Any]:
        return {
            "path": relative_display(path, self.repo_root),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }

    def _initial_manifest(self) -> dict[str, Any]:
        return {
            "manifest_version": 1,
            "candidate_id": self.candidate_id,
            "status": "prepared",
            "created_at_utc": utc_now(),
            "updated_at_utc": utc_now(),
            "seed": self.seed,
            "code_commit": git_commit(self.repo_root),
            "parent": self._file_evidence(self.parent_path),
            "frozen_parent": self._file_evidence(self.frozen_parent_path),
            "corpus_manifest": self._file_evidence(
                self.corpus_manifest_path
            ),
            "training_data": self._file_evidence(self.training_data_path),
            "config": None,
            "training": None,
            "metrics": [],
            "latest_checkpoint": None,
            "output_path": relative_display(
                self.candidate_dir, self.repo_root
            ),
            "promotion": {
                "permitted_as_training_side_effect": False,
                "performed": False,
            },
        }

    def _save_manifest(self) -> None:
        self.manifest["updated_at_utc"] = utc_now()
        atomic_write_json(self.manifest_path, self.manifest)

    def verify_frozen_inputs(self) -> None:
        required = (
            self.parent_path,
            self.frozen_parent_path,
            self.corpus_manifest_path,
            self.training_data_path,
        )
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise CandidateSafetyError(
                "required frozen input is missing: " + ", ".join(missing)
            )

        parent_hash = sha256_file(self.parent_path)
        archive_hash = sha256_file(self.frozen_parent_path)
        manifest_hash = sha256_file(self.corpus_manifest_path)
        if parent_hash != self.expected_parent_sha256:
            raise CandidateSafetyError(
                "live parent hash changed: "
                f"expected {self.expected_parent_sha256}, got {parent_hash}"
            )
        if archive_hash != self.expected_parent_sha256:
            raise CandidateSafetyError(
                "frozen parent archive hash changed: "
                f"expected {self.expected_parent_sha256}, got {archive_hash}"
            )
        if manifest_hash != self.expected_corpus_manifest_sha256:
            raise CandidateSafetyError(
                "corpus manifest hash changed: "
                f"expected {self.expected_corpus_manifest_sha256}, "
                f"got {manifest_hash}"
            )

    def assert_candidate_output(self, path: Path) -> Path:
        resolved = path.resolve()
        if resolved == self.parent_path or resolved == self.frozen_parent_path:
            raise CandidateSafetyError(
                "candidate training may not write a parent checkpoint path"
            )
        if not _is_relative_to(resolved, self.candidate_dir):
            raise CandidateSafetyError(
                f"candidate output escapes isolated run directory: {resolved}"
            )
        return resolved

    def checkpoint_path(self, epoch: int) -> Path:
        if epoch <= 0:
            raise CandidateSafetyError("checkpoint epoch must be positive")
        return self.assert_candidate_output(
            self.candidate_dir
            / "checkpoints"
            / f"candidate_epoch_{epoch:04d}.pt"
        )

    def mark_training_started(
        self,
        *,
        config: dict[str, Any],
        turns: int,
        epochs: int,
        batch_size: int,
        max_sequence_length: int,
        device: str,
    ) -> None:
        self.verify_frozen_inputs()
        self.manifest["status"] = "training"
        self.manifest["config"] = deepcopy(config)
        self.manifest["training"] = {
            "turns": int(turns),
            "epochs_requested": int(epochs),
            "batch_size": int(batch_size),
            "max_sequence_length": int(max_sequence_length),
            "device": device,
            "started_at_utc": utc_now(),
        }
        self._save_manifest()

    def save_checkpoint(
        self,
        payload: dict[str, Any],
        *,
        epoch: int,
        metrics: dict[str, Any],
    ) -> Path:
        self.verify_frozen_inputs()
        path = self.checkpoint_path(epoch)
        if path.exists():
            raise CandidateSafetyError(
                f"candidate checkpoint already exists: {path}"
            )
        atomic_torch_save(payload, path)
        checkpoint = self._file_evidence(path)
        checkpoint["epoch"] = int(epoch)
        self.manifest["latest_checkpoint"] = checkpoint
        metric_record = deepcopy(metrics)
        metric_record["epoch"] = int(epoch)
        self.manifest["metrics"].append(metric_record)
        self.manifest["status"] = "checkpointed"
        self._save_manifest()
        return path

    def mark_completed(self) -> None:
        self.verify_frozen_inputs()
        if not self.manifest.get("latest_checkpoint"):
            raise CandidateSafetyError(
                "cannot complete a candidate run without a checkpoint"
            )
        self.manifest["status"] = "completed"
        self.manifest["completed_at_utc"] = utc_now()
        self._save_manifest()

    def mark_failed(self, error: BaseException) -> None:
        self.manifest["status"] = "failed"
        self.manifest["failure"] = {
            "type": type(error).__name__,
            "message": str(error),
            "recorded_at_utc": utc_now(),
        }
        self._save_manifest()
