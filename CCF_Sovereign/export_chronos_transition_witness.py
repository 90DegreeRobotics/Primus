"""Export one non-executable Primus transition-evidence witness for future Chronos consumers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluate_bridgedata_rollout_stability import ROOT, _sha256_json, load_frozen_rollout_candidate
from evaluate_bridgedata_strict_task_cross_rollout import INTAKE_MANIFEST_PATH, select_strict_target_episodes
from real_data.bridgedata_rollouts import DEFAULT_CASE_SELECTION_SEED, build_rollout_cases
from real_data.bridgedata_transitions import BridgeDataTransitionConfig, derive_bridgedata_transitions, load_bridgedata_intake, sha256_file
from real_data.chronos_transition_contract import ChronosTransitionEvidence, write_new_contract
from train_bridgedata_real_transition import resolve_device


CANDIDATE_ID = "bridge-real-20260827-002"
STRICT_EVIDENCE_PATH = (
    ROOT / "evaluation" / "bridgedata_strict_task_cross_rollouts"
    / "strict-task-cross-rollout-20260828-001" / "strict_task_cross_rollout.json"
)
DEFAULT_EVIDENCE_ROOT = (
    ROOT / "evidence" / "chronos_transition_contracts"
)
DEFAULT_OUTPUT_PATH = DEFAULT_EVIDENCE_ROOT / "bridge-real-20260827-002-h5-witness.json"


class TransitionWitnessExportError(ValueError):
    pass


def _load_strict_evidence(path: Path) -> dict:
    if not path.is_file():
        raise TransitionWitnessExportError("strict rollout evidence is missing")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise TransitionWitnessExportError("strict rollout evidence is not valid JSON") from error
    if not isinstance(payload, dict) or payload.get("payload_sha256") != _sha256_json({key: value for key, value in payload.items() if key != "payload_sha256"}):
        raise TransitionWitnessExportError("strict rollout evidence payload digest mismatch")
    return payload


def export_one_witness(*, output_path: Path, device_name: str = "cpu") -> dict:
    source_evidence = _load_strict_evidence(STRICT_EVIDENCE_PATH)
    device = resolve_device(device_name)
    frozen = load_frozen_rollout_candidate(CANDIDATE_ID, device=device)
    intake = load_bridgedata_intake(INTAKE_MANIFEST_PATH)
    selected = select_strict_target_episodes(CANDIDATE_ID, frozen["split"], intake.episodes)
    extracted = derive_bridgedata_transitions(
        intake,
        BridgeDataTransitionConfig(selected_episode_indices=frozenset(item.episode_index for item in selected)),
    )
    cases = build_rollout_cases(
        extracted.transitions,
        split="held_out_task",
        horizon=5,
        max_cases=256,
        case_selection_seed=DEFAULT_CASE_SELECTION_SEED,
    )
    if not cases:
        raise TransitionWitnessExportError("strict rollout case selection is empty")
    case = sorted(cases, key=lambda item: item.case_id)[0]
    current_state = case.initial_state
    predicted_states = []
    for action in case.actions:
        current_state = tuple(float(value) for value in frozen["model_predictor"](current_state, action))
        predicted_states.append(current_state)
    candidate_root = ROOT / "checkpoints" / "candidates" / CANDIDATE_ID
    evidence = ChronosTransitionEvidence(
        candidate_id=CANDIDATE_ID,
        candidate_checkpoint_sha256=sha256_file(candidate_root / "checkpoints" / "state_transition_mlp.pt"),
        candidate_manifest_sha256=sha256_file(candidate_root / "real_data.run.manifest.json"),
        protected_parent_sha256=sha256_file(ROOT / "checkpoints" / "primus_council_trained.pt"),
        intake_manifest_sha256=sha256_file(INTAKE_MANIFEST_PATH),
        source_evidence_sha256=sha256_file(STRICT_EVIDENCE_PATH),
        source_evidence_payload_sha256=str(source_evidence["payload_sha256"]),
        source_evidence_path=str(STRICT_EVIDENCE_PATH.resolve()),
        rollout_case_id=case.case_id,
        episode_index=case.episode_index,
        task_index=case.task_index,
        horizon=case.horizon,
        observed_initial_state=case.initial_state,
        observed_action_sequence=case.actions,
        predicted_state_sequence=tuple(predicted_states),
    )
    file_sha256 = write_new_contract(output_path, evidence, allowed_root=DEFAULT_EVIDENCE_ROOT)
    return {
        "output_path": str(output_path.resolve()),
        "file_sha256": file_sha256,
        "payload_sha256": evidence.payload_sha256(),
        "candidate_id": CANDIDATE_ID,
        "rollout_case_id": case.case_id,
        "horizon": case.horizon,
        "chronos_invoked": False,
        "control_permitted": False,
        "promotion_performed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export one schema-only Primus transition-evidence witness.")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--device", default="cpu", choices=("cpu", "auto", "cuda"))
    arguments = parser.parse_args()
    print(json.dumps(export_one_witness(output_path=Path(arguments.output_path), device_name=arguments.device), ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
