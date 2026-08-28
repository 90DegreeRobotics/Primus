"""Build a local limitation-forward evidence packet from frozen Primus artifacts."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
from typing import Any, Mapping

from .offline_artifact_safety import OfflineArtifactSafetyError, sha256_file, validate_offline_artifact_pair


BUYER_DEMO_VERSION = 1
DEMO_SCOPE = "offline_frozen_evidence_packet"
REQUIRED_HORIZONS = (1, 2, 5)
REQUIRED_LABEL = "Opaque 7D BridgeData state coordinates — not a Chronos scene, render, policy, or control signal."
PROHIBITED_CLAIM_TERMS = ("robot control", "actuation", "autonomous", "native chronos", "scene reconstruction", "renderer output", "safety certified", "product ready", "promotion")


class BuyerEvidencePacketError(ValueError):
    """Raised if an evidence packet cannot be constructed without weakening limits."""


@dataclass(frozen=True)
class StrictEvidenceRow:
    source_candidate_id: str
    horizon: int
    candidate_rmse: float
    strongest_baseline_name: str
    strongest_baseline_rmse: float
    margin: float
    case_count: int
    source_train_task_overlap: int
    selected_episode_overlap: int


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BuyerEvidencePacketError("evidence input is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise BuyerEvidencePacketError("evidence input must be a JSON object")
    return value


def _verify_payload_digest(payload: Mapping[str, Any], label: str) -> None:
    supplied = payload.get("payload_sha256")
    unsigned = {key: value for key, value in payload.items() if key != "payload_sha256"}
    expected = hashlib.sha256(_canonical_json(unsigned).encode("utf-8")).hexdigest()
    if supplied != expected:
        raise BuyerEvidencePacketError(f"{label} payload SHA-256 mismatch")


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise BuyerEvidencePacketError(f"{label} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise BuyerEvidencePacketError(f"{label} must be numeric") from error
    if not (result == result and abs(result) != float("inf")):
        raise BuyerEvidencePacketError(f"{label} must be finite")
    return result


def extract_strict_evidence_rows(payload: Mapping[str, Any]) -> tuple[StrictEvidenceRow, ...]:
    """Extract exact source-train task-disjoint rows; refuse incomplete or unsafe evidence."""

    _verify_payload_digest(payload, "strict rollout evidence")
    if tuple(payload.get("acceptance_horizons", ())) != REQUIRED_HORIZONS:
        raise BuyerEvidencePacketError("strict rollout evidence does not have the required fixed horizons")
    if payload.get("no_training") is not True or payload.get("no_checkpoint_mutation") is not True or payload.get("promotion_performed") is not False:
        raise BuyerEvidencePacketError("strict rollout evidence does not preserve frozen no-training/no-promotion boundary")
    reports = payload.get("source_reports")
    if not isinstance(reports, Mapping) or len(reports) != 2:
        raise BuyerEvidencePacketError("strict rollout evidence must contain exactly two frozen source reports")
    results: list[StrictEvidenceRow] = []
    for source_id, report in sorted(reports.items()):
        if not isinstance(report, Mapping) or report.get("point_estimate_passed_all_horizons") is not True or report.get("bootstrap_passed_all_horizons") is not True:
            raise BuyerEvidencePacketError("strict source report does not pass all declared horizons")
        rows = report.get("rows")
        if not isinstance(rows, list) or len(rows) != len(REQUIRED_HORIZONS):
            raise BuyerEvidencePacketError("strict source report rows are incomplete")
        seen: set[int] = set()
        for row in rows:
            if not isinstance(row, Mapping):
                raise BuyerEvidencePacketError("strict source report row is invalid")
            horizon = int(row.get("horizon", -1))
            if horizon not in REQUIRED_HORIZONS or horizon in seen:
                raise BuyerEvidencePacketError("strict source report horizons are invalid")
            seen.add(horizon)
            if row.get("source_candidate_id") != source_id:
                raise BuyerEvidencePacketError("strict source report candidate identity drift")
            if int(row.get("source_train_task_overlap_count", -1)) != 0 or int(row.get("source_selected_episode_overlap_count", -1)) != 0:
                raise BuyerEvidencePacketError("strict source report lacks task or episode disjointness")
            candidate = row.get("candidate_metrics")
            baselines = row.get("baseline_metrics")
            strongest = row.get("strongest_baseline")
            if not isinstance(candidate, Mapping) or not isinstance(baselines, Mapping) or strongest not in baselines or not isinstance(baselines[strongest], Mapping):
                raise BuyerEvidencePacketError("strict source report baseline metrics are invalid")
            candidate_rmse = _number(candidate.get("aggregate_rmse"), "candidate RMSE")
            baseline_rmse = _number(baselines[strongest].get("aggregate_rmse"), "strongest baseline RMSE")
            if candidate_rmse >= baseline_rmse:
                raise BuyerEvidencePacketError("strict source row does not improve on declared strongest baseline")
            coverage = candidate.get("coverage")
            if not isinstance(coverage, Mapping) or int(coverage.get("expected_prediction_count", -1)) != int(coverage.get("prediction_count", -2)) or int(coverage.get("unknown_prediction_count", -1)) != 0 or int(coverage.get("excluded_prediction_count", -1)) != 0:
                raise BuyerEvidencePacketError("strict source row does not have exact finite coverage")
            results.append(StrictEvidenceRow(
                source_candidate_id=source_id, horizon=horizon, candidate_rmse=candidate_rmse,
                strongest_baseline_name=str(strongest), strongest_baseline_rmse=baseline_rmse,
                margin=baseline_rmse - candidate_rmse, case_count=int(coverage["prediction_count"]),
                source_train_task_overlap=int(row["source_train_task_overlap_count"]),
                selected_episode_overlap=int(row["source_selected_episode_overlap_count"]),
            ))
    return tuple(sorted(results, key=lambda value: (value.source_candidate_id, value.horizon)))


def _build_html(rows: tuple[StrictEvidenceRow, ...], *, safety_receipt_sha256: str, strict_evidence_sha256: str, diagnostic_filename: str) -> str:
    grouped: dict[str, list[StrictEvidenceRow]] = {}
    for row in rows:
        grouped.setdefault(row.source_candidate_id, []).append(row)
    table_rows = []
    for source_id, source_rows in sorted(grouped.items()):
        for row in sorted(source_rows, key=lambda value: value.horizon):
            table_rows.append("<tr>" + "".join((
                f"<td>{html.escape(source_id)}</td>", f"<td>h{row.horizon}</td>", f"<td>{row.candidate_rmse:.10f}</td>",
                f"<td>{html.escape(row.strongest_baseline_name)}</td>", f"<td>{row.strongest_baseline_rmse:.10f}</td>",
                f"<td>+{row.margin:.10f}</td>", f"<td>{row.case_count}</td>",
            )) + "</tr>")
    forbidden = " · ".join(PROHIBITED_CLAIM_TERMS)
    template = """<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>Primus Frozen Evidence Packet</title><style>
