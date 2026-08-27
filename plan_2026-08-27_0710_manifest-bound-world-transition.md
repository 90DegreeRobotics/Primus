# Plan — manifest-bound generated world-transition experiment

**Created:** 2026-08-27 07:10 CDT
**Owner:** Manus, under Michael Holt’s autonomous-progress directive
**Repository:** `C:\Primus` / `main`
**Status:** ACTIVE — code is pushed; first candidate attempt preserved as failed after checkpoint creation because final JSON receipt import was missing; corrected code requires focused re-gate and a fresh-ID retry

## Goal

Build the smallest end-to-end path that can test a real model against action-conditioned, **generated** WorldProgram transition targets under the existing whole-family holdouts. The experiment must bind a hash-verified Stage 2 dataset into an isolated candidate, learn only from the train partition, emit per-example predictions, and report train, held-out-object, held-out-operation, and held-out-composition metrics separately. It must compare against an explicit static baseline and retain non-promotion by default.

This is not an attempt to claim physical or observed dynamics. Current Stage 2 outcomes are generated/inferred from deterministic programs and no renderer or per-frame observed state snapshot exists. A passing experiment would therefore establish only **generated transition-rule learnability under the specified holdouts**.

## Problem framing and minimal target

The existing `WorldProgram` holds initial entity transforms plus an explicit `SET_TRANSFORM` action delta, then relation additions/removals. It does not carry complete per-frame state snapshots. The experiment will therefore derive an explicit, narrow supervised target from each validated program:

| Input available before target derivation | Generated target |
|---|---|
| Subject initial translation `(x, y, z)` | Subject next translation `(x + dx, y + dy, z + dz)` |
| `SET_TRANSFORM` action delta `(dx, dy, dz)` | Support relation absent after the declared removal |
| Operation sequence and initial relation identities | Near relation present after the declared addition |

The model receives only the stated input features. It must not receive canonical program bytes, final target values, held-out labels, source hashes, evidence URIs, or partition markers as features. Separate split labels are retained exclusively for evaluation and leakage checking.

The baseline is the static no-motion/no-relation-change predictor. It is expected to fail the generated transition task; that expectation is recorded in advance and must be measured rather than presumed.

## Files to read

- [x] `AGENTS.md`, Charter, current repository status, Wave 3 corrections, and latest handoffs
- [x] `CCF_Sovereign/src/world_schema/model.py`
- [x] `CCF_Sovereign/src/world_schema/trajectory_generator.py`
- [x] `CCF_Sovereign/src/world_data/ingestion.py`
- [x] `CCF_Sovereign/src/world_metrics/transition_metrics.py`
- [x] `CCF_Sovereign/train.py`, `training/candidate_run.py`, `src/substrate/model.py`, and `src/substrate/tokenizer.py`
- [ ] `CCF_Sovereign/generate_world_trajectories.py`, generator CLI configuration, candidate safety tests, evaluation manifest/compare contracts, and relevant package exports

## Files to edit or add

- [x] `CCF_Sovereign/src/world_data/transitions.py` — explicit generated transition-example derivation and split-safe input/target records
- [x] `CCF_Sovereign/src/world_data/__init__.py` — narrow exports only
- [x] `CCF_Sovereign/src/world_metrics/state_transitions.py` — typed per-split numeric and relation metrics; no pooled holdout score
- [x] `CCF_Sovereign/src/world_metrics/__init__.py` — narrow exports only
- [x] `CCF_Sovereign/training/candidate_run.py` — hash-bound additional frozen inputs without weakening current parent/corpus safeguards
- [x] `CCF_Sovereign/train_world_transition.py` — explicit isolated candidate CLI; generated-data label; deterministic small regressor; baseline and model prediction artifacts
- [x] Focused tests for data derivation, leakage, metrics, candidate evidence binding, and train-only fitting
- [ ] `plan_2026-08-27_0710_manifest-bound-world-transition.md` and final `handoff_manus_2026-08-27_manifest-bound-world-transition.md`

No `README.md`, `STATUS.md`, CCF root documentation, `chronos2`, parent/frozen checkpoints, raw Council corpus, or foreign agent path is edited by this unit. Any truth-surface change will be a `TRUTH-SURFACE REQUEST` in the handoff.

## Ordered work

