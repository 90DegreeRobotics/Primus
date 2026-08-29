# Handoff — Phase 0 Geometry Forward-Model Trainer

**Date:** 2026-08-29 CDT
**Agent lane:** Manus — Primus trainer
**Repositories:** `C:\Primus` and `C:\chronos2`
**Status:** **v2 intake and fixture-only trainer ready; no real-corpus training result is claimed.**

## Scope and Ownership

This unit implements the Manus lane in `task_2026-08-29_forward-model-sprint.md`.
It upgrades the Primus consumer to `geometry_program_corpus_v2`, defines a small
program-to-mesh-metric forward-model harness, and proves the harness against
explicitly marked v2 fixtures. The implementation touched only task-owned
Primus paths plus this paired handoff. Chronos2 was read, never modified except
for this matching handoff document.

No sampler, renderer, Blender process, port `9876`, corpus generator, no-recipe
guard source, installer, UI, BridgeData source, candidate parent, or promotion
surface was modified. No real corpus was trained on. No fixture result is
reported as a learning result.

## Tandem Baseline and Alignment

The active sprint order and the Lane A corpus handoff were SHA-256-identical in
both repositories before implementation. The pre-edit branches were clean:

| Repository | Start commit | Start upstream | Role during this unit |
|---|---|---|---|
| `C:\Primus` | `9e74bee361a912c013b7b50bfe53747ec76b46f2` | Same | Learner intake and trainer implementation |
| `C:\chronos2` | `f1deb8518b6a020ef4e5d4d3817d9ed128925f28` | Same | Read-only source of the real v2 corpus contract |

The real `seed_777` corpus in Chronos2 had `23` records and manifest pins for
`geometry_program_corpus_v2`; its corpus SHA-256 was
`c8e37449dd592b59649d7ffd672fccdafa87064b4da331ffb9c61a8817484c9f`.

## Factual Implementation Commit

| Signal | Value |
|---|---|
| Primus implementation commit | `e4b9518d37d0285424a9ea95749d6b0926cec01a` |
| Commit subject | `feat(geometry-phase0): add v2 forward trainer` |
| Primus implementation upstream after push | `e4b9518d37d0285424a9ea95749d6b0926cec01a` |
| Chronos2 code changes | None; it remains the read-only corpus producer in this lane. |

## Files Changed in Primus

| Path | Change |
|---|---|
| `CCF_Sovereign/src/geometry_corpus/__init__.py` | Exposes the v2 intake and complete target-vector interface. |
| `CCF_Sovereign/src/geometry_corpus/intake.py` | Accepts only v2 records; verifies JSONL/split/schema hashes; rejects forbidden keys; and derives structure from `program.steps` rather than trusting copied metadata. |
| `CCF_Sovereign/src/geometry_corpus/baselines.py` | Evaluates all three declared baselines over the expanded v2 target vector, separated by structural holdout. |
| `CCF_Sovereign/test_geometry_corpus.py` | Replaces the v1 fixture with a marked v2 fixture and covers hashes, structural derivation, split properties, and full baseline output. |
| `CCF_Sovereign/train_geometry_phase0.py` | Implements a small normalized MLP, frozen input receipt, atomic candidate manifest/checkpoint, and no-promotion policy. |
| `CCF_Sovereign/test_train_geometry_phase0.py` | Tests fixture candidate isolation, hash pinning, rejection-by-default, and view-score non-use. |

## V2 Input and Target Discipline

The consumer now requires v2 mesh fields: `vert_count`, `edge_count`,
`face_count`, `tri_count`, `loose_part_count`, the three bounding-box vectors,
`surface_area_mm2`, `volume_mm3`, and `is_closed`. It validates that
`step_count`, `op_mix`, and `op_signature` are re-derived from the ordered v2
`program.steps` operations. A copied structural record that disagrees with the
program is refused.

The Phase 0 model consumes numerical properties derived from `program` and
`program_structure` only: step count, per-operation counts, and aggregated
numeric program parameters. It predicts the complete v2 mesh target vector,
with per-feature standardization calculated from the training partition. The
loss never sees raw-scale dominance from large metrics such as volume.

`view_score` is intentionally outside the feature and target builders and does
not decide eligibility. The regression suite creates two otherwise identical
v2 corpora whose scores differ by `1000`; their training features, targets,
model metrics, and declared baseline metrics must remain exactly equal. This
test fails if score becomes a target or a filter.

## Candidate Lifecycle

`run_phase0_training()` is the real-corpus-ready entry point. It creates only a
new child directory under the supplied output root, writes a `created` manifest
atomically, verifies frozen corpus/manifest/split/schema inputs, records the
code and trainer hashes, runs only in the child directory, atomically saves the
checkpoint, then records the `evaluated` state and split-separated metrics.

The manifest records `promotion.state: rejected_by_default` and
`promotion.permitted: false`; the trainer has no promotion operation.
`run_fixture_training()` is the test-only wrapper. It requires `_fixture_` in
all three input filenames and records `fixture_only: true` with the explicit
note that fixture execution proves the harness executes and is never a learning
result.

## Commands Run and Actual Results

| Command | Actual result |
|---|---|
| `python test_no_recipe_guard.py` | Passed: `5` tests in `0.091s`. |
| `python test_geometry_corpus.py` | Passed: `8` tests in `2.791s`. |
| `python test_train_geometry_phase0.py` | Passed: `3` tests in `2.614s`. |
| `python -m py_compile ...` over the intake, baselines, trainer, and tests | Passed with no output. |
| Non-training load of `C:\chronos2\out\geometry_corpus\seed_777` | Passed: v2, `23` records, `train=15`, `held_out_length=3`, `held_out_op_combo=5`, and `33` declared baseline reports. |
| `git diff --cached --check` | Passed before the implementation commit. |
| `git pull --rebase origin main` before Primus implementation push | Passed: current branch already up to date. |
| `git push origin main` for Primus implementation commit | Pushed `9e74bee..e4b9518`. |

The non-training real-corpus check verifies contract compatibility and baseline
plumbing only. It is not a model run, optimization result, generalization
result, capability result, or promotion decision.

## Not Run and Remaining Boundaries

No real-corpus training, persistent background job, real candidate creation,
promotion, parent-checkpoint comparison, full Primus suite, full Chronos2
workspace suite, Blender or renderer execution, installer operation, or product
claim was run in this lane. The `600`-sample corpus was not used because it did
not have a completed manifest in the Lane A handoff; the verified `seed_777`
corpus was loaded only for a non-training contract check.

Before any real training claim, use `run_phase0_training()` with a real frozen
v2 corpus, an isolated output root, and a unique candidate ID. Preserve the
initial manifest and input hashes, corroborate process state during execution,
and report per-metric errors for both structural holdouts together with all
three declared baselines. A passing process, decreasing loss, or a fixture run
alone is not sufficient evidence of learning, generalization, capability, or
promotion.
