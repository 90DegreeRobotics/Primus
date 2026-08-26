"""
Non-interactive smoke: ingest → saturate → full sealed sleep → verify.

Exit nonzero on any integrity or phase failure.
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.config import SovereignConfig
from lifecycles.circadian_controller import CircadianController
from lifecycles.sleep_architecture import SleepArchitecture
from memory.canonical import CanonicalMemory
from memory.forever_law import ForeverLawCodex
from memory.saturation import SaturationMonitor
from memory.steb import Episode, STEB
from substrate.model import CCFSubstrate


def main() -> int:
    torch.manual_seed(7)
    with tempfile.TemporaryDirectory() as tmp:
        config = SovereignConfig.operator()
        config.DATA_ROOT = tmp
        config.MODEL_DIM = 64
        config.STATE_DIM = 32
        config.NUM_LAYERS = 1
        config.VOCAB_SIZE = 128
        config.HRR_DIM = 64
        config.MIN_SURPRISE_THRESHOLD = 0.01
        config.NREM_EPOCHS = 1
        config.REM_MAX_CANDIDATES = 2
        config.REM_GENERATE_TOKENS = 6
        config.VALIDATE_TRAIN_PROMOTED = False
        config.STEB_MAX_EPISODES = 32
        config.SATURATION_SOFT_THRESHOLD = 0.15
        config.SATURATION_STEB_SOFT_FILL = 0.2

        mind = CCFSubstrate(config)
        steb = STEB(max_episodes=config.STEB_MAX_EPISODES, surprise_threshold=0.01)
        codex = ForeverLawCodex(Path(tmp) / "forever_law")
        canonical = CanonicalMemory(Path(tmp) / "canonical")
        architecture = SleepArchitecture(
            config=config,
            mind=mind,
            steb=steb,
            codex=codex,
            canonical=canonical,
            saturation_monitor=SaturationMonitor(config),
        )
        heart = CircadianController(config, architecture=architecture)
        heart.attach(architecture)

        for i in range(6):
            tokens = torch.arange(1 + i, 9 + i, dtype=torch.long) % (config.VOCAB_SIZE - 1) + 1
            ep = Episode(
                token_ids=tokens,
                surprise=2.0 + i * 0.1,
                timestamp=time.time(),
                text=f"smoke-{i}",
            )
            assert steb.push(ep)
            architecture.record_wake_episode(ep, text=ep.text)

        sat = architecture.measure_saturation()
        report = heart.run_sleep_cycle(force=False, reason="smoke")
        integrity = codex.verify_full_chain()

        payload = {
            "saturation": sat.to_dict(),
            "nrem_success": report.nrem.success,
            "rem_success": report.rem.success,
            "validate_success": report.validate.success,
            "integrity_valid": integrity.valid,
            "events": len(codex),
            "t0": report.t0,
            "t1": report.t1,
            "candidates": report.candidates,
            "canonical_beliefs": len(canonical),
        }
        print(json.dumps(payload, indent=2))

        if not report.nrem.success:
            print("FAIL: NREM", file=sys.stderr)
            return 2
        if not report.rem.success:
            print("FAIL: REM", file=sys.stderr)
            return 3
        if not report.validate.success:
            print("FAIL: VALIDATE", file=sys.stderr)
            return 4
        if not integrity.valid:
            print("FAIL: integrity", file=sys.stderr)
            return 5
        if report.t0 is None or report.t1 is None:
            print("FAIL: missing seals", file=sys.stderr)
            return 6
        if report.t0["merkle_root"] == report.t1["merkle_root"]:
            print("FAIL: T0 == T1 (expected chain growth)", file=sys.stderr)
            return 7
        print("SMOKE OK")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
