"""Build one local buyer evidence packet from frozen offline-only Primus artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.buyer_evidence_packet import build_buyer_evidence_packet


WITNESS = ROOT / "evidence" / "chronos_transition_contracts" / "bridge-real-20260827-002-h5-witness.json"
DIAGNOSTIC_ROOT = ROOT / "evidence" / "transition_diagnostics" / "diagnostic-20260828-002-complete"
SAFETY_RECEIPT = ROOT / "evidence" / "offline_artifact_safety" / "safety-20260828-001" / "offline_artifact_safety_receipt.json"
STRICT_EVIDENCE = ROOT / "evaluation" / "bridgedata_strict_task_cross_rollouts" / "strict-task-cross-rollout-20260828-001" / "strict_task_cross_rollout.json"
OUTPUT_ROOT = ROOT / "evidence" / "buyer_demo_packets"
DEFAULT_OUTPUT = OUTPUT_ROOT / "buyer-evidence-20260828-001"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a local offline-only Primus buyer evidence packet.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    receipt = build_buyer_evidence_packet(
        witness_path=WITNESS,
        diagnostic_receipt_path=DIAGNOSTIC_ROOT / "diagnostic_receipt.json",
        diagnostic_png_path=DIAGNOSTIC_ROOT / "opaque_state_trajectory_diagnostic.png",
        safety_receipt_path=SAFETY_RECEIPT,
        strict_evidence_path=STRICT_EVIDENCE,
        output_dir=Path(args.output_dir),
        allowed_root=OUTPUT_ROOT,
    )
    print(json.dumps({"output_dir": str(Path(args.output_dir).resolve()), **receipt}, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
