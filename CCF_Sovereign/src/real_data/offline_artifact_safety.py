"""Mechanical offline-only safety gate for Primus transition evidence artifacts."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .chronos_transition_contract import (
    STATE_COORDINATE_SEMANTICS,
    ChronosTransitionContractError,
    load_verified_contract,
)


SAFETY_GATE_VERSION = 1
OFFLINE_INTENT = "offline_observational_evidence_review"
REQUIRED_DIAGNOSTIC_SCOPE = "offline_opaque_7d_state_trajectory_plot"
REQUIRED_DIAGNOSTIC_LABEL = "Opaque 7D BridgeData state coordinates — not a Chronos scene, render, policy, or control signal."
REQUIRED_FALSE_FLAGS = ("chronos_invoked", "renderer_invoked", "control_permitted", "promotion_performed")
REQUIRED_RECEIPT_FIELDS = frozenset({
    "diagnostic_version", "diagnostic_scope", "png_path", "png_sha256", "png_bytes", "png_dimensions",
    "witness_path", "witness_sha256", "witness_payload_sha256", "intake_manifest_sha256", "episode_index",
    "task_index", "horizon", "observed_transition_ids", "component_mean_absolute_error", "overall_mean_absolute_error",
    *REQUIRED_FALSE_FLAGS, "required_label", "payload_sha256",
})


class OfflineArtifactSafetyError(ValueError):
    """Raised when an artifact is unsafe or insufficiently bound for offline review."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as error:
        raise OfflineArtifactSafetyError("required artifact is unreadable") from error
    return digest.hexdigest()


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OfflineArtifactSafetyError("artifact receipt is not valid UTF-8 JSON") from error
    if not isinstance(data, dict):
        raise OfflineArtifactSafetyError("artifact receipt must be a JSON object")
    return data


def _validate_digest(payload: Mapping[str, Any]) -> None:
    if "payload_sha256" not in payload:
        raise OfflineArtifactSafetyError("artifact receipt lacks payload SHA-256")
    unsigned = {key: value for key, value in payload.items() if key != "payload_sha256"}
    expected = hashlib.sha256(_canonical_json(unsigned).encode("utf-8")).hexdigest()
    if payload["payload_sha256"] != expected:
        raise OfflineArtifactSafetyError("artifact receipt payload SHA-256 mismatch")


def _assert_false_flags(payload: Mapping[str, Any]) -> None:
    for key in REQUIRED_FALSE_FLAGS:
        if payload.get(key) is not False:
            raise OfflineArtifactSafetyError(f"offline artifact requires {key}=false")


