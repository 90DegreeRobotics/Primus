# Plan — generated temporal-context candidate

**Created:** 2026-08-27 07:42 CDT
**Owner:** Manus, under Michael Holt’s autonomous-progress directive
**Repository:** `C:\Primus` / `main`
**Status:** EXECUTION COMPLETE — contextual candidate result, restore smoke, and non-mutating ineligibility decision are recorded; documentation closure and final delivery remain

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
- [x] `plan_2026-08-27_0742_temporal-context-candidate.md` and final `handoff_manus_2026-08-27_temporal-context-candidate.md`

No parent/frozen checkpoint, existing candidate, source dataset, raw Council corpus, external compiler state, renderer output, `chronos2`, or foreign file may be changed. Datasets, candidates, logs, temporary helpers, and checkpoints remain ignored and local.

## Ordered work

- [x] Implement the candidate runner using only `derive_temporal_witnesses(ingested)` and the declared context feature vector. It fails before output creation if the full ingestion receipt, feature boundary, or train-only partition check fails.
- [x] Add fail-hard focused tests. They verify exact prediction coverage, separate split reporting, direct delta/target feature exclusion, and train-only fitting rejection on split mixing.
- [x] Run and preserve the complete gate: compile plus 57 tests across schema, generator, ingestion, both transition metrics, both generated witness paths, candidate safety, and both candidate runners.
- [x] Audit and push the runner/test/plan commit using explicit pathspecs. Recheck clean parity and parent hashes before any candidate creation. Runner commit `b3891cc141eb7597f09523c85e4b5d35b5269230` was pushed and synchronized.
- [x] Generate a fresh ignored 448-program dataset using seed `20260827` and the 256/64/64/64 split contract. The JSONL SHA-256 is `3fbcedd9a7b5316945bec224d1ab09a59dcef4b5e5c4ff1d2ca22db59afbfb2a`; the manifest SHA-256 is `1ee427195a3922c9e51f56a48a87311f5b974a109f9a25a042b2406c3bd46a41`; the temporal witness set is `18a408d656b62a08029b76cfca25d8a4b0ee930e561ff84a64c76ad830cf5de8`.
- [x] Run one fresh-ID candidate with a bounded MLP, CUDA only if available, 300 epochs, batch size 16, and a fixed learning rate. Candidate `temporal-context-20260827-0742-mlp` completed 4,800 updates in 20.792273499973817 seconds. Its complete transition accuracy was 0.0390625 on train and 0.0625, 0.015625, and 0.03125 across held-out object, operation, and composition; it is an underfit generated-context result, not a learned-world claim.
- [x] Rehash parent/frozen/candidate/evidence artifacts. Run a non-mutating promotion policy evaluation without fabricating any behavioral comparison. The checkpoint is `96a4f511757754f3a3be2b00b982ed49e675d05882fd692c0f9397e133b299a2`; parent/frozen remain `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`; restore smoke passed; the policy decision is ineligible and non-mutating. The final handoff is written and needs documentation-only commit/push.

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
