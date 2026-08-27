from __future__ import annotations

import sys
import unittest
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from real_data.bridgedata_transitions import BridgeDataTransition  # noqa: E402
from train_bridgedata_real_transition import (  # noqa: E402
    BridgeDataResidualMLP,
    arrays_for_transitions,
    configure_seed,
    fit_train_only_normalization,
    model_predictions,
    train_residual_mlp,
)


def transition(index: int) -> BridgeDataTransition:
    state = tuple(float(index + dimension) / 10 for dimension in range(7))
    action = tuple(float((index % 3) + dimension) / 20 for dimension in range(7))
    delta = tuple(0.02 * (dimension + 1) + action[dimension] * 0.1 for dimension in range(7))
    return BridgeDataTransition(
        transition_id=f"fixture-{index}",
        episode_index=0,
        task_index=0,
        task="fixture",
        source_index=index,
        target_index=index + 1,
        source_frame_index=index,
        target_frame_index=index + 1,
        source_timestamp=index * 0.2,
        target_timestamp=(index + 1) * 0.2,
        state_t=state,
        action_t=action,
        state_t_plus_1=tuple(value + offset for value, offset in zip(state, delta)),
    )


class BridgeDataRealTransitionTrainerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transitions = tuple(transition(index) for index in range(12))

    def test_train_only_normalization_and_bounded_mlp_prediction(self):
        normalizer = fit_train_only_normalization(self.transitions)
        features, targets = arrays_for_transitions(self.transitions, normalizer)
        self.assertEqual(features.shape, (12, 14))
        self.assertEqual(targets.shape, (12, 7))
        self.assertEqual(normalizer.train_transition_ids, tuple(item.transition_id for item in self.transitions))

        configure_seed(31)
        model = BridgeDataResidualMLP(hidden_dimensions=16)
        result = train_residual_mlp(
            model,
            self.transitions,
            normalizer,
            seed=31,
            device=torch.device("cpu"),
            epochs=3,
            batch_size=4,
            learning_rate=0.01,
            weight_decay=0.0,
        )
        predictions = model_predictions(
            model,
            self.transitions,
            normalizer,
            device=torch.device("cpu"),
        )

        self.assertEqual(result["updates"], 9)
        self.assertGreaterEqual(result["first_batch_loss"], 0.0)
        self.assertGreaterEqual(result["last_batch_loss"], 0.0)
        self.assertEqual(set(predictions), {item.transition_id for item in self.transitions})
        self.assertTrue(
            all(
                len(prediction.state_t_plus_1) == 7
                and all(torch.isfinite(torch.tensor(prediction.state_t_plus_1)))
                for prediction in predictions.values()
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
