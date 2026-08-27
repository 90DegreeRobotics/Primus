# Plan — temporal state witness and contextual generated dynamics

**Created:** 2026-08-27 07:32 CDT
**Owner:** Manus, under Michael Holt’s autonomous-progress directive
**Repository:** `C:\Primus` / `main`
**Status:** ACTIVE — documentation correction is pushed and the temporal witness implementation passed the complete 54-test matrix; code commit and contextual dataset generation remain

## Goal

Correct the stale world-schema documentation that says synthetic trajectories have not been ingested or evaluated as model predictions. Then add an explicit, hash-bound sidecar temporal-state witness derived from typed Stage 2 programs. The new generator revision will make its declared action outcomes depend on safe pre-action context and action intent rather than independent random deltas. A future candidate will receive only pre-state, action-intent, and context features; it will not receive a final translation, action delta, target relations, partition label, program ID, evidence URI, or source hash as an input.

The result remains a generated benchmark. It must not be described as observed physical dynamics, visual grounding, renderer correctness, or a general learned-world result.

## Why this is needed

The completed positive control proved only that an isolated candidate can consume a manifest-bound Stage 2 dataset and learn an exposed coordinate-addition target. It deliberately included the action delta as a feature, so a linear regressor reached complete accuracy across held-out partitions. That was a useful pipeline check but not a nontrivial dynamics test.

The existing `WorldProgram` encodes typed frames and operations, but not complete per-frame state snapshots. A backward-compatible sidecar witness can carry explicit generated pre-state, action-context, and post-state evidence while retaining the original program as the canonical schema/compiler payload. Its target must be rederived and verified from the program’s declared `SET_TRANSFORM` and relation operations.

## Files to read

- [x] `AGENTS.md`, Charter, current Git status, active-process baseline, and latest Wave 3 correction
- [x] `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`
- [x] `CCF_Sovereign/src/world_schema/model.py`
- [x] `CCF_Sovereign/src/world_schema/trajectory_generator.py`
- [x] `CCF_Sovereign/src/world_schema/tokens.py`
- [x] `CCF_Sovereign/src/world_compile/witness.py`
- [x] `CCF_Sovereign/src/world_data/ingestion.py`
- [x] `CCF_Sovereign/src/world_data/transitions.py`
- [x] Existing generator and schema test fixtures that assert operation/frame structure

## Files to edit or add

- [x] `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md` — corrected stale ingestion/prediction statement and retained the narrow positive-control boundary in pushed commit `69982abe9e8f51edaf4bff4259b03e834bc913a3`
- [x] `CCF_Sovereign/src/world_schema/trajectory_generator.py` — generator v1.1 derives declared generated action outcomes from safe context/action intent
- [x] `CCF_Sovereign/src/world_data/temporal_witness.py` — derives and validates generated temporal pre-state/context/post-state witnesses from manifest-bound records
- [x] `CCF_Sovereign/src/world_data/__init__.py` — narrow temporal witness exports only
- [x] `CCF_Sovereign/test_world_trajectory_generator.py` and compatibility tests — validated deterministic contextual action effects
- [x] `CCF_Sovereign/test_temporal_state_witness.py` — fail-hard target rederivation, direct-target feature exclusion, whole-family split, and relation-history tests
- [ ] `plan_2026-08-27_0732_temporal-state-witness.md` and final `handoff_manus_2026-08-27_temporal-state-witness.md`

No changes to parent/frozen checkpoints, candidate artifacts, raw Council corpus, `chronos2`, external compiler state, renderer output, or foreign-agent files are allowed. All generated datasets and candidates stay ignored and local.

## Explicit contextual generated rule

For each program, the generator exposes an action intent and safe pre-action context through existing generated program fields: geometry extent, bevel amount, variant, material metallic/roughness values, and the initial subject transform. It derives the declared action delta and target relation operations from those values by a deterministic rule. The sidecar witness records the pre-state at tick 0, the action context at tick 1, and the target state at tick 2.

The temporal-witness feature contract will include only pre-state values and action-context values. It will exclude the declared `SET_TRANSFORM` delta, end-camera transform, target translation, final relation booleans, whole-family split labels, object classes, operation-family labels, program IDs, source hashes, and evidence URIs. Feature-name tests enforce this exclusion. The target remains labeled `generated`/`inferred` only.

## Ordered work

- [x] Replace only the stale sentence in `WORLD_SCHEMA_V1.md` with a truthful summary of the completed positive control and its explicit limits. The audited documentation correction is pushed in `69982abe9e8f51edaf4bff4259b03e834bc913a3`.
- [x] Implement context-dependent generated action deltas and optional relation transitions in the deterministic trajectory generator. Outputs remain canonical, valid, round-trippable, deterministic, and partitioned.
- [x] Implement a sidecar temporal witness that proves its target exactly matches the source program’s pre-state plus declared action/result operations, and that all required whole-family splits are present.
- [x] Add fail-hard tests for derivation, integrity, target leakage exclusions, and changed relation operations. The complete gate passed: compile plus 54 tests across schema, generator, ingestion, existing/new metrics, candidate safety, the original positive-control runner, and temporal witness.
- [ ] Update this plan with final commit evidence; audit it for whitespace and prohibited unresolved markers; commit and push only the owned code/tests/docs/plan.
- [ ] Generate a fresh ignored contextual dataset under a unique path. Inspect its manifest, holdout distribution, action-outcome distribution, structural diversity, witness hashes, and source integrity.
- [ ] Only after the prior code is clean and pushed, write a separate bounded candidate plan. It must use a nonlinear model, never direct target-delta features, score every split separately against an explicit baseline, preserve no-promotion, and terminate safely on any integrity or numerical failure.

## Test gate

```powershell
cd C:\Primus\CCF_Sovereign
python -m compileall -q src\world_schema src\world_data generate_world_trajectories.py
python test_world_schema.py
python test_world_trajectory_generator.py
python test_world_ingestion.py
python test_world_transition_examples.py
python test_temporal_state_witness.py
```

Before a commit, all applicable gates must pass and cached whitespace must pass. Before any candidate, the Git worktree must be clean and synchronized; the unique source/destination paths must be absent; the parent/frozen SHA-256 must remain `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`; the dataset must ingest/witness cleanly; and no matching process may be active.

## Rollback and evidence rules

Never overwrite a dataset, candidate, checkpoint, manifest, temporary evidence record, or prior failed candidate. Do not retitle generated or inferred evidence as observed. Do not run the compiler/render stack merely to manufacture an observed label. Do not promote any candidate. If a generator, test, or candidate fails, preserve its unique output, record the reason, and choose a fresh identifier for a retry.

## Next-agent pickup notes

`50ac04e503e5f4ba241bb5e1552cdad94d60ec24` sealed the generated coordinate-addition positive control. `WORLD_SCHEMA_V1.md` presently contains a stale sentence that says Stage 2 fixtures have not been ingested/evaluated as predictions, despite the completed and documented generated positive-control candidate. Correct it narrowly; do not broaden the claim. The next technical action is the documentation correction, followed by the generator/witness implementation in this plan.