body{margin:0;background:#f5f7fa;color:#17212b;font-family:Arial,sans-serif;line-height:1.45}.page{max-width:1100px;margin:auto;padding:38px}.hero{background:#12233d;color:#fff;padding:30px;border-radius:12px}.badge{display:inline-block;background:#d8e7ff;color:#123d6d;padding:6px 10px;border-radius:999px;font-weight:bold;font-size:13px}.warning{background:#fff1f1;border-left:5px solid #b42318;padding:16px;margin:24px 0;font-weight:bold}.card{background:#fff;border:1px solid #d9e0e8;border-radius:10px;padding:24px;margin:22px 0}.metric{font-size:28px;font-weight:bold;color:#0b5d3b}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #d9e0e8;padding:10px;text-align:left}th{background:#edf3fa}img{width:100%;height:auto;border:1px solid #ccd6e0;border-radius:6px}code{background:#eef2f6;padding:2px 4px;border-radius:3px;word-break:break-all}.limits{color:#5c1717}</style></head>
<body><main class=\"page\"><section class=\"hero\"><span class=\"badge\">OFFLINE EVIDENCE REVIEW ONLY</span><h1>Primus Local Transition-Prediction Evidence</h1><p>This packet presents frozen, provenance-bound evaluation results for two compact locally trained 7D state-transition predictors. It is a local evidence packet, not a product demonstration.</p></section>
<section class=\"warning\">{label}<br>This packet does not authorize execution, rendering, policy use, robot action, promotion, or native Chronos operation.</section>
<section class=\"card\"><h2>What was measured</h2><p>Each frozen predictor was evaluated on 256 exact finite open-loop cases at h1, h2, and h5. Target task identities and selected episodes were absent from the respective source training partitions. Each candidate beat its declared strongest source-train-only baseline in every displayed row, with point-estimate and episode-clustered bootstrap gates passing in the signed strict evaluation.</p><table><thead><tr><th>Frozen source</th><th>Horizon</th><th>Candidate RMSE</th><th>Strongest baseline</th><th>Baseline RMSE</th><th>Margin</th><th>Cases</th></tr></thead><tbody>{table_rows}</tbody></table></section>
<section class=\"card\"><h2>One raw-lineage-verified diagnostic trace</h2><p>The chart below compares one witness's observed and recursively predicted opaque numeric coordinates across five observed actions. Coordinate meanings are intentionally unknown; the chart is a data diagnostic, not a reconstructed world.</p><img src=\"{image}\" alt=\"Offline opaque 7D state-transition diagnostic\"></section>
<section class=\"card limits\"><h2>What this does not show</h2><p>It does not show or authorize: {forbidden}. It does not establish causal understanding, vision, long-horizon reliability, physical-world semantics, or general intelligence. The checked safety gate only proves the current artifact schemas preserve offline-only flags; it is not runtime or physical safety certification.</p></section>
<section class=\"card\"><h2>Integrity bindings</h2><p>Strict evidence SHA-256: <code>{strict_hash}</code></p><p>Offline safety receipt SHA-256: <code>{safety_hash}</code></p><p>Packet scope: <code>{scope}</code> · execution authorization: <code>false</code></p></section>
</main></body></html>"""
    replacements = {
        "label": html.escape(REQUIRED_LABEL),
        "table_rows": "\n".join(table_rows),
        "image": html.escape(diagnostic_filename),
        "forbidden": html.escape(forbidden),
        "strict_hash": html.escape(strict_evidence_sha256),
        "safety_hash": html.escape(safety_receipt_sha256),
        "scope": DEMO_SCOPE,
    }
    for key, value in replacements.items():
        template = template.replace("{" + key + "}", value)
    return template


def build_buyer_evidence_packet(*, witness_path: Path, diagnostic_receipt_path: Path, diagnostic_png_path: Path, safety_receipt_path: Path, strict_evidence_path: Path, output_dir: Path, allowed_root: Path) -> dict[str, Any]:
    """Build one fresh local packet only after mandatory offline-safety validation."""

    output = output_dir.expanduser().resolve(); root = allowed_root.expanduser().resolve()
    try:
        output.relative_to(root)
    except ValueError as error:
        raise BuyerEvidencePacketError("buyer demo packet must remain under local evidence root") from error
    if output.exists():
        raise BuyerEvidencePacketError("buyer demo packet destination already exists")
    try:
        safety = validate_offline_artifact_pair(witness_path=witness_path, diagnostic_receipt_path=diagnostic_receipt_path, diagnostic_png_path=diagnostic_png_path)
    except OfflineArtifactSafetyError as error:
        raise BuyerEvidencePacketError("offline safety prerequisite failed") from error
    if safety.get("execution_authorized") is not False:
        raise BuyerEvidencePacketError("offline safety prerequisite did not reject execution")
    safety_payload = _load_json(safety_receipt_path); _verify_payload_digest(safety_payload, "offline safety receipt")
    if safety_payload.get("execution_authorized") is not False or safety_payload.get("control_permitted") is not False or safety_payload.get("renderer_permitted") is not False or safety_payload.get("chronos_execution_permitted") is not False or safety_payload.get("promotion_performed") is not False:
        raise BuyerEvidencePacketError("stored safety receipt lacks false offline-only flags")
    strict_payload = _load_json(strict_evidence_path); rows = extract_strict_evidence_rows(strict_payload)
    output.mkdir(parents=True, exist_ok=False)
    chart_copy = output / "offline_opaque_state_diagnostic.png"; shutil.copyfile(diagnostic_png_path, chart_copy)
    if sha256_file(chart_copy) != sha256_file(diagnostic_png_path):
        raise BuyerEvidencePacketError("copied diagnostic hash mismatch")
    index_path = output / "index.html"
    index_path.write_text(_build_html(rows, safety_receipt_sha256=sha256_file(safety_receipt_path), strict_evidence_sha256=sha256_file(strict_evidence_path), diagnostic_filename=chart_copy.name), encoding="utf-8", newline="\n")
    page = index_path.read_text(encoding="utf-8").lower()
    if REQUIRED_LABEL.lower() not in page or "what this does not show" not in page or "does not authorize execution" not in page:
        raise BuyerEvidencePacketError("buyer packet lacks required explicit limitation text")
    receipt = {"buyer_demo_version": BUYER_DEMO_VERSION, "demo_scope": DEMO_SCOPE, "index_html_sha256": sha256_file(index_path), "copied_chart_sha256": sha256_file(chart_copy), "strict_evidence_sha256": sha256_file(strict_evidence_path), "strict_evidence_payload_sha256": strict_payload["payload_sha256"], "safety_receipt_sha256": sha256_file(safety_receipt_path), "safety_receipt_payload_sha256": safety_payload["payload_sha256"], "execution_authorized": False, "control_permitted": False, "renderer_permitted": False, "chronos_execution_permitted": False, "promotion_performed": False, "required_label": REQUIRED_LABEL, "source_candidate_ids": sorted({row.source_candidate_id for row in rows}), "horizons": list(REQUIRED_HORIZONS)}
    receipt["payload_sha256"] = hashlib.sha256(_canonical_json(receipt).encode("utf-8")).hexdigest()
    (output / "demo_receipt.json").write_text(json.dumps(receipt, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return receipt

