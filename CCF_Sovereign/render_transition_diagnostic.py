"""Render one deterministic offline diagnostic from a verified transition witness."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.bridgedata_transitions import BridgeDataTransitionConfig, derive_bridgedata_transitions, load_bridgedata_intake, sha256_file
from real_data.chronos_transition_contract import STATE_COORDINATE_SEMANTICS, load_verified_contract
from real_data.transition_diagnostic import component_absolute_errors, resolve_observed_sequence


WITNESS_PATH = ROOT / "evidence" / "chronos_transition_contracts" / "bridge-real-20260827-002-h5-witness.json"
INTAKE_MANIFEST_PATH = ROOT / "data" / "external" / "bridgedata2_lerobot_v3_metadata_20260827" / "intake_manifest.json"
DEFAULT_OUTPUT_ROOT = ROOT / "evidence" / "transition_diagnostics"
DEFAULT_OUTPUT_DIR = DEFAULT_OUTPUT_ROOT / "diagnostic-20260828-001"


class TransitionDiagnosticRenderError(ValueError):
    pass


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _write_new_json(path: Path, payload: dict) -> None:
    if path.exists():
        raise TransitionDiagnosticRenderError("diagnostic receipt destination already exists")
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")


def render_diagnostic(*, output_dir: Path) -> dict:
    output_dir = output_dir.expanduser().resolve()
    root = DEFAULT_OUTPUT_ROOT.resolve()
    try:
        output_dir.relative_to(root)
    except ValueError as error:
        raise TransitionDiagnosticRenderError("diagnostic output must remain under local evidence root") from error
    if output_dir.exists():
        raise TransitionDiagnosticRenderError("diagnostic output destination already exists")
    evidence = load_verified_contract(WITNESS_PATH)
    if evidence.to_dict()["state_coordinate_semantics"] != STATE_COORDINATE_SEMANTICS:
        raise TransitionDiagnosticRenderError("witness coordinate semantics are not the required explicit unknown sentinel")
    intake = load_bridgedata_intake(INTAKE_MANIFEST_PATH)
    extracted = derive_bridgedata_transitions(
        intake, BridgeDataTransitionConfig(selected_episode_indices=frozenset({evidence.episode_index})),
    )
    observed = resolve_observed_sequence(extracted.transitions, evidence)
    errors = component_absolute_errors(observed, evidence)
    actual = np.asarray(observed.observed_state_sequence, dtype=np.float64)
    predicted = np.asarray(evidence.predicted_state_sequence, dtype=np.float64)
    absolute_error = np.asarray(errors, dtype=np.float64)
    if actual.shape != (evidence.horizon, 7) or predicted.shape != actual.shape or not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise TransitionDiagnosticRenderError("verified diagnostic arrays are not finite expected-shape traces")
    output_dir.mkdir(parents=True, exist_ok=False)
    figure = plt.figure(figsize=(16, 10.5), dpi=100, constrained_layout=True)
    grid = figure.add_gridspec(4, 2, height_ratios=(1.0, 1.0, 1.0, 1.25))
    steps = np.arange(1, evidence.horizon + 1)
    colors = {"observed": "#1f4e79", "predicted": "#c55a11", "error": "#7f6000"}
    for coordinate in range(7):
        axis = figure.add_subplot(grid[coordinate // 2, coordinate % 2])
        axis.plot(steps, actual[:, coordinate], color=colors["observed"], marker="o", linewidth=2.0, label="Observed")
        axis.plot(steps, predicted[:, coordinate], color=colors["predicted"], marker="s", linestyle="--", linewidth=2.0, label="Frozen predictor")
        axis.set_title(f"State coordinate {coordinate + 1}", fontsize=11, fontweight="bold")
        axis.set_xlabel("Observed action step")
        axis.set_ylabel("Opaque numeric value")
        axis.set_xticks(steps)
        axis.grid(alpha=0.25)
        if coordinate == 0:
            axis.legend(loc="best", frameon=False)
    error_axis = figure.add_subplot(grid[3, :])
    coordinate_labels = [f"C{index}" for index in range(1, 8)]
    for step_index, step in enumerate(steps):
        error_axis.plot(coordinate_labels, absolute_error[step_index], marker="o", linewidth=1.6, label=f"Step {step}")
    error_axis.set_title("Absolute error by opaque state coordinate", fontsize=11, fontweight="bold")
    error_axis.set_xlabel("State coordinate")
    error_axis.set_ylabel("Absolute error")
    error_axis.grid(alpha=0.25)
    error_axis.legend(ncol=evidence.horizon, loc="upper left", frameon=False)
    figure.suptitle("Offline 7D State-Transition Diagnostic — Frozen Candidate 002, Strict Task-Disjoint h5 Witness", fontsize=16, fontweight="bold")
    figure.text(0.5, 0.01, "Opaque 7D BridgeData state coordinates — not a Chronos scene, render, policy, or control signal.", ha="center", va="bottom", fontsize=10, color="#7f0000", fontweight="bold")
    png_path = output_dir / "opaque_state_trajectory_diagnostic.png"
    figure.savefig(png_path, dpi=100, facecolor="white")
    plt.close(figure)
    if not png_path.is_file() or png_path.stat().st_size < 10_000:
        raise TransitionDiagnosticRenderError("diagnostic PNG was not written at plausible nonempty size")
    receipt = {
        "diagnostic_version": 1,
        "diagnostic_scope": "offline_opaque_7d_state_trajectory_plot",
        "png_path": str(png_path),
        "png_sha256": sha256_file(png_path),
        "png_bytes": png_path.stat().st_size,
        "png_dimensions": [1600, 1050],
        "witness_path": str(WITNESS_PATH),
        "witness_sha256": sha256_file(WITNESS_PATH),
        "witness_payload_sha256": evidence.payload_sha256(),
        "intake_manifest_sha256": intake.manifest_sha256,
        "episode_index": evidence.episode_index,
        "task_index": evidence.task_index,
        "horizon": evidence.horizon,
        "observed_transition_ids": list(observed.source_transition_ids),
        "component_mean_absolute_error": [float(value) for value in absolute_error.mean(axis=0)],
        "overall_mean_absolute_error": float(absolute_error.mean()),
        "chronos_invoked": False,
        "renderer_invoked": False,
        "control_permitted": False,
        "promotion_performed": False,
        "required_label": "Opaque 7D BridgeData state coordinates — not a Chronos scene, render, policy, or control signal.",
    }
    receipt["payload_sha256"] = hashlib.sha256(_canonical_json(receipt).encode("utf-8")).hexdigest()
    _write_new_json(output_dir / "diagnostic_receipt.json", receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a deterministic offline opaque-state diagnostic.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    arguments = parser.parse_args()
    print(json.dumps(render_diagnostic(output_dir=Path(arguments.output_dir)), ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
