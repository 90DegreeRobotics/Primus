"""Command-line entry point for deterministic Stage 2 world trajectories."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_schema.trajectory_generator import (  # noqa: E402
    TrajectoryGeneratorConfig,
    write_dataset,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic, evidence-labeled Primus world-trajectory "
            "dataset. The destination must not already exist."
        )
    )
    parser.add_argument("--output", required=True, help="New output directory")
    parser.add_argument("--seed", type=int, default=20_260_826)
    parser.add_argument("--train-count", type=int, default=12)
    parser.add_argument("--held-out-object-count", type=int, default=3)
    parser.add_argument("--held-out-operation-count", type=int, default=3)
    parser.add_argument("--held-out-composition-count", type=int, default=3)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = TrajectoryGeneratorConfig(
        seed=args.seed,
        train_count=args.train_count,
        held_out_object_count=args.held_out_object_count,
        held_out_operation_count=args.held_out_operation_count,
        held_out_composition_count=args.held_out_composition_count,
    )
    receipt = write_dataset(args.output, config)
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
