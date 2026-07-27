"""
Shadow-cycle manifest primitives for auditable CCF hardening.

The manifest records what parent/candidate artifacts, training inputs, and
benchmark cases belong to a shadow run. It does not train or promote a model.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


MANIFEST_VERSION = 1


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_manifest_path(path: Path) -> str:
    """Normalize paths for cross-machine manifest comparison."""
    return path.as_posix()


@dataclass(frozen=True)
class FileEvidence:
    path: str
    sha256: str
    bytes: int

    @classmethod
    def from_path(cls, path: Path, root: Optional[Path] = None) -> "FileEvidence":
        resolved = path.resolve()
        display_path = resolved
        if root is not None:
            try:
                display_path = resolved.relative_to(root.resolve())
            except ValueError:
                display_path = resolved
        return cls(
            path=normalize_manifest_path(display_path),
            sha256=sha256_file(resolved),
            bytes=resolved.stat().st_size,
        )

    @classmethod
    def from_dict(cls, raw: dict) -> "FileEvidence":
        return cls(
            path=str(raw["path"]),
            sha256=str(raw["sha256"]),
            bytes=int(raw["bytes"]),
        )

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "bytes": self.bytes,
        }


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    prompt: str
    expected_contains: tuple[str, ...] = field(default_factory=tuple)
    protected: bool = True
    tags: tuple[str, ...] = field(default_factory=tuple)
    source_path: Optional[str] = None

    @classmethod
    def from_dict(cls, raw: dict) -> "BenchmarkCase":
        return cls(
            case_id=str(raw["case_id"]),
            prompt=str(raw["prompt"]),
            expected_contains=tuple(raw.get("expected_contains", [])),
            protected=bool(raw.get("protected", True)),
            tags=tuple(raw.get("tags", [])),
            source_path=raw.get("source_path"),
        )

    def prompt_sha256(self) -> str:
        return hashlib.sha256(self.prompt.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "prompt": self.prompt,
            "prompt_sha256": self.prompt_sha256(),
            "expected_contains": list(self.expected_contains),
            "protected": self.protected,
            "tags": list(self.tags),
            "source_path": self.source_path,
        }


@dataclass(frozen=True)
class ShadowCycleManifest:
    cycle_id: str
    parent: FileEvidence
    training_inputs: tuple[FileEvidence, ...]
    benchmark_cases: tuple[BenchmarkCase, ...]
    candidate: Optional[FileEvidence] = None
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
    )
    manifest_version: int = MANIFEST_VERSION
    notes: str = ""

    @classmethod
    def from_dict(cls, raw: dict) -> "ShadowCycleManifest":
        candidate = raw.get("candidate")
        return cls(
            cycle_id=str(raw["cycle_id"]),
            parent=FileEvidence.from_dict(raw["parent"]),
            candidate=FileEvidence.from_dict(candidate) if candidate else None,
            training_inputs=tuple(
                FileEvidence.from_dict(item)
                for item in raw.get("training_inputs", [])
            ),
            benchmark_cases=tuple(
                BenchmarkCase.from_dict(item)
                for item in raw.get("benchmark_cases", [])
            ),
            created_at_utc=str(raw["created_at_utc"]),
            manifest_version=int(raw.get("manifest_version", MANIFEST_VERSION)),
            notes=str(raw.get("notes", "")),
        )

    def to_dict(self) -> dict:
        return {
            "manifest_version": self.manifest_version,
            "cycle_id": self.cycle_id,
            "created_at_utc": self.created_at_utc,
            "parent": self.parent.to_dict(),
            "candidate": self.candidate.to_dict() if self.candidate else None,
            "training_inputs": [
                evidence.to_dict() for evidence in self.training_inputs
            ],
            "benchmark_cases": [
                case.to_dict() for case in self.benchmark_cases
            ],
            "leakage_warnings": self.leakage_warnings(),
            "notes": self.notes,
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )

    def manifest_sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def leakage_warnings(self) -> list[str]:
        training_paths = {
            evidence.path.lower().replace("\\", "/")
            for evidence in self.training_inputs
        }
        warnings = []
        for case in self.benchmark_cases:
            if not case.source_path:
                continue
            source = case.source_path.lower().replace("\\", "/")
            if source in training_paths:
                warnings.append(
                    f"benchmark case {case.case_id} uses training source {case.source_path}"
                )
        return warnings

    def validate(self) -> None:
        if self.manifest_version != MANIFEST_VERSION:
            raise ValueError(f"unsupported manifest version: {self.manifest_version}")
        if not self.cycle_id:
            raise ValueError("cycle_id is required")
        if not self.benchmark_cases:
            raise ValueError("at least one benchmark case is required")

        case_ids = [case.case_id for case in self.benchmark_cases]
        duplicate_ids = sorted(
            {case_id for case_id in case_ids if case_ids.count(case_id) > 1}
        )
        if duplicate_ids:
            raise ValueError(f"duplicate benchmark case IDs: {', '.join(duplicate_ids)}")

        leakage = self.leakage_warnings()
        if leakage:
            raise ValueError("; ".join(leakage))

    def save(self, path: Path) -> Path:
        self.validate()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.canonical_json() + "\n", encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "ShadowCycleManifest":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


def create_shadow_cycle_manifest(
    cycle_id: str,
    parent_checkpoint: Path,
    training_inputs: Iterable[Path],
    benchmark_cases: Iterable[BenchmarkCase],
    candidate_checkpoint: Optional[Path] = None,
    root: Optional[Path] = None,
    notes: str = "",
) -> ShadowCycleManifest:
    """Build a manifest from artifact paths and benchmark cases."""
    manifest = ShadowCycleManifest(
        cycle_id=cycle_id,
        parent=FileEvidence.from_path(parent_checkpoint, root=root),
        candidate=(
            FileEvidence.from_path(candidate_checkpoint, root=root)
            if candidate_checkpoint
            else None
        ),
        training_inputs=tuple(
            FileEvidence.from_path(path, root=root)
            for path in training_inputs
        ),
        benchmark_cases=tuple(benchmark_cases),
        notes=notes,
    )
    manifest.validate()
    return manifest
