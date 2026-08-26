"""
Fail-hard component tests for the CCF prototype + Sleep Architecture wiring.

These tests prove component behavior only. They do not certify neuromorphic hardware.
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from core.config import SovereignConfig, SystemState
from lifecycles.circadian_controller import CircadianController
from lifecycles.sleep_architecture import SleepArchitecture
from memory.canonical import CanonicalMemory
from memory.forever_law import ForeverLawCodex
from memory.holographic import HolographicMemory
from memory.saturation import SaturationMonitor
from memory.steb import Episode, STEB
from substrate.model import CCFSubstrate
from substrate.tokenizer import SimpleTokenizer


def tiny_config(data_root: str = "data") -> SovereignConfig:
    return SovereignConfig(
        MODEL_DIM=32,
        STATE_DIM=16,
        NUM_LAYERS=1,
        VOCAB_SIZE=128,
        MAMBA_D_STATE=4,
        MAMBA_D_CONV=2,
        MAMBA_EXPAND=1,
        MAMBA_DROPOUT=0.0,
        HRR_DIM=32,
        GALORE_RANK=4,
        SLEEP_LEARNING_RATE=1e-4,
        MIN_SURPRISE_THRESHOLD=0.5,
        IDLE_TIMEOUT_MINUTES=0,
        NREM_EPOCHS=1,
        REM_MAX_CANDIDATES=1,
        REM_GENERATE_TOKENS=2,
        VALIDATE_TRAIN_PROMOTED=False,
        DATA_ROOT=data_root,
    )


class CCFMVPComponentTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(0)

    def test_config_defaults_are_sane(self):
        config = SovereignConfig()
        self.assertGreater(config.MODEL_DIM, 0)
        self.assertGreater(config.STATE_DIM, 0)
        self.assertGreater(config.VOCAB_SIZE, 0)
        self.assertEqual(SystemState.AWAKE.value, "AWAKE")
        self.assertEqual(SystemState.NREM.value, "NREM")

    def test_tokenizer_fallback_round_trip_without_hf_dependency(self):
        with patch.dict(sys.modules, {"transformers": None}):
            tokenizer = SimpleTokenizer()
        encoded = tokenizer.encode("Hello")
        decoded = tokenizer.decode(encoded)
        self.assertIsInstance(encoded, torch.Tensor)
        self.assertEqual(encoded.dtype, torch.long)
        self.assertEqual(decoded, "Hello")

    def test_steb_stores_only_high_surprise_episodes(self):
        steb = STEB(max_episodes=3, surprise_threshold=2.5)
        low = Episode(token_ids=torch.tensor([1, 2]), surprise=1.0, timestamp=0.0)
        high = Episode(token_ids=torch.tensor([3, 4]), surprise=3.0, timestamp=1.0)
        steb.push(low)
        self.assertEqual(len(steb), 0)
        steb.push(high)
        self.assertEqual(len(steb), 1)
        self.assertEqual(steb.sample_batch(batch_size=8)[0].surprise, 3.0)

    def test_holographic_identity_key_round_trip(self):
        key = torch.zeros(16)
        key[0] = 1.0
        value = torch.linspace(-1.0, 1.0, 16)
        bound = HolographicMemory.bind(key, value)
        unbound = HolographicMemory.unbind(bound, key)
        self.assertTrue(torch.allclose(bound, value, atol=1e-6))
        self.assertTrue(torch.allclose(unbound, value, atol=1e-6))

    def test_substrate_forward_uses_tiny_cpu_config(self):
        config = tiny_config()
        model = CCFSubstrate(config).to("cpu")
        tokens = torch.randint(0, config.VOCAB_SIZE, (1, 5), dtype=torch.long)
        logits, field_state, surprise = model(tokens)
        self.assertEqual(tuple(logits.shape), (1, 5, config.VOCAB_SIZE))
        self.assertEqual(tuple(field_state.shape), (1, config.STATE_DIM))
        self.assertEqual(tuple(surprise.shape), (1, 5))
        self.assertTrue(torch.isfinite(logits).all())
        self.assertTrue(torch.isfinite(field_state).all())
        self.assertTrue(torch.isfinite(surprise).all())

    def test_circadian_sleep_consolidation_clears_valid_steb(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = tiny_config(tmp)
            model = CCFSubstrate(config).to("cpu")
            steb = STEB(max_episodes=2, surprise_threshold=config.MIN_SURPRISE_THRESHOLD)
            steb.push(Episode(
                token_ids=torch.tensor([1, 2, 3, 4], dtype=torch.long),
                surprise=1.0,
                timestamp=0.0,
                text="fixture",
            ))
            architecture = SleepArchitecture(
                config=config,
                mind=model,
                steb=steb,
                codex=ForeverLawCodex(Path(tmp) / "forever_law"),
                canonical=CanonicalMemory(Path(tmp) / "canonical"),
                saturation_monitor=SaturationMonitor(config),
            )
            # Bind Forever Law ID like the runtime does.
            architecture.record_wake_episode(list(steb.buffer)[0], text="fixture")

            controller = CircadianController(config, architecture=architecture)
            controller.attach(architecture)
            consolidated = controller._initiate_sleep_protocol()

            self.assertTrue(consolidated)
            self.assertEqual(len(steb), 0)
            self.assertTrue(architecture.codex.verify_full_chain().valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
