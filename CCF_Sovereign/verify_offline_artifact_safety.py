"""Write one local offline-only safety receipt for the accepted transition diagnostic."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from real_data.offline_artifact_safety import validate_offline_artifact_pair, write_new_safety_receipt


WITNESS = ROOT / "evidence" / "chronos_transition_contracts" / "bridge-real-20260827-002-h5-witness.json"
DIAGNOSTIC_ROOT = ROOT / "evidence" / "transition_diagnostics" / "diagnostic-20260828-002-complete"
RECEIPT = DIAGNOSTIC_ROOT / "diagnostic_receipt.json"
PNG = DIAGNOSTIC_ROOT / "opaque_state_trajectory_diagnostic.png"
OUTPUT_ROOT = ROOT / "evidence" / "offline_artifact_safety"
DEFAULT_OUTPUT = OUTPUT_ROOT / "safety-20260828-001" / "offline_artifact_safety_receipt.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate one offline-only Primus evidence pair.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve()
    report = validate_offline_artifact_pair(
        witness_path=WITNESS,
        diagnostic_receipt_path=RECEIPT,
        diagnostic_png_path=PNG,
    )
    digest = write_new_safety_receipt(output, report, allowed_root=OUTPUT_ROOT)
    print(json.dumps({"receipt_path": str(output), "receipt_sha256": digest, **report}, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
