"""Command-line compiler witness for Primus Stage 2 world programs.

Runs the real ChronoSophia compiler against a Stage 2 dataset and writes a
hash-bound witness report. The destination must not already exist.

This command proves compiler acceptance and Primus envelope integrity. It does
not render, and it makes no visual-correctness claim.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_compile.witness import (  # noqa: E402
    load_programs,
    witness_dataset,
    write_witness_report,
)

DEFAULT_COMPILER = r"C:\chronos2\target\release\chronos.exe"
DEFAULT_LEDGER = r"C:\chronos2\data\capability_ledger.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Witness Stage 2 world programs through the real ChronoSophia "
            "compiler. The output directory must not already exist."
        )
    )
    parser.add_argument("--dataset", required=True, help="Stage 2 JSONL path")
    parser.add_argument("--output", required=True, help="New output directory")
    parser.add_argument("--compiler", default=DEFAULT_COMPILER)
    parser.add_argument("--ledger", default=DEFAULT_LEDGER)
    parser.add_argument(
        "--workdir",
        required=True,
        help="Scratch directory for emitted S3V artifacts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    programs = load_programs(args.dataset)
    report = witness_dataset(
        programs,
        compiler_exe=args.compiler,
        ledger_path=args.ledger,
        workdir=args.workdir,
    )
    path = write_witness_report(report, args.output)
    summary = {
        "report": str(path),
        "program_count": len(report.receipts),
        "witnessed_count": report.witnessed_count,
        "capability_executable_count": report.executable_count,
        "failure_histogram": report.failure_histogram(),
        "compiler_present": report.compiler_present,
        "render_observed": False,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
