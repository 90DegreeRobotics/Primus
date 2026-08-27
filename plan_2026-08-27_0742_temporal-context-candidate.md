# Plan — generated temporal-context candidate

**Created:** 2026-08-27 07:42 CDT
**Owner:** Manus, under Michael Holt’s autonomous-progress directive
**Repository:** `C:\Primus` / `main`
**Status:** ACTIVE — nonlinear runner and complete 57-test gate passed; audit, code commit, and fresh candidate execution remain

## Goal

Run one bounded isolated candidate that learns a **generated** action-conditioned temporal-state target from pre-state and safe geometry/material/action-intent context, without direct target-delta, target state, target relation, split, object class, operation family, program ID, source hash, or evidence URI input features. Train only the manifest-bound train partition and score every whole-family holdout separately against an explicit static baseline. Promotion remains disabled by default and no physical, observed, renderer, or general learned-world claim is allowed.

## Experiment contract

The source is a fresh deterministic Stage 2 generator v1.1 dataset. `TemporalStateWitness` derives the target from the source program’s typed operation history and verifies the full manifest-bound ingestion receipt. The trainable context vector is exactly:

```text
source_x_m, source_y_m, source_z_m,
geometry_extent_m, geometry_bevel_fraction, geometry_variant_fraction,
material_metallic_fraction, material_roughness_fraction
```

The output target is final subject `(x, y, z)` metres and final support/near relation booleans. A nonlinear MLP is chosen because the declared generator rule includes quotient, modulo, branch, and comparison structure. It is still intentionally small and must never be compared to the 50M Council-corpus ladder.

## Files to read

- [x] `AGENTS.md`, Charter, latest `STATUS.md`, current Git/process baseline
- [x] `CCF_Sovereign/src/world_data/temporal_witness.py`
- [x] `CCF_Sovereign/src/world_metrics/state_transitions.py`
- [x] `CCF_Sovereign/training/candidate_run.py`
- [x] `CCF_Sovereign/train_world_transition.py`
- [x] `CCF_Sovereign/src/promotion/gate.py`
- [x] Existing candidate runner and candidate-safety test patterns needed by the new runner

## Files to edit or add

- [x] `CCF_Sovereign/train_temporal_context.py` — explicit isolated candidate CLI, small nonlinear MLP, static baseline, per-split artifacts, no promotion
- [x] `CCF_Sovereign/test_temporal_context_candidate.py` — train-only, feature contract, exact output coverage, and metric regression tests
- [ ] `plan_2026-08-27_0742_temporal-context-candidate.md` and final `handoff_manus_2026-08-27_temporal-context-candidate.md`

No parent/frozen checkpoint, existing candidate, source dataset, raw Council corpus, external compiler state, renderer output, `chronos2`, or foreign file may be changed. Datasets, candidates, logs, temporary helpers, and checkpoints remain ignored and local.

## Ordered work

- [x] Implement the candidate runner using only `derive_temporal_witnesses(ingested)` and the declared context feature vector. It fails before output creation if the full ingestion receipt, feature boundary, or train-only partition check fails.
- [x] Add fail-hard focused tests. They verify exact prediction coverage, separate split reporting, direct delta/target feature exclusion, and train-only fitting rejection on split mixing.
- [x] Run and preserve the complete gate: compile plus 57 tests across schema, generator, ingestion, both transition metrics, both generated witness paths, candidate safety, and both candidate runners.
- [ ] Audit and push the runner/test/plan commit using explicit pathspecs. Recheck clean parity and parent hashes before any candidate creation.
- [ ] Generate a fresh ignored 448-program dataset using seed `20260827` and the 256/64/64/64 split contract. Derive its temporal witnesses, inspect holdout and relation-outcome distributions, and record both source hashes.
- [ ] Run one fresh-ID candidate with a bounded MLP, CUDA only if available, 300 epochs, batch size 16, and a fixed learning rate. Preserve baseline predictions, candidate predictions, split-separated metrics, candidate manifest, checkpoint, runtime log, and strict restore smoke.
- [ ] Rehash parent/frozen/candidate/evidence artifacts. Run a non-mutating promotion policy evaluation without fabricating any behavioral comparison. Update this plan and write an audited handoff before committing only documentation closure.

## Test gate

```powershell
cd C:\Primus\CCF_Sovereign
python -m compileall -q src\world_data src\world_metrics training\candidate_run.py train_temporal_context.py
python test_candidate_training.py
python test_world_ingestion.py
python test_world_state_transition_metrics.py
python test_temporal_state_witness.py
python test_temporal_context_candidate.py
```

Before candidate creation, `main` must be clean and synchronized; unique dataset/candidate/log paths must be absent; no matching process may be active; source parent and frozen hashes must match `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`; the source dataset must be generated fresh and ingested/witnessed successfully; and no policy permits promotion as a training side effect.

## Rollback and non-claims

Never reuse or overwrite an isolated candidate/dataset ID, force-push, reset, clean, amend a pushed commit, or promote a candidate. Any failed run remains an artifact with its error recorded. A successful score establishes only a synthetic generated-context task result. It does not establish observed dynamics, physical correctness, visual/render correctness, broad object intelligence, or a promotable parent replacement.

## Next-agent pickup notes

The direct-delta positive control is sealed at `50ac04e503e5f4ba241bb5e1552cdad94d60ec24`. The temporal witness/context rule is sealed at `7fbfcaa8e0f8c083329c3fb4733f05a91b948bd6`. Begin with the candidate runner only; do not make a candidate until its focused test gate is green and pushed.