- [x] Inspect the Stage 2 generator CLI and candidate/evaluation contracts; verify a larger explicit destination can be created without overwriting existing data.
- [x] Implement fail-closed transition-example derivation. It rejects absent/multiple move actions, ambiguous relations, malformed deltas, non-generated/inferred target labels, non-train inputs in a training set, and any caller that lacks an ingestion result.
- [x] Implement split-separated metrics with position RMSE, tolerance-bounded position accuracy, support/near relation accuracy, and complete-prediction coverage. No pooled held-out figure is calculated.
- [x] Implement an explicit isolated candidate CLI with a fixed low-capacity linear transition regressor and a static baseline. It binds code commit, frozen Stage 2 manifest, source dataset hashes, model configuration, output directory, input feature contract, and no-promotion policy into atomic local evidence.
- [x] Add fail-hard focused unit tests and run the preserved final test gate: compile passed and 41 tests passed across candidate safety (5), ingestion (11), existing world metrics (8), generator (7), generated examples (4), generated metrics (4), and runner (2).
- [ ] Generate a new ignored dataset using seed `20260827` and 256 train / 64 each held-out object, operation, and composition programs. Record its two source hashes and emitted split counts.
- [ ] Commit the verified code and plan using explicit pathspecs, push `main`, and verify exact remote synchronization before candidate creation.
- [ ] Recheck parent/frozen hashes, clean Git state, unique candidate/output paths, CUDA availability, candidate policy, and active process absence.
- [x] Generated the isolated Stage 2 source dataset at `CCF_Sovereign/tmp/world_transition_dataset_20260827_0710/`: 448 programs (256 train / 64 each protected split), JSONL SHA-256 `f30ba907c71d2c736aeb5e13c0e8a9a79e28d5e649c697dfceee1b5c79febbeb`, manifest SHA-256 `5da51ab06158cb655aef920e744e214875e369d1aa6346f402bdec10cac5fd43`, and 448/448 unique structural programs.
- [x] Pushed implementation commit `9daca8320c70ef88bbb18d58e82a0f993b1ec64d`; the repository was clean and synchronized before the candidate attempt.
- [ ] Train one bounded generated-transition candidate on the train partition only; run static-baseline and candidate predictions over every partition; write per-split metrics and no-promotion evidence. Attempt `world-transition-20260827-0710-linear` created its isolated checkpoint/report artifacts but then failed in final receipt printing due to missing `json` import; it is preserved as `failed` and must never be reused. The import correction requires re-gating, a code commit/push, and retrying once under fresh ID `world-transition-20260827-0725-linear`.
- [ ] Rehash parent/frozen artifacts, candidate checkpoint, prediction records, and metrics. Run the non-mutating promotion policy with no fabricated behavioral-comparison evidence, record its expected ineligible result, and write an audited handoff.

## Candidate and resource boundary

The initial candidate is deliberately small because it isolates a narrow arithmetic/relation transition target rather than language modeling or complete program reconstruction. It is not comparable to the 50M Council-corpus ladder and must not be advertised as such. Training stops if numerical instability occurs, candidate isolation fails, protected input hash drifts, holdout leakage is detected, GPU memory exceeds the safe cap, or a process/checkpoint artifact contradicts lifecycle evidence.

Candidate directories, generated datasets, checkpoint files, runtime logs, and result JSON remain ignored local artifacts. Expected candidate checkpoint scale is below 10 MB. The protected parent remains immutable at SHA-256 `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.

## Test gate

```powershell
cd C:\Primus\CCF_Sovereign
python -m compileall -q src\world_data src\world_metrics training\candidate_run.py train_world_transition.py
python test_world_ingestion.py
python test_transition_metrics.py
python test_world_trajectory_generator.py
python test_candidate_training.py
python test_world_transition_examples.py
python test_world_state_transition_metrics.py
python test_world_transition_candidate.py
```

Before a code commit, all relevant tests must pass and cached whitespace must pass. The preserved gate `CCF_Sovereign/tmp/manus_world_transition_gate_20260827_0710.log` records the passed compile command and 41 focused tests. Before candidate creation, the repository must be clean and synchronized, the dataset destination and candidate destination must be absent, the generated dataset must ingest cleanly, and parent/frozen hashes must equal the recorded value.

## Rollback path

Never reset, clean, force-push, amend a pushed commit, reuse a generated dataset or candidate ID, overwrite a checkpoint, or write a candidate over the parent. If any run fails, preserve its isolated dataset, candidate directory, manifest, logs, and output as evidence. Do not mark synthetic/generated targets as observed, and do not promote a candidate.

## Next-agent pickup notes

The previous Wave 3 50M Council-corpus diagnostic is complete and correctly framed as hardware/harness evidence. Codex’s correction `0dcc05d6179bcda5dea08f2ab1dc56a00080cec3` clarified that the 100-step diagnostic does not supersede the August 26 3,940-step 50M result. Two historic ladder manifests remain stale as `training` without matching processes; preserve them and do not repair them in this unit. The immediate next action is the first listed contract inspection.
