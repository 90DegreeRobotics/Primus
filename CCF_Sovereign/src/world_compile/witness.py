"""Compiler witness for Primus typed world programs.

This module closes a specific, measured gap. The Stage 2 trajectory generator
declares every operation as ``capability_id="geometry_core_primitives"`` with
``capability_status=AVAILABLE``. Those are literals in the generator source; no
module under ``src/world_schema`` reads ``data/capability_ledger.json``. The
world-schema contract states the design law that the schema "does not turn an
unavailable ledger entry into an executable promise", but nothing enforced it.
This module performs the binding and records the result.

It also records a second measured fact. ``chronos.exe s3v validate`` accepts a
plan whose title envelope has been destroyed, and accepts an unknown ``version``
value. The Primus ``WorldProgram`` is carried inside that title envelope.
Compiler acceptance therefore does not imply Primus payload integrity, and this
module verifies the envelope round trip separately rather than inferring it
from a zero exit code.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from world_schema import from_s3v_json, to_s3v_json  # noqa: E402
from world_schema.model import WorldProgram  # noqa: E402

WITNESS_VERSION = "1.0.0"
REPORT_FILENAME = "compiler_witness.json"


class WitnessError(RuntimeError):
    """Raised when the witness cannot produce an honest receipt."""


class EvidenceLabel(str, Enum):
    """Charter §6 evidence vocabulary."""

    GENERATED = "generated"
    INFERRED = "inferred"
    OBSERVED = "observed"


class FailureClass(str, Enum):
    """Failure taxonomy.

    Every member here has been produced by a real execution. Do not add a
    member speculatively; a class that has never been observed is not evidence.
    """

    NONE = "none"
    MALFORMED_JSON = "malformed_json"
    SCHEMA_TYPE_ERROR = "schema_type_error"
    COMPILER_REJECTED = "compiler_rejected"
    ENVELOPE_CORRUPTED = "envelope_corrupted"
    CAPABILITY_UNBOUND = "capability_unbound"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    COMPILER_ABSENT = "compiler_absent"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize_capability_id(value: str) -> str:
    """Fold ``geometry.core_primitives`` and ``geometry_core_primitives``.

    Normalization is reported, never silent. An identifier that matches only
    after normalization is a weaker binding than an exact match and the receipt
    says so.
    """
    return re.sub(r"[^a-z0-9]+", ".", value.strip().lower()).strip(".")


@dataclass(frozen=True)
class CapabilityLedger:
    """Read-only view of the ChronoSophia capability ledger."""

    entries: tuple[dict[str, Any], ...]
    source_path: str
    source_sha256: str

    @classmethod
    def load(cls, path: str | Path) -> "CapabilityLedger":
        p = Path(path)
        if not p.is_file():
            raise WitnessError(f"capability ledger not found: {p}")
        raw = p.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, list):
            raise WitnessError("capability ledger must be a JSON list")
        return cls(
            entries=tuple(data),
            source_path=str(p),
            source_sha256=_sha256_text(raw),
        )

    def lookup(self, capability_id: str) -> tuple[dict[str, Any] | None, bool]:
        """Return ``(entry, exact)``.

        ``exact`` is True only when the declared identifier matched a ledger
        ``id`` verbatim.
        """
        for entry in self.entries:
            if entry.get("id") == capability_id:
                return entry, True
        target = _normalize_capability_id(capability_id)
        for entry in self.entries:
            if _normalize_capability_id(str(entry.get("id", ""))) == target:
                return entry, False
        return None, False

    def available_ids(self) -> tuple[str, ...]:
        return tuple(
            str(e.get("id"))
            for e in self.entries
            if e.get("status") == "available"
        )


@dataclass(frozen=True)
class CapabilityBinding:
    """One operation's declared capability, checked against the ledger."""

    operation_id: str
    declared_id: str
    declared_status: str
    ledger_id: str | None
    ledger_status: str | None
    exact_match: bool
    failure: FailureClass

    @property
    def bound(self) -> bool:
        return self.ledger_id is not None

    @property
    def executable(self) -> bool:
        return self.bound and self.ledger_status == "available"

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "declared_id": self.declared_id,
            "declared_status": self.declared_status,
            "ledger_id": self.ledger_id,
            "ledger_status": self.ledger_status,
            "exact_match": self.exact_match,
            "bound": self.bound,
            "executable": self.executable,
            "failure": self.failure.value,
        }


