"""
Fail-hard tests for NeuroCognica Sleep Architecture v0.1.

These prove Forever Law sealing, saturation, NREM/REM/VALIDATE mechanics,
and that dream candidates cannot silently become canonical memory.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.config import SovereignConfig, SystemState
from lifecycles.circadian_controller import CircadianController
from lifecycles.sleep_architecture import SleepArchitecture
from memory.canonical import CanonicalMemory
from memory.forever_law import ForeverLawCodex, compute_merkle_root
from memory.saturation import SaturationMonitor
from memory.steb import Episode, STEB
from substrate.model import CCFSubstrate


def tiny_config(data_root: str) -> SovereignConfig:
    return SovereignConfig(
        MODEL_DIM=32,
        STATE_DIM=16,
        NUM_LAYERS=1,
        VOCAB_SIZE=64,
        MAMBA_D_STATE=4,
        MAMBA_D_CONV=2,
        MAMBA_EXPAND=1,
        MAMBA_DROPOUT=0.0,
        HRR_DIM=32,
        GALORE_RANK=4,
        SLEEP_LEARNING_RATE=1e-3,
        HEBBIAN_LEARNING_RATE=1e-3,
        MIN_SURPRISE_THRESHOLD=0.1,
        IDLE_TIMEOUT_MINUTES=0,
        NREM_EPOCHS=1,
        NREM_KEEP_FRACTION=1.0,
        NREM_FAST_WEIGHT_DECAY=0.5,
        REM_MAX_CANDIDATES=2,
        REM_GENERATE_TOKENS=4,
        REM_MAX_SEED_TOKENS=8,
        VALIDATE_PROMOTE_THRESHOLD=0.0,  # allow promotions in tiny random model
        VALIDATE_REJECT_THRESHOLD=-1.0,
        VALIDATE_TRAIN_PROMOTED=False,
        SATURATION_SOFT_THRESHOLD=0.2,
        SATURATION_HARD_THRESHOLD=0.9,
        SATURATION_STEB_SOFT_FILL=0.25,
        STEB_MAX_EPISODES=16,
        DATA_ROOT=data_root,
    )


class ForeverLawTests(unittest.TestCase):
    def test_hash_chain_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            codex = ForeverLawCodex(Path(tmp) / "codex")
            a = codex.append("wake", "episodic_observation", {"n": 1}, layer=1)
            b = codex.append("wake", "episodic_observation", {"n": 2}, causation=[a.event_id])
            self.assertEqual(len(codex), 2)
            self.assertEqual(codex.events()[1].parent_hash, a.integrity_hash)
            report = codex.verify_full_chain()
            self.assertTrue(report.valid)

            # Tamper with first event payload on disk and reload.
            path = Path(tmp) / "codex" / "events.jsonl"
            lines = path.read_text(encoding="utf-8").splitlines()
            first = json.loads(lines[0])
            first["content"]["n"] = 999
            lines[0] = json.dumps(first)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            reloaded = ForeverLawCodex(Path(tmp) / "codex")
            bad = reloaded.verify_full_chain()
            self.assertFalse(bad.valid)
            self.assertGreaterEqual(bad.corrupted_count, 1)

    def test_merkle_boundary_seals_change_with_new_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            codex = ForeverLawCodex(Path(tmp) / "codex")
            t0 = codex.seal_boundary("T0")
            codex.append("wake", "episodic_observation", {"x": 1})
            t1 = codex.seal_boundary("T1")
            self.assertNotEqual(t0.merkle_root, t1.merkle_root)
            self.assertTrue(codex.verify_full_chain().valid)
            # Empty-domain root differs from populated roots.
            self.assertNotEqual(t1.merkle_root, compute_merkle_root([]))


class SleepArchitectureTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(0)
        self.tmp = tempfile.TemporaryDirectory()
        self.config = tiny_config(self.tmp.name)
        self.device = "cpu"
        self.mind = CCFSubstrate(self.config).to(self.device)
        self.steb = STEB(max_episodes=16, surprise_threshold=self.config.MIN_SURPRISE_THRESHOLD)
        self.codex = ForeverLawCodex(Path(self.tmp.name) / "forever_law")
        self.canonical = CanonicalMemory(Path(self.tmp.name) / "canonical")
        self.architecture = SleepArchitecture(
            config=self.config,
            mind=self.mind,
            steb=self.steb,
            codex=self.codex,
            canonical=self.canonical,
            saturation_monitor=SaturationMonitor(self.config),
            tokenizer=None,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _push_episode(self, tokens, surprise=1.0, text="ep"):
        ep = Episode(
            token_ids=torch.tensor(tokens, dtype=torch.long),
            surprise=surprise,
            timestamp=0.0,
            text=text,
        )
        self.assertTrue(self.steb.push(ep))
        self.architecture.record_wake_episode(ep, text=text)
        return ep

    def test_full_cycle_seals_and_clears_steb(self):
        self._push_episode([1, 2, 3, 4, 5], surprise=2.0, text="alpha")
        self._push_episode([5, 4, 3, 2, 1], surprise=2.5, text="beta")
        before = len(self.codex)
        report = self.architecture.run_cycle(force=False)
        self.assertTrue(report.nrem.success)
        self.assertTrue(report.rem.success)
        self.assertTrue(report.validate.success)
        self.assertTrue(report.integrity_valid)
        self.assertIsNotNone(report.t0)
        self.assertIsNotNone(report.t1)
        self.assertNotEqual(report.t0["merkle_root"], report.t1["merkle_root"])
        self.assertEqual(len(self.steb), 0)
        self.assertGreater(len(self.codex), before)
        # Every dream decision must be explicit.
        for candidate in report.candidates:
            self.assertIn(candidate["decision"], {"promoted", "rejected", "uncertain"})

    def test_dreams_do_not_silently_become_memory_without_validation_event(self):
        self._push_episode([1, 2, 3, 4], surprise=2.0)
        self._push_episode([2, 3, 4, 5], surprise=2.2)
        report = self.architecture.run_cycle(force=False)
        validation_events = [
            e for e in self.codex.events() if e.event_type == "dream_validation"
        ]
        self.assertEqual(len(validation_events), len(report.candidates))
        for event in validation_events:
            self.assertIn(event.content["decision"], {"promoted", "rejected", "uncertain"})

    def test_saturation_detects_fill_pressure(self):
        for i in range(8):
            self._push_episode([i + 1, i + 2, i + 3, i + 4], surprise=2.0 + i * 0.01)
        sat = self.architecture.measure_saturation()
        self.assertGreaterEqual(sat.steb_fill_ratio, 0.5)
        self.assertTrue(sat.should_sleep_soft)

    def test_circadian_controller_runs_architecture(self):
        self._push_episode([1, 2, 3, 4], surprise=3.0)
        heart = CircadianController(self.config, architecture=self.architecture)
        heart.attach(self.architecture)
        report = heart.run_sleep_cycle(force=False, reason="test")
        self.assertTrue(report.integrity_valid)
        self.assertEqual(heart.cycles_completed, 1)
        self.assertEqual(heart.current_state, SystemState.AWAKE)

    def test_rejected_dreams_are_not_canonical_promotions(self):
        # Force reject by making promote threshold unreachable.
        self.config.VALIDATE_PROMOTE_THRESHOLD = 1.1
        self.config.VALIDATE_REJECT_THRESHOLD = 1.0
        self._push_episode([1, 2, 3, 4, 5], surprise=2.0)
        self._push_episode([9, 8, 7, 6, 5], surprise=2.4)
        report = self.architecture.run_cycle(force=False)
        self.assertTrue(report.validate.success)
        self.assertGreaterEqual(len(report.candidates), 1)
        for candidate in report.candidates:
            self.assertEqual(candidate["decision"], "rejected")
        self.assertEqual(len(self.canonical.promoted()), 0)

    def test_codex_persists_and_reloads_with_valid_chain(self):
        self._push_episode([1, 2, 3, 4], surprise=2.0)
        self.architecture.run_cycle(force=False)
        path = Path(self.tmp.name) / "forever_law"
        before = len(self.codex)
        tip = self.codex.tip_hash
        reloaded = ForeverLawCodex(path)
        self.assertEqual(len(reloaded), before)
        self.assertEqual(reloaded.tip_hash, tip)
        self.assertTrue(reloaded.verify_full_chain().valid)

    def test_surprise_targets_next_token(self):
        tokens = torch.tensor([[1, 2, 3, 4]], dtype=torch.long)
        logits, _, surprise = self.mind(tokens, compute_surprise=True)
        self.assertEqual(surprise.shape, tokens.shape)
        # Position 0 is padded (no prediction target); later positions are real NLL.
        self.assertEqual(float(surprise[0, 0].item()), 0.0)
        self.assertGreater(float(surprise[0, 1:].mean().item()), 0.0)
        self.assertEqual(logits.shape[-1], self.config.VOCAB_SIZE)


class LegacyMVPRegressionTests(unittest.TestCase):
    def test_config_states_include_sleep_phases(self):
        self.assertEqual(SystemState.AWAKE.value, "AWAKE")
        self.assertEqual(SystemState.NREM.value, "NREM")
        self.assertEqual(SystemState.REM.value, "REM")
        self.assertEqual(SystemState.VALIDATE.value, "VALIDATE")
        # Legacy aliases resolve to the real phases.
        self.assertEqual(SystemState.DEEP_SLEEP, SystemState.NREM)
        self.assertEqual(SystemState.DREAMING, SystemState.REM)


if __name__ == "__main__":
    unittest.main(verbosity=2)
