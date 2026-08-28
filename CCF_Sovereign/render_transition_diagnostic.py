"""Render one deterministic offline diagnostic from a verified transition witness using Pillow."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.bridgedata_transitions import BridgeDataTransitionConfig, derive_bridgedata_transitions, load_bridgedata_intake, sha256_file
from real_data.chronos_transition_contract import STATE_COORDINATE_SEMANTICS, load_verified_contract
from real_data.transition_diagnostic import component_absolute_errors, resolve_observed_sequence


WITNESS_PATH = ROOT / "evidence" / "chronos_transition_contracts" / "bridge-real-20260827-002-h5-witness.json"
INTAKE_MANIFEST_PATH = ROOT / "data" / "external" / "bridgedata2_lerobot_v3_metadata_20260827" / "intake_manifest.json"
DEFAULT_OUTPUT_ROOT = ROOT / "evidence" / "transition_diagnostics"
DEFAULT_OUTPUT_DIR = DEFAULT_OUTPUT_ROOT / "diagnostic-20260828-001"
WIDTH, HEIGHT = 1600, 1050


class TransitionDiagnosticRenderError(ValueError):
    pass


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _write_new_json(path: Path, payload: dict) -> None:
    if path.exists():
        raise TransitionDiagnosticRenderError("diagnostic receipt destination already exists")
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")


def _line_points(values: tuple[float, ...], bounds: tuple[int, int, int, int], low: float, high: float) -> list[tuple[float, float]]:
    left, top, right, bottom = bounds
    if len(values) == 1:
        return [((left + right) / 2.0, (top + bottom) / 2.0)]
    span = high - low
    return [
        (
            left + index * (right - left) / (len(values) - 1),
            bottom - (value - low) * (bottom - top) / span,
        )
        for index, value in enumerate(values)
    ]


def _draw_trace_panel(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], coordinate: int, actual: tuple[tuple[float, ...], ...], predicted: tuple[tuple[float, ...], ...], fonts: dict[str, ImageFont.ImageFont]) -> None:
    left, top, right, bottom = bounds
    panel = (250, 250, 250)
    draw.rectangle(bounds, outline=(174, 174, 174), width=1, fill=(252, 252, 252))
    actual_values = tuple(row[coordinate] for row in actual)
    predicted_values = tuple(row[coordinate] for row in predicted)
    lower, upper = min(actual_values + predicted_values), max(actual_values + predicted_values)
    padding = max((upper - lower) * 0.12, 1e-6)
    low, high = lower - padding, upper + padding
    for fraction in (0.25, 0.5, 0.75):
        y = top + fraction * (bottom - top)
        draw.line((left, y, right, y), fill=panel, width=1)
    draw.text((left + 8, top + 6), f"State coordinate {coordinate + 1}", fill=(25, 25, 25), font=fonts["panel_bold"])
    draw.text((left + 8, top + 26), f"range {low:.4g} to {high:.4g}", fill=(95, 95, 95), font=fonts["small"])
    plot = (left + 46, top + 48, right - 16, bottom - 32)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill=(120, 120, 120), width=1)
    draw.line((plot[0], plot[1], plot[0], plot[3]), fill=(120, 120, 120), width=1)
    draw.line(_line_points(actual_values, plot, low, high), fill=(31, 78, 121), width=3)
    draw.line(_line_points(predicted_values, plot, low, high), fill=(197, 90, 17), width=3)
    for x, y in _line_points(actual_values, plot, low, high):
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(31, 78, 121))
    for x, y in _line_points(predicted_values, plot, low, high):
        draw.rectangle((x - 3, y - 3, x + 3, y + 3), fill=(197, 90, 17))
    for index in range(len(actual_values)):
        x = plot[0] + index * (plot[2] - plot[0]) / max(len(actual_values) - 1, 1)
        draw.text((x - 5, plot[3] + 7), str(index + 1), fill=(75, 75, 75), font=fonts["small"])


def _draw_error_panel(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], errors: tuple[tuple[float, ...], ...], fonts: dict[str, ImageFont.ImageFont]) -> None:
    left, top, right, bottom = bounds
    draw.rectangle(bounds, outline=(174, 174, 174), width=1, fill=(252, 252, 252))
    draw.text((left + 8, top + 6), "Absolute error by opaque state coordinate", fill=(25, 25, 25), font=fonts["panel_bold"])
    plot = (left + 62, top + 42, right - 24, bottom - 35)
    maximum = max(max(row) for row in errors)
    high = maximum * 1.15 if maximum > 0.0 else 1.0
    for fraction in (0.25, 0.5, 0.75):
        y = plot[3] - fraction * (plot[3] - plot[1])
        draw.line((plot[0], y, plot[2], y), fill=(235, 235, 235), width=1)
    draw.text((left + 10, top + 52), f"0\n\n\n{high:.3g}", fill=(80, 80, 80), font=fonts["small"], spacing=14)
    colors = ((127, 96, 0), (75, 134, 180), (112, 173, 71), (165, 165, 165), (112, 48, 160))
    for row_index, row in enumerate(errors):
        values = tuple(float(value) for value in row)
        points = _line_points(values, plot, 0.0, high)
        draw.line(points, fill=colors[row_index], width=3)
        for x, y in points:
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=colors[row_index])
        draw.text((plot[0] + 12 + row_index * 120, top + 18), f"Step {row_index + 1}", fill=colors[row_index], font=fonts["small"])
    for coordinate in range(7):
        x = plot[0] + coordinate * (plot[2] - plot[0]) / 6
        draw.text((x - 7, plot[3] + 8), f"C{coordinate + 1}", fill=(75, 75, 75), font=fonts["small"])


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
    extracted = derive_bridgedata_transitions(intake, BridgeDataTransitionConfig(selected_episode_indices=frozenset({evidence.episode_index})))
    observed = resolve_observed_sequence(extracted.transitions, evidence)
    errors = component_absolute_errors(observed, evidence)
    if len(observed.observed_state_sequence) != evidence.horizon or any(len(row) != 7 for row in observed.observed_state_sequence + evidence.predicted_state_sequence + errors):
        raise TransitionDiagnosticRenderError("verified diagnostic arrays have an invalid shape")
    if not all(all(math.isfinite(value) for value in row) for row in observed.observed_state_sequence + evidence.predicted_state_sequence + errors):
        raise TransitionDiagnosticRenderError("verified diagnostic arrays contain nonfinite values")
    output_dir.mkdir(parents=True, exist_ok=False)
    image = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    fonts = {"title": _font(25, bold=True), "panel_bold": _font(15, bold=True), "small": _font(12), "body": _font(14)}
    draw.text((40, 24), "Offline 7D State-Transition Diagnostic — Frozen Candidate 002, Strict Task-Disjoint h5 Witness", fill=(20, 20, 20), font=fonts["title"])
    draw.line((40, 66, 1560, 66), fill=(31, 78, 121), width=3)
    draw.line((48, 83, 83, 83), fill=(31, 78, 121), width=3); draw.ellipse((62, 79, 68, 85), fill=(31, 78, 121)); draw.text((91, 75), "Observed state", fill=(31, 78, 121), font=fonts["body"])
    draw.line((252, 83, 287, 83), fill=(197, 90, 17), width=3); draw.rectangle((267, 79, 273, 85), fill=(197, 90, 17)); draw.text((295, 75), "Frozen predictor", fill=(197, 90, 17), font=fonts["body"])
    margin_x, gap_x, panel_width = 40, 28, 746
    top, panel_height, gap_y = 116, 190, 18
    for coordinate in range(7):
        column, row = coordinate % 2, coordinate // 2
        left = margin_x + column * (panel_width + gap_x)
        panel_top = top + row * (panel_height + gap_y)
        _draw_trace_panel(draw, (left, panel_top, left + panel_width, panel_top + panel_height), coordinate, observed.observed_state_sequence, evidence.predicted_state_sequence, fonts)
    _draw_error_panel(draw, (40, 750, 1560, 952), errors, fonts)
    required_label = "Opaque 7D BridgeData state coordinates — not a Chronos scene, render, policy, or control signal."
    draw.text((65, 1002), required_label, fill=(127, 0, 0), font=_font(16, bold=True))
    png_path = output_dir / "opaque_state_trajectory_diagnostic.png"
    image.save(png_path, format="PNG", optimize=True)
    if not png_path.is_file() or png_path.stat().st_size < 10_000:
        raise TransitionDiagnosticRenderError("diagnostic PNG was not written at plausible nonempty size")
    flattened_errors = [value for row in errors for value in row]
    receipt = {
        "diagnostic_version": 1, "diagnostic_scope": "offline_opaque_7d_state_trajectory_plot",
        "png_path": str(png_path), "png_sha256": sha256_file(png_path), "png_bytes": png_path.stat().st_size,
        "png_dimensions": [WIDTH, HEIGHT], "witness_path": str(WITNESS_PATH), "witness_sha256": sha256_file(WITNESS_PATH),
        "witness_payload_sha256": evidence.payload_sha256(), "intake_manifest_sha256": intake.manifest_sha256,
        "episode_index": evidence.episode_index, "task_index": evidence.task_index, "horizon": evidence.horizon,
        "observed_transition_ids": list(observed.source_transition_ids),
        "component_mean_absolute_error": [sum(row[index] for row in errors) / len(errors) for index in range(7)],
        "overall_mean_absolute_error": sum(flattened_errors) / len(flattened_errors),
        "chronos_invoked": False, "renderer_invoked": False, "control_permitted": False, "promotion_performed": False,
        "required_label": required_label,
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
