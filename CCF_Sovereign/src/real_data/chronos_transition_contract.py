"""Schema-only Primus-to-Chronos transition evidence contract.

This module does not map BridgeData's 7D state/action vectors into Chronos scene
coordinates. It preserves that semantic gap explicitly. A schema-valid artifact
is offline observational prediction evidence, not an executable program,
renderer input, robot command, policy, control signal, or promotion artifact.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Mapping, Sequence


CHRONOS_TRANSITION_CONTRACT_VERSION = 1
STATE_DIMENSION = 7
ARTIFACT_SCOPE = "offline_observational_prediction_evidence"
STATE_COORDINATE_SEMANTICS = "unknown_not_a_chronos_scene_transform"
REQUIRED_LIMITATIONS = (
    "No verified mapping exists from these 7D robot-state vectors to Chronos scene coordinates, entities, geometry, materials, cameras, or renderer primitives.",
    "This artifact is not an executable program, policy, control signal, actuation command, manufacturing instruction, or safety-certified output.",
    "This artifact is not native Chronos integration evidence and cannot by itself authorize Chronos execution, rendering, product use, or candidate promotion.",
)
ALLOWED_KEYS = frozenset({
    "contract_version", "artifact_scope", "state_dimension", "state_coordinate_semantics",
    "control_permitted", "promotion_performed", "chronos_consumer_status", "limitations",
    "provenance", "rollout", "payload_sha256",
})


class ChronosTransitionContractError(ValueError):
    """Raised when a transition-evidence artifact violates its fail-closed boundary."""


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _sha256_json(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _finite_vector(value: Sequence[float], name: str) -> tuple[float, ...]:
    if isinstance(value, (str, bytes)):
        raise ChronosTransitionContractError(f"{name} must be a numeric sequence")
    try:
        vector = tuple(float(item) for item in value)
    except (TypeError, ValueError) as error:
        raise ChronosTransitionContractError(f"{name} must be a numeric sequence") from error
    if len(vector) != STATE_DIMENSION:
        raise ChronosTransitionContractError(f"{name} must have exactly {STATE_DIMENSION} dimensions")
    if not all(math.isfinite(item) for item in vector):
        raise ChronosTransitionContractError(f"{name} must contain finite numbers")
    return vector


def _sha256(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ChronosTransitionContractError(f"{name} must be a SHA-256 hexadecimal string")
    try:
        int(value, 16)
    except ValueError as error:
        raise ChronosTransitionContractError(f"{name} must be a SHA-256 hexadecimal string") from error
    return value.lower()


def _nonempty_string(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ChronosTransitionContractError(f"{name} must be a nonempty string")
    return value


@dataclass(frozen=True)
class ChronosTransitionEvidence:
    """Canonical numeric evidence handoff with an explicit no-scene/no-control boundary."""

    candidate_id: str
    candidate_checkpoint_sha256: str
    candidate_manifest_sha256: str
    protected_parent_sha256: str
    intake_manifest_sha256: str
    source_evidence_sha256: str
    source_evidence_payload_sha256: str
    source_evidence_path: str
    rollout_case_id: str
    episode_index: int
    task_index: int
    horizon: int
    observed_initial_state: tuple[float, ...]
    observed_action_sequence: tuple[tuple[float, ...], ...]
    predicted_state_sequence: tuple[tuple[float, ...], ...]

    def validate(self) -> None:
        _nonempty_string(self.candidate_id, "candidate_id")
        for name, value in (
            ("candidate_checkpoint_sha256", self.candidate_checkpoint_sha256),
            ("candidate_manifest_sha256", self.candidate_manifest_sha256),
            ("protected_parent_sha256", self.protected_parent_sha256),
            ("intake_manifest_sha256", self.intake_manifest_sha256),
            ("source_evidence_sha256", self.source_evidence_sha256),
            ("source_evidence_payload_sha256", self.source_evidence_payload_sha256),
        ):
            _sha256(value, name)
        _nonempty_string(self.source_evidence_path, "source_evidence_path")
        _nonempty_string(self.rollout_case_id, "rollout_case_id")
        if self.episode_index < 0 or self.task_index < 0:
            raise ChronosTransitionContractError("episode_index and task_index must be non-negative")
        if isinstance(self.horizon, bool) or not isinstance(self.horizon, int) or self.horizon < 1:
            raise ChronosTransitionContractError("horizon must be a positive integer")
        _finite_vector(self.observed_initial_state, "observed_initial_state")
        if len(self.observed_action_sequence) != self.horizon:
            raise ChronosTransitionContractError("observed action count must equal horizon")
        if len(self.predicted_state_sequence) != self.horizon:
            raise ChronosTransitionContractError("predicted state count must equal horizon")
        for index, action in enumerate(self.observed_action_sequence):
            _finite_vector(action, f"observed_action_sequence[{index}]")
        for index, state in enumerate(self.predicted_state_sequence):
            _finite_vector(state, f"predicted_state_sequence[{index}]")

    def _without_digest(self) -> dict[str, Any]:
        self.validate()
        return {
            "contract_version": CHRONOS_TRANSITION_CONTRACT_VERSION,
            "artifact_scope": ARTIFACT_SCOPE,
            "state_dimension": STATE_DIMENSION,
            "state_coordinate_semantics": STATE_COORDINATE_SEMANTICS,
            "control_permitted": False,
            "promotion_performed": False,
            "chronos_consumer_status": "schema_only_coordinate_adapter_required",
            "limitations": list(REQUIRED_LIMITATIONS),
            "provenance": {
                "candidate_id": self.candidate_id,
                "candidate_checkpoint_sha256": self.candidate_checkpoint_sha256.lower(),
                "candidate_manifest_sha256": self.candidate_manifest_sha256.lower(),
                "protected_parent_sha256": self.protected_parent_sha256.lower(),
                "intake_manifest_sha256": self.intake_manifest_sha256.lower(),
                "source_evidence_path": self.source_evidence_path,
                "source_evidence_sha256": self.source_evidence_sha256.lower(),
                "source_evidence_payload_sha256": self.source_evidence_payload_sha256.lower(),
            },
            "rollout": {
                "rollout_case_id": self.rollout_case_id,
                "episode_index": self.episode_index,
                "task_index": self.task_index,
                "horizon": self.horizon,
                "observed_initial_state": list(self.observed_initial_state),
                "observed_action_sequence": [list(item) for item in self.observed_action_sequence],
                "predicted_state_sequence": [list(item) for item in self.predicted_state_sequence],
            },
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._without_digest()
        payload["payload_sha256"] = _sha256_json(payload)
        return payload

    def payload_sha256(self) -> str:
        return str(self.to_dict()["payload_sha256"])

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ChronosTransitionEvidence":
        if not isinstance(payload, Mapping):
            raise ChronosTransitionContractError("contract payload must be an object")
        unknown = set(payload) - ALLOWED_KEYS
        missing = ALLOWED_KEYS - set(payload)
        if unknown:
            raise ChronosTransitionContractError("contract payload has unknown fields: " + ", ".join(sorted(unknown)))
        if missing:
            raise ChronosTransitionContractError("contract payload is missing fields: " + ", ".join(sorted(missing)))
        if payload["contract_version"] != CHRONOS_TRANSITION_CONTRACT_VERSION:
            raise ChronosTransitionContractError("unsupported contract version")
        if payload["artifact_scope"] != ARTIFACT_SCOPE:
            raise ChronosTransitionContractError("artifact scope is not offline observational prediction evidence")
        if payload["state_dimension"] != STATE_DIMENSION:
            raise ChronosTransitionContractError("state dimension is not the required 7D contract")
        if payload["state_coordinate_semantics"] != STATE_COORDINATE_SEMANTICS:
            raise ChronosTransitionContractError("state coordinate semantics must remain explicitly unknown")
        if payload["control_permitted"] is not False or payload["promotion_performed"] is not False:
            raise ChronosTransitionContractError("contract cannot permit control or promotion")
        if payload["chronos_consumer_status"] != "schema_only_coordinate_adapter_required":
            raise ChronosTransitionContractError("contract consumer status is invalid")
        if tuple(payload["limitations"]) != REQUIRED_LIMITATIONS:
            raise ChronosTransitionContractError("contract limitations must be exact and complete")
        provenance = payload["provenance"]
        rollout = payload["rollout"]
        if not isinstance(provenance, Mapping) or not isinstance(rollout, Mapping):
            raise ChronosTransitionContractError("provenance and rollout must be objects")
        expected_provenance = {
            "candidate_id", "candidate_checkpoint_sha256", "candidate_manifest_sha256", "protected_parent_sha256",
            "intake_manifest_sha256", "source_evidence_path", "source_evidence_sha256", "source_evidence_payload_sha256",
        }
        expected_rollout = {
            "rollout_case_id", "episode_index", "task_index", "horizon", "observed_initial_state",
            "observed_action_sequence", "predicted_state_sequence",
        }
        if set(provenance) != expected_provenance or set(rollout) != expected_rollout:
            raise ChronosTransitionContractError("contract provenance or rollout fields disagree with schema")
        evidence = cls(
            candidate_id=_nonempty_string(provenance["candidate_id"], "candidate_id"),
            candidate_checkpoint_sha256=_sha256(provenance["candidate_checkpoint_sha256"], "candidate_checkpoint_sha256"),
            candidate_manifest_sha256=_sha256(provenance["candidate_manifest_sha256"], "candidate_manifest_sha256"),
            protected_parent_sha256=_sha256(provenance["protected_parent_sha256"], "protected_parent_sha256"),
            intake_manifest_sha256=_sha256(provenance["intake_manifest_sha256"], "intake_manifest_sha256"),
            source_evidence_sha256=_sha256(provenance["source_evidence_sha256"], "source_evidence_sha256"),
            source_evidence_payload_sha256=_sha256(provenance["source_evidence_payload_sha256"], "source_evidence_payload_sha256"),
            source_evidence_path=_nonempty_string(provenance["source_evidence_path"], "source_evidence_path"),
            rollout_case_id=_nonempty_string(rollout["rollout_case_id"], "rollout_case_id"),
            episode_index=int(rollout["episode_index"]),
            task_index=int(rollout["task_index"]),
            horizon=int(rollout["horizon"]),
            observed_initial_state=_finite_vector(rollout["observed_initial_state"], "observed_initial_state"),
            observed_action_sequence=tuple(_finite_vector(item, "observed action") for item in rollout["observed_action_sequence"]),
            predicted_state_sequence=tuple(_finite_vector(item, "predicted state") for item in rollout["predicted_state_sequence"]),
        )
        expected_digest = _sha256_json(evidence._without_digest())
        if payload["payload_sha256"] != expected_digest:
            raise ChronosTransitionContractError("contract payload SHA-256 mismatch")
        return evidence


def write_new_contract(path: Path, evidence: ChronosTransitionEvidence, *, allowed_root: Path) -> str:
    """Atomically write exactly one new schema-valid local contract witness."""

    destination = path.expanduser().resolve()
    root = allowed_root.expanduser().resolve()
    try:
        destination.relative_to(root)
    except ValueError as error:
        raise ChronosTransitionContractError("contract witness must remain under its local evidence root") from error
    if destination.exists():
        raise ChronosTransitionContractError("contract witness destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=False)
    payload = evidence.to_dict()
    # Validate canonical fields and digest immediately before persistent write.
    ChronosTransitionEvidence.from_dict(payload)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    if temporary.exists():
        raise ChronosTransitionContractError("contract temporary destination already exists")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, destination)
    except OSError as error:
        raise ChronosTransitionContractError("contract witness write failed") from error
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def load_verified_contract(path: Path) -> ChronosTransitionEvidence:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ChronosTransitionContractError("contract witness is not valid UTF-8 JSON") from error
    return ChronosTransitionEvidence.from_dict(payload)
