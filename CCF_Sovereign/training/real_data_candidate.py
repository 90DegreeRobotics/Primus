"""Fail-closed lifecycle for isolated real-data state-transition candidates.

The existing ``CandidateRun`` is intentionally coupled to the Council text
parent and corpus.  This separate lifecycle is used only for the bounded
BridgeData one-step state-transition experiment.  It hash-protects the Council
parent and frozen archive without loading either as a model input, binds every
real-data artifact by SHA-256, writes only below a fresh candidate directory,
and provides no promotion operation.
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
from typing import Any, Mapping


PARENT_RELATIVE_PATH = Path("checkpoints") / "primus_council_trained.pt"
FROZEN_PARENT_RELATIVE_PATH = Path("checkpoints") / "frozen" / "parent_5e36cc9a_2026-08-26.pt"
CANDIDATE_ROOT_RELATIVE_PATH = Path("checkpoints") / "candidates"
RUN_MANIFEST_NAME = "real_data.run.manifest.json"
CANDIDATE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
FROZEN_INPUT_LABEL_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class RealDataCandidateSafetyError(RuntimeError):
    """Raised when a real-data candidate would violate an evidence boundary."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_display(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _git_output(repo_root: Path, arguments: list[str]) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    encoded = json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _atomic_torch_save(payload: Mapping[str, Any], path: Path) -> None:
    import torch

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    torch.save(dict(payload), temporary)
    os.replace(temporary, path)


def _valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _resolve_permitted_untracked(
    repo_root: Path,
    bindings: Mapping[str, tuple[str | Path, str]],
) -> dict[str, tuple[Path, str]]:
    """Resolve only hash-pinned untracked files inherited from another work lane."""

    resolved: dict[str, tuple[Path, str]] = {}
    for label, binding in sorted(bindings.items()):
        if not FROZEN_INPUT_LABEL_RE.fullmatch(label):
            raise RealDataCandidateSafetyError("permitted untracked label has an invalid format")
        if not isinstance(binding, tuple) or len(binding) != 2:
            raise RealDataCandidateSafetyError("permitted untracked file must be a (path, sha256) tuple")
        raw_path, expected_hash = binding
        path = Path(raw_path).expanduser().resolve()
        digest = str(expected_hash).lower()
        if not _is_relative_to(path, repo_root):
            raise RealDataCandidateSafetyError("permitted untracked file escapes the repository")
        if not path.is_file() or not _valid_sha256(digest) or sha256_file(path) != digest:
            raise RealDataCandidateSafetyError("permitted untracked file path or SHA-256 is invalid")
        resolved[label] = (path, digest)
    return resolved


def _assert_clean_or_permitted_untracked(
    repo_root: Path,
    permitted: Mapping[str, tuple[Path, str]],
) -> None:
    """Require no tracked edits and exactly the declared untracked paths."""

    status_lines = [
        line for line in _git_output(repo_root, ["status", "--porcelain", "--untracked-files=all"]).splitlines()
        if line
    ]
    permitted_relative = {
        _relative_display(path, repo_root).replace("/", "\\")
        for path, _ in permitted.values()
    }
    observed_untracked: set[str] = set()
    for line in status_lines:
        if not line.startswith("?? "):
            raise RealDataCandidateSafetyError("real-data candidate training requires no tracked repository changes")
        observed_untracked.add(line[3:].replace("/", "\\"))
    if observed_untracked != permitted_relative:
        raise RealDataCandidateSafetyError(
            "real-data candidate training requires a clean repository except exact hash-pinned inherited untracked files"
        )