def validate_offline_artifact_pair(*, witness_path: Path, diagnostic_receipt_path: Path, diagnostic_png_path: Path, consumer_intent: str = OFFLINE_INTENT) -> dict[str, Any]:
    """Validate one frozen contract witness plus its diagnostic as offline-only evidence.

    The function has no action, renderer, network, model, or Chronos interfaces.
    """

    if consumer_intent != OFFLINE_INTENT:
        raise OfflineArtifactSafetyError("consumer intent is not permitted for offline-only evidence")
    try:
        witness = load_verified_contract(witness_path)
    except ChronosTransitionContractError as error:
        raise OfflineArtifactSafetyError("contract witness failed validation") from error
    witness_payload = witness.to_dict()
    if witness_payload["state_coordinate_semantics"] != STATE_COORDINATE_SEMANTICS:
        raise OfflineArtifactSafetyError("contract must retain unknown coordinate semantics")
    if witness_payload["control_permitted"] is not False or witness_payload["promotion_performed"] is not False:
        raise OfflineArtifactSafetyError("contract cannot permit control or promotion")
    diagnostic = _load_json(diagnostic_receipt_path)
    if set(diagnostic) != REQUIRED_RECEIPT_FIELDS:
        unexpected = set(diagnostic) - REQUIRED_RECEIPT_FIELDS
        missing = REQUIRED_RECEIPT_FIELDS - set(diagnostic)
        raise OfflineArtifactSafetyError("diagnostic receipt schema is unsafe or incomplete: unexpected=" + ",".join(sorted(unexpected)) + ";missing=" + ",".join(sorted(missing)))
    _validate_digest(diagnostic)
    _assert_false_flags(diagnostic)
    if diagnostic["diagnostic_scope"] != REQUIRED_DIAGNOSTIC_SCOPE:
        raise OfflineArtifactSafetyError("diagnostic scope is not opaque offline state evidence")
    if diagnostic["required_label"] != REQUIRED_DIAGNOSTIC_LABEL:
        raise OfflineArtifactSafetyError("diagnostic lacks required offline-only disclaimer")
    if diagnostic["witness_sha256"] != sha256_file(witness_path):
        raise OfflineArtifactSafetyError("diagnostic witness file binding mismatch")
    if diagnostic["witness_payload_sha256"] != witness.payload_sha256():
        raise OfflineArtifactSafetyError("diagnostic witness payload binding mismatch")
    if diagnostic["png_sha256"] != sha256_file(diagnostic_png_path):
        raise OfflineArtifactSafetyError("diagnostic PNG binding mismatch")
    if diagnostic["png_bytes"] != diagnostic_png_path.stat().st_size or diagnostic["png_bytes"] <= 0:
        raise OfflineArtifactSafetyError("diagnostic PNG byte evidence mismatch")
    if tuple(diagnostic["png_dimensions"]) != (1600, 1050):
        raise OfflineArtifactSafetyError("diagnostic PNG dimensions are not the declared fixed layout")
    if diagnostic["horizon"] != witness.horizon or diagnostic["episode_index"] != witness.episode_index or diagnostic["task_index"] != witness.task_index:
        raise OfflineArtifactSafetyError("diagnostic lineage identifiers disagree with contract witness")
    return {
        "safety_gate_version": SAFETY_GATE_VERSION,
        "consumer_intent": OFFLINE_INTENT,
        "execution_authorized": False,
        "control_permitted": False,
        "renderer_permitted": False,
        "chronos_execution_permitted": False,
        "promotion_performed": False,
        "witness_sha256": sha256_file(witness_path),
        "witness_payload_sha256": witness.payload_sha256(),
        "diagnostic_receipt_sha256": sha256_file(diagnostic_receipt_path),
        "diagnostic_receipt_payload_sha256": diagnostic["payload_sha256"],
        "diagnostic_png_sha256": sha256_file(diagnostic_png_path),
        "diagnostic_png_dimensions": list(diagnostic["png_dimensions"]),
        "required_label": REQUIRED_DIAGNOSTIC_LABEL,
        "limitations": [
            "Validation authorizes offline evidence review only; it has no action, command, execution, policy, renderer, or network output.",
            "The 7D state coordinates retain unknown scene semantics and cannot be transformed into Chronos geometry or robot control from this gate.",
            "This mechanical schema check is not a runtime-safety, physical-safety, policy-quality, or downstream-consumer compliance proof.",
        ],
    }


def write_new_safety_receipt(path: Path, report: Mapping[str, Any], *, allowed_root: Path) -> str:
    destination = path.expanduser().resolve()
    root = allowed_root.expanduser().resolve()
    try:
        destination.relative_to(root)
    except ValueError as error:
        raise OfflineArtifactSafetyError("safety receipt must remain under local evidence root") from error
    if destination.exists():
        raise OfflineArtifactSafetyError("safety receipt destination already exists")
    if report.get("execution_authorized") is not False:
        raise OfflineArtifactSafetyError("safety receipt cannot authorize execution")
    destination.parent.mkdir(parents=True, exist_ok=False)
    payload = dict(report)
    payload["payload_sha256"] = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    if temporary.exists():
        raise OfflineArtifactSafetyError("safety receipt temporary destination already exists")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, destination)
    except OSError as error:
        raise OfflineArtifactSafetyError("safety receipt write failed") from error
    return sha256_file(destination)
