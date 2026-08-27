# Plan — temporal-context normalization ablation

**Created:** 2026-08-27 07:52 CDT
**Owner:** Manus, under Michael Holt’s autonomous-progress directive
**Repository:** `C:\Primus` / `main`
**Status:** EXECUTION COMPLETE — fixed-data normalized candidate and non-mutating ineligibility decision are recorded; documentation closure and final diagnosis remain

## Goal

Test one specific explanation for the completed temporal-context candidate’s low strict position accuracy: its MLP optimized raw position/context coordinates and raw positional targets together with binary relation logits. This ablation will normalize the eight allowed context features and the three positional target dimensions using statistics computed **only from the 256 train witnesses**. Relation targets remain binary logits. It will use the exact existing 448-program dataset, seed, 300 epochs, batch size, learning rate, MLP width, prediction metric, static baseline, and no-promotion policy.

The ablation changes numerical representation only. It must not alter the source programs, splits, feature names, feature exclusions, target construction, model capacity, training data size, optimizer, resource budget, evaluation rule, or protected artifacts. It remains a generated benchmark and must not be described as observed/physical dynamics or a learned-world result.

## Fixed evidence inputs

| Input | SHA-256 / reference |
|---|---|
| Contextual dataset JSONL | `3fbcedd9a7b5316945bec224d1ab09a59dcef4b5e5c4ff1d2ca22db59afbfb2a` |
| Contextual dataset manifest | `1ee427195a3922c9e51f56a48a87311f5b974a109f9a25a042b2406c3bd46a41` |
| Temporal witness set | `18a408d656b62a08029b76cfca25d8a4b0ee930e561ff84a64c76ad830cf5de8` |
| Baseline candidate | `temporal-context-20260827-0742-mlp` |
| Baseline candidate code | `b3891cc141eb7597f09523c85e4b5d35b5269230` |
| Parent and frozen parent | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |

## Files to read

- [x] `AGENTS.md`, Charter, baseline handoff, current Git/process/hash state
- [x] `CCF_Sovereign/train_temporal_context.py`
- [x] `CCF_Sovereign/src/world_data/temporal_witness.py`
- [x] `CCF_Sovereign/src/world_metrics/state_transitions.py`
- [x] `CCF_Sovereign/training/candidate_run.py`
- [x] Existing candidate, metric, and safety regression tests relevant to train-only normalization

## Files to add or edit

- [x] `CCF_Sovereign/src/world_data/normalization.py` — deterministic train-only normalization statistics and inverse target transform with finite/variance checks
- [x] `CCF_Sovereign/train_temporal_context_normalized.py` — explicit equal-budget isolated candidate runner; no raw target/inference leakage
- [x] `CCF_Sovereign/test_temporal_context_normalization.py` — train-only statistic, normalization/inversion, leakage, and finite checks
- [x] `CCF_Sovereign/test_temporal_context_normalized_candidate.py` — exact feature contract, train-only fitting, prediction coverage, and split reports
- [x] `plan_2026-08-27_0752_temporal-context-normalization-ablation.md` and final `handoff_manus_2026-08-27_temporal-context-normalization-ablation.md`

No code path may read held-out witnesses when fitting normalization statistics. No target delta, final target, relation target, partition, class, family, program ID, source hash, or evidence URI enters the model input tensor. No checkpoint promotion, parent/frozen mutation, candidate reuse, source artifact mutation, compiler/render invocation, raw corpus mutation, `chronos2` change, or foreign worktree edit is allowed.

## Ordered work

- [x] Implement immutable normalization statistics from a nonempty all-train witness collection. It requires finite means/scales and a stable positive floor for constant dimensions and emits exact forward/inverse transforms with a canonical SHA-256 receipt.
- [x] Implement an equal-budget candidate runner using the exact 8→32→32→5 MLP and hyperparameters of the underfit baseline. It normalizes inputs and position targets using the train-only receipt, passes relation targets unchanged, and persists normalization/fixed-data evidence in the manifest and run summary.
- [x] Add fail-hard tests and run the preserved complete gate: compile plus 61 tests across current schema/generator/ingestion/witness/metric/candidate contracts and the two new normalization suites.
- [x] Audit, commit, and push only the runner, normalization module, tests, and plan. Clean parity and unchanged parent/frozen hashes were verified in pushed commit `28f0e5b473661ed9ae519b362e8718c4e5e1edf5`.
- [x] Recheck the fixed source dataset and manifest hashes, candidate destination absence, GPU availability, policy/no-promotion, and no matching active process.
- [x] Execute fresh candidate `temporal-context-20260827-0752-normalized-mlp` with identical 300 epochs, batch 16, learning rate 0.01, hidden width 32, and 25-mm metric tolerance. It completed 4,800 updates in 20.921008399978746 seconds; baseline/model artifacts, restore smoke, and non-mutating promotion decision all completed.
- [x] Report train and protected-split results separately. Train-only normalization improved train strict accuracy from 0.0390625 to 0.0703125 and train RMSE from 72.1068 to 50.3891 mm, but worsened protected position RMSE in each split; it is insufficient for the generated contextual rule. The final handoff is written and needs documentation-only commit/push.

## Test gate

```powershell
cd C:\Primus\CCF_Sovereign
python -m compileall -q src\world_data src\world_metrics training\candidate_run.py train_temporal_context.py train_temporal_context_normalized.py
python test_world_schema.py
python test_world_trajectory_generator.py
python test_world_ingestion.py
python test_world_transition_examples.py
python test_world_state_transition_metrics.py
python test_transition_metrics.py
python test_temporal_state_witness.py
python test_candidate_training.py
python test_temporal_context_candidate.py
python test_temporal_context_normalization.py
python test_temporal_context_normalized_candidate.py
```

## Rollback and evidence rules

Never overwrite, delete, or reuse any candidate/dataset/output destination. Preserve any failed attempt and its log. Do not `reset`, force-push, clean, or amend pushed history. The normalization receipt is an artifact of the train partition only and must be written atomically. Promotion stays ineligible unless the existing policy is later satisfied with separately created behavioral comparison evidence and explicit authorization.

## Next-agent pickup notes

The baseline temporal-context candidate is sealed in `9a49b2dc6e903cd11464e2815c815025a67b4d5d`. It reduced position RMSE to 67.56–77.76 mm but only achieved 1.6%–6.3% strict complete-transition accuracy; train accuracy was also 3.9%. This plan isolates only scaling/normalization. If the normalized candidate remains underfit, next investigate function approximation or target rule structure. If it fits train but fails held-outs, record a genuine generalization limitation.