def bind_capabilities(
    program: WorldProgram, ledger: CapabilityLedger
) -> tuple[CapabilityBinding, ...]:
    """Bind every declared capability to the ledger.

    A declared status of ``available`` is not trusted. The ledger decides.
    """
    bindings: list[CapabilityBinding] = []
    for operation in program.operations:
        declared_id = getattr(operation, "capability_id", None)
        if not declared_id:
            continue
        status_obj = getattr(operation, "capability_status", None)
        declared_status = getattr(status_obj, "value", None) or str(status_obj)
        entry, exact = ledger.lookup(declared_id)
        if entry is None:
            failure = FailureClass.CAPABILITY_UNBOUND
            ledger_id = None
            ledger_status = None
        else:
            ledger_id = str(entry.get("id"))
            ledger_status = str(entry.get("status"))
            failure = (
                FailureClass.NONE
                if ledger_status == "available"
                else FailureClass.CAPABILITY_UNAVAILABLE
            )
        bindings.append(
            CapabilityBinding(
                operation_id=str(getattr(operation, "operation_id", "")),
                declared_id=str(declared_id),
                declared_status=str(declared_status),
                ledger_id=ledger_id,
                ledger_status=ledger_status,
                exact_match=exact,
                failure=failure,
            )
        )
    return tuple(bindings)


@dataclass(frozen=True)
class CompilerReceipt:
    """Hash-bound record of one real compiler invocation."""

    program_id: str
    program_sha256: str
    s3v_sha256: str
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    envelope_round_trip_ok: bool
    failure: FailureClass
    evidence_label: EvidenceLabel
    capability_bindings: tuple[CapabilityBinding, ...] = field(default=())

    @property
    def compiler_accepted(self) -> bool:
        return self.exit_code == 0

    @property
    def witnessed(self) -> bool:
        """True only when compiler acceptance AND envelope integrity hold."""
        return self.compiler_accepted and self.envelope_round_trip_ok

    def to_dict(self) -> dict[str, Any]:
        return {
            "program_id": self.program_id,
            "program_sha256": self.program_sha256,
            "s3v_sha256": self.s3v_sha256,
            "command": list(self.command),
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "compiler_accepted": self.compiler_accepted,
            "envelope_round_trip_ok": self.envelope_round_trip_ok,
            "witnessed": self.witnessed,
            "failure": self.failure.value,
            "evidence_label": self.evidence_label.value,
            "capability_bindings": [b.to_dict() for b in self.capability_bindings],
        }


def _classify_failure(exit_code: int, stderr: str) -> FailureClass:
    if exit_code == 0:
        return FailureClass.NONE
    blob = stderr.lower()
    if "key must be a string" in blob or "expected value" in blob:
        return FailureClass.MALFORMED_JSON
    if "invalid type" in blob or "missing field" in blob:
        return FailureClass.SCHEMA_TYPE_ERROR
    return FailureClass.COMPILER_REJECTED