@dataclass
class RealDataCandidateRun:
    """One isolated real-data candidate with immutable input and parent guards."""

    project_root: Path
    repo_root: Path
    candidate_id: str
    seed: int
    candidate_dir: Path
    manifest_path: Path
    parent_path: Path
    frozen_parent_path: Path
    expected_parent_sha256: str
    additional_frozen_inputs: dict[str, tuple[Path, str]]
    permitted_preexisting_untracked: dict[str, tuple[Path, str]]
    manifest: dict[str, Any]

    @classmethod
    def create(
        cls,
        project_root: str | Path,
        candidate_id: str,
        seed: int,
        *,
        expected_parent_sha256: str,
        additional_frozen_inputs: Mapping[str, tuple[str | Path, str]],
        permitted_preexisting_untracked: Mapping[str, tuple[str | Path, str]] | None = None,
        require_clean_repo: bool = True,
    ) -> "RealDataCandidateRun":
        project_root = Path(project_root).expanduser().resolve()
        repo_root = project_root.parent.resolve()
        if not CANDIDATE_ID_RE.fullmatch(candidate_id):
            raise RealDataCandidateSafetyError("candidate_id has an invalid format")
        if not _valid_sha256(expected_parent_sha256.lower()):
            raise RealDataCandidateSafetyError("expected_parent_sha256 must be a SHA-256 digest")
        candidate_root = (project_root / CANDIDATE_ROOT_RELATIVE_PATH).resolve()
        candidate_dir = (candidate_root / candidate_id).resolve()
        if not _is_relative_to(candidate_dir, candidate_root):
            raise RealDataCandidateSafetyError("candidate path escapes the candidate root")
        if candidate_dir.exists():
            raise RealDataCandidateSafetyError(f"candidate destination already exists: {candidate_dir}")
        resolved_permitted_untracked = _resolve_permitted_untracked(
            repo_root, permitted_preexisting_untracked or {}
        )
        if require_clean_repo:
            _assert_clean_or_permitted_untracked(repo_root, resolved_permitted_untracked)
        parent_path = (project_root / PARENT_RELATIVE_PATH).resolve()
        frozen_parent_path = (project_root / FROZEN_PARENT_RELATIVE_PATH).resolve()
        resolved_inputs: dict[str, tuple[Path, str]] = {}
        for label, binding in sorted(additional_frozen_inputs.items()):
            if not FROZEN_INPUT_LABEL_RE.fullmatch(label):
                raise RealDataCandidateSafetyError("frozen input label has an invalid format")
            if not isinstance(binding, tuple) or len(binding) != 2:
                raise RealDataCandidateSafetyError("frozen input must be a (path, sha256) tuple")
            raw_path, expected_hash = binding
            source = Path(raw_path).expanduser().resolve()
            digest = str(expected_hash).lower()
            if not source.is_file() or not _valid_sha256(digest):
                raise RealDataCandidateSafetyError("frozen input path or SHA-256 is invalid")
            resolved_inputs[label] = (source, digest)
        required_labels = {"intake_manifest", "data_parquet", "episodes_parquet", "tasks_parquet"}
        missing_labels = sorted(required_labels - set(resolved_inputs))
        if missing_labels:
            raise RealDataCandidateSafetyError(
                "real-data candidate lacks required frozen inputs: " + ", ".join(missing_labels)
            )
        run = cls(
            project_root=project_root,
            repo_root=repo_root,
            candidate_id=candidate_id,
            seed=int(seed),
            candidate_dir=candidate_dir,
            manifest_path=candidate_dir / RUN_MANIFEST_NAME,
            parent_path=parent_path,
            frozen_parent_path=frozen_parent_path,
            expected_parent_sha256=expected_parent_sha256.lower(),
            additional_frozen_inputs=resolved_inputs,
            permitted_preexisting_untracked=resolved_permitted_untracked,
            manifest={},
        )
        run.verify_frozen_inputs()
        candidate_dir.mkdir(parents=True, exist_ok=False)
        (candidate_dir / "checkpoints").mkdir()
        (candidate_dir / "evidence").mkdir()
        run.manifest = run._initial_manifest()
        run._save_manifest()
        return run

    def _file_evidence(self, path: Path) -> dict[str, Any]:
        return {
            "path": _relative_display(path, self.repo_root),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }

    def _initial_manifest(self) -> dict[str, Any]:
        return {
            "manifest_version": 1,
            "candidate_kind": "bridgedata_observed_state_transition",
            "candidate_id": self.candidate_id,
            "status": "prepared",
            "created_at_utc": utc_now(),
            "updated_at_utc": utc_now(),
            "seed": self.seed,
            "code_commit": _git_output(self.repo_root, ["rev-parse", "HEAD"]),
            "parent_protection": {
                "used_as_model_input": False,
                "touched_by_training": False,
                "live_parent": self._file_evidence(self.parent_path),
                "frozen_parent": self._file_evidence(self.frozen_parent_path),
            },
            "additional_frozen_inputs": {
                label: self._file_evidence(path)
                for label, (path, _) in sorted(self.additional_frozen_inputs.items())
            },
            "permitted_preexisting_untracked": {
                label: self._file_evidence(path)
                for label, (path, _) in sorted(self.permitted_preexisting_untracked.items())
            },
            "config": None,
            "training": None,
            "checkpoint": None,
            "evaluation": None,
            "promotion": {
                "permitted_as_training_side_effect": False,
                "performed": False,
                "interface_available": False,
            },
            "output_path": _relative_display(self.candidate_dir, self.repo_root),
        }

    def _save_manifest(self) -> None:
        self.manifest["updated_at_utc"] = utc_now()
        _atomic_json(self.manifest_path, self.manifest)

    def verify_frozen_inputs(self) -> None:
        required = (self.parent_path, self.frozen_parent_path)
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise RealDataCandidateSafetyError("protected parent input is missing: " + ", ".join(missing))
        for path in required:
            if sha256_file(path) != self.expected_parent_sha256:
                raise RealDataCandidateSafetyError("protected Council parent hash changed")
        for label, (path, expected_hash) in self.additional_frozen_inputs.items():
            if not path.is_file() or sha256_file(path) != expected_hash:
                raise RealDataCandidateSafetyError(f"frozen real-data input hash changed: {label}")
        for label, (path, expected_hash) in self.permitted_preexisting_untracked.items():
            if not path.is_file() or sha256_file(path) != expected_hash:
                raise RealDataCandidateSafetyError(
                    f"permitted preexisting untracked file hash changed: {label}"
                )
        _assert_clean_or_permitted_untracked(
            self.repo_root, self.permitted_preexisting_untracked
        )

    def assert_candidate_output(self, path: str | Path) -> Path:
        resolved = Path(path).expanduser().resolve()
        if resolved in {self.parent_path, self.frozen_parent_path}:
            raise RealDataCandidateSafetyError("real-data candidate may not write a protected parent path")
        if not _is_relative_to(resolved, self.candidate_dir):
            raise RealDataCandidateSafetyError("candidate output escapes the isolated run directory")
        return resolved

    def evidence_path(self, name: str) -> Path:
        if not name or Path(name).name != name:
            raise RealDataCandidateSafetyError("evidence name must be a single file name")
        return self.assert_candidate_output(self.candidate_dir / "evidence" / name)

    def checkpoint_path(self) -> Path:
        return self.assert_candidate_output(self.candidate_dir / "checkpoints" / "state_transition_mlp.pt")

    def mark_training_started(self, *, config: Mapping[str, Any], examples: int, epochs: int, batch_size: int, device: str) -> None:
        self.verify_frozen_inputs()
        if self.manifest.get("status") != "prepared":
            raise RealDataCandidateSafetyError("candidate is not in the prepared state")
        self.manifest["status"] = "training"
        self.manifest["config"] = deepcopy(dict(config))
        self.manifest["training"] = {
            "examples": int(examples),
            "epochs_requested": int(epochs),
            "batch_size": int(batch_size),
            "device": str(device),
            "started_at_utc": utc_now(),
        }
        self._save_manifest()

    def save_checkpoint(self, payload: Mapping[str, Any], *, metrics: Mapping[str, Any]) -> Path:
        self.verify_frozen_inputs()
        if self.manifest.get("status") != "training":
            raise RealDataCandidateSafetyError("candidate checkpoint requires an active training state")
        path = self.checkpoint_path()
        if path.exists():
            raise RealDataCandidateSafetyError("candidate checkpoint destination already exists")
        _atomic_torch_save(payload, path)
        self.verify_frozen_inputs()
        self.manifest["checkpoint"] = {
            **self._file_evidence(path),
            "metrics": deepcopy(dict(metrics)),
        }
        self.manifest["status"] = "checkpointed"
        self._save_manifest()
        return path

    def write_evidence_json(self, name: str, payload: Mapping[str, Any]) -> Path:
        path = self.evidence_path(name)
        if path.exists():
            raise RealDataCandidateSafetyError("candidate evidence destination already exists")
        _atomic_json(path, payload)
        return path

    def mark_evaluated(self, *, metrics_report: Path, predictions: Path) -> None:
        self.verify_frozen_inputs()
        if self.manifest.get("status") != "checkpointed":
            raise RealDataCandidateSafetyError("evaluation requires a checkpointed candidate")
        metrics_report = self.assert_candidate_output(metrics_report)
        predictions = self.assert_candidate_output(predictions)
        if not metrics_report.is_file() or not predictions.is_file():
            raise RealDataCandidateSafetyError("evaluation evidence files are missing")
        self.manifest["evaluation"] = {
            "metrics_report": self._file_evidence(metrics_report),
            "predictions": self._file_evidence(predictions),
            "evaluated_at_utc": utc_now(),
        }
        self.manifest["status"] = "evaluated"
        self._save_manifest()

    def mark_rejected(self, reason: str) -> None:
        self.verify_frozen_inputs()
        if self.manifest.get("status") != "evaluated":
            raise RealDataCandidateSafetyError("rejection requires an evaluated candidate")
        if not reason:
            raise RealDataCandidateSafetyError("rejection reason is required")
        self.manifest["status"] = "rejected"
        self.manifest["rejection"] = {"reason": reason, "recorded_at_utc": utc_now()}
        self._save_manifest()

    def mark_failed(self, error: BaseException) -> None:
        self.manifest["status"] = "failed"
        self.manifest["failure"] = {
            "type": type(error).__name__,
            "message": str(error),
            "recorded_at_utc": utc_now(),
        }
        self._save_manifest()