def compile_program(
    program: WorldProgram,
    *,
    compiler_exe: str | Path,
    workdir: str | Path,
    ledger: CapabilityLedger | None = None,
    timeout_seconds: int = 120,
) -> CompilerReceipt:
    """Lower one program to S³V, run the real compiler, and hash the result.

    The receipt is labelled ``observed`` only because ``compiler_exe`` actually
    ran. If the binary is absent, the receipt is labelled ``generated`` and the
    failure class records why — it is never labelled ``observed`` on the
    strength of code that did not execute.
    """
    exe = Path(compiler_exe)
    work = Path(workdir)
    work.mkdir(parents=True, exist_ok=True)

    s3v_text = to_s3v_json(program)
    s3v_sha = _sha256_text(s3v_text)
    program_id = str(getattr(program, "program_id", "")) or "unknown"
    artifact = work / f"{program_id}.s3v.json"
    artifact.write_text(s3v_text, encoding="utf-8")

    # Envelope integrity is checked independently of the compiler, because the
    # compiler demonstrably accepts a destroyed envelope.
    try:
        restored = from_s3v_json(s3v_text)
        envelope_ok = restored == program
    except Exception:
        envelope_ok = False

    bindings = bind_capabilities(program, ledger) if ledger is not None else ()

    if not exe.is_file():
        return CompilerReceipt(
            program_id=program_id,
            program_sha256=program.sha256(),
            s3v_sha256=s3v_sha,
            command=(str(exe), "s3v", "validate", str(artifact)),
            exit_code=-1,
            stdout="",
            stderr=f"compiler binary not found: {exe}",
            envelope_round_trip_ok=envelope_ok,
            failure=FailureClass.COMPILER_ABSENT,
            evidence_label=EvidenceLabel.GENERATED,
            capability_bindings=bindings,
        )

    command = (str(exe), "s3v", "validate", str(artifact))
    proc = subprocess.run(  # noqa: S603
        command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    failure = _classify_failure(proc.returncode, proc.stderr)
    if failure is FailureClass.NONE and not envelope_ok:
        failure = FailureClass.ENVELOPE_CORRUPTED

    return CompilerReceipt(
        program_id=program_id,
        program_sha256=program.sha256(),
        s3v_sha256=s3v_sha,
        command=command,
        exit_code=proc.returncode,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
        envelope_round_trip_ok=envelope_ok,
        failure=failure,
        evidence_label=EvidenceLabel.OBSERVED,
        capability_bindings=bindings,
    )


@dataclass(frozen=True)
class WitnessReport:
    """Aggregate witness over a dataset."""

    receipts: tuple[CompilerReceipt, ...]
    ledger_path: str
    ledger_sha256: str
    compiler_exe: str
    compiler_present: bool
    render_witness_attempted: bool = False
    render_witness_note: str = (
        "Not attempted. A render witness requires the full ChronoSophia render "
        "stack (local model plus Blender) and writes into the product output "
        "tree, which is outside the Lane A read-only boundary and requires "
        "per-item operator approval. No render hash is claimed and nothing "
        "here is labelled observed on the basis of rendering."
    )

    @property
    def witnessed_count(self) -> int:
        return sum(1 for r in self.receipts if r.witnessed)

    @property
    def executable_count(self) -> int:
        return sum(
            1
            for r in self.receipts
            if r.capability_bindings
            and all(b.executable for b in r.capability_bindings)
        )

    def failure_histogram(self) -> dict[str, int]:
        hist: dict[str, int] = {}
        for r in self.receipts:
            hist[r.failure.value] = hist.get(r.failure.value, 0) + 1
        return dict(sorted(hist.items()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "witness_version": WITNESS_VERSION,
            "compiler_exe": self.compiler_exe,
            "compiler_present": self.compiler_present,
            "ledger_path": self.ledger_path,
            "ledger_sha256": self.ledger_sha256,
            "program_count": len(self.receipts),
            "witnessed_count": self.witnessed_count,
            "capability_executable_count": self.executable_count,
            "failure_histogram": self.failure_histogram(),
            "render_witness_attempted": self.render_witness_attempted,
            "render_witness_note": self.render_witness_note,
            "claims": {
                "compiler_execution_observed": self.compiler_present,
                "render_observed": False,
                "visual_correctness_proven": False,
                "learned_world_dynamics_proven": False,
                "model_training_started": False,
                "candidate_promoted": False,
            },
            "receipts": [r.to_dict() for r in self.receipts],
        }


def witness_dataset(
    programs: Iterable[WorldProgram],
    *,
    compiler_exe: str | Path,
    ledger_path: str | Path,
    workdir: str | Path,
) -> WitnessReport:
    """Witness every program in a dataset against the real compiler."""
    ledger = CapabilityLedger.load(ledger_path)
    exe = Path(compiler_exe)
    receipts = tuple(
        compile_program(
            p, compiler_exe=exe, workdir=workdir, ledger=ledger
        )
        for p in programs
    )
    return WitnessReport(
        receipts=receipts,
        ledger_path=ledger.source_path,
        ledger_sha256=ledger.source_sha256,
        compiler_exe=str(exe),
        compiler_present=exe.is_file(),
    )


def write_witness_report(report: WitnessReport, destination: str | Path) -> Path:
    """Write the report atomically to a new directory.

    Refuses an existing destination, matching the Stage 2 writer contract.
    """
    dest = Path(destination)
    if dest.exists():
        raise WitnessError(f"destination already exists, refusing: {dest}")
    staging = dest.parent / f".{dest.name}.staging"
    if staging.exists():
        raise WitnessError(f"staging path already exists, refusing: {staging}")
    staging.mkdir(parents=True)
    payload = json.dumps(report.to_dict(), indent=2, sort_keys=True)
    (staging / REPORT_FILENAME).write_text(payload, encoding="utf-8")
    staging.rename(dest)
    return dest / REPORT_FILENAME


def load_programs(jsonl_path: str | Path) -> tuple[WorldProgram, ...]:
    """Load canonical world programs from Stage 2 JSONL."""
    path = Path(jsonl_path)
    if not path.is_file():
        raise WitnessError(f"dataset not found: {path}")
    programs: list[WorldProgram] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            programs.append(WorldProgram.from_dict(json.loads(line)))
    if not programs:
        raise WitnessError(f"dataset is empty: {path}")
    return tuple(programs)


__all__ = [
    "CapabilityBinding",
    "CapabilityLedger",
    "CompilerReceipt",
    "EvidenceLabel",
    "FailureClass",
    "WitnessError",
    "WitnessReport",
    "bind_capabilities",
    "compile_program",
    "load_programs",
    "witness_dataset",
    "write_witness_report",
]
