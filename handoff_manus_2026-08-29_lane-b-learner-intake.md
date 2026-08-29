# Handoff — Lane B Learner Intake

**Date:** 2026-08-29 CDT
**Lane:** B — Learner Intake
**Repository:** `C:\Primus`
**Status:** **Implementation and focused gate complete; global clean-tree closure awaits Lane C's concurrent untracked file.**

## Scope and Boundary

This handoff records the learner-side consumer for the frozen
`geometry_program_corpus_v1` contract defined in
`plan_2026-08-29_0603_multi-lane-no-recipe-build.md` (§5 and §7). The work
implements **only** the Lane B paths in `C:\Primus`; it does not generate a
corpus, invoke Blender, train a model, create a candidate, or modify
BridgeData, `src/real_data`, the synthetic trajectory generator, product code,
or shared truth surfaces.

The only test data is constructed in `TemporaryDirectory` under test-controlled
filenames containing `_fixture_`. Each fixture-writing and fixture-loading test
asserts that marker. It is test plumbing, never a corpus, result, training
input, or evidence of geometry capability.

## Start and Factual Implementation Commit

| Signal | Value |
|---|---|
| Start commit | `baa88807b609d152905638dfdc95611038dbb20c` |
| Start upstream | `baa88807b609d152905638dfdc95611038dbb20c` |
| Factual implementation commit | `497935fa3c89d1533dbff3e67c1e72a60b6b2f70` |
| Commit subject | `feat(geometry-corpus): add frozen structural intake` |
| Upstream after implementation push | `497935fa3c89d1533dbff3e67c1e72a60b6b2f70` |
| Protected model/checkpoint activity | None; no model or candidate was created or touched. |

## Files Added

| Path | Purpose |
|---|---|
| `CCF_Sovereign/src/geometry_corpus/__init__.py` | Restrained public API for the frozen intake and declared baseline evaluation. |
| `CCF_Sovereign/src/geometry_corpus/intake.py` | Fail-closed JSONL contract validation, SHA-256 pinning, structural split definition, and evaluation-time re-verification. |
| `CCF_Sovereign/src/geometry_corpus/baselines.py` | The three Phase 0 baselines, evaluated separately on each structural holdout. |
| `CCF_Sovereign/test_geometry_corpus.py` | Fixture-marked tests for schema intake, hash refusal, structural split properties, and baseline output. |

## Implemented Contract

The intake accepts only records whose `schema_version` equals
`geometry_program_corpus_v1`. It validates canonical `sample_id` hashes of
program JSON and rejects every forbidden noun-bearing key at every nested depth:
`class`, `object_class`, `label`, `name`, `brief`, `prompt`, `category`,
`family`, `noun`, and `kind_name`.

The manifest pins SHA-256 values for the corpus JSONL, split definition, and
schema-version string. Loading refuses a missing file or mismatch. The
`GeometryCorpusIntake.verify()` method recomputes all pins, including the loaded
manifest's own immutable receipt hash, and `evaluate_declared_baselines()` calls
that verification before it calculates any metric.

Structural membership is computed from `program_structure` only. The supported
holdouts are `held_out_length` and `held_out_op_combo`; an operation-combination
holdout takes precedence if both conditions match, so each sample belongs to
exactly one partition. The implementation refuses a split that leaves any of
`train`, `held_out_length`, or `held_out_op_combo` empty, and refuses any
operation signature shared by `train` and `held_out_op_combo`.

The declared baseline registry is fixed before training:

| Baseline | Prediction rule |
|---|---|
| `training_mean` | Per-metric mean of the training partition. |
| `step_count_only` | Mean for the training records at the same `step_count`, with the training mean only when that count is absent. |
| `op_mix_nearest_neighbour` | Target metric from the training record with the smallest operation-count distance; sample ID breaks ties deterministically. |

Each baseline produces MAE and RMSE for `vert_count` and `face_count` separately
for `held_out_length` and `held_out_op_combo`. This is **baseline plumbing, not a
learned result**. No claim has been made that any model beats a baseline.

## Commands Run and Actual Results

| Command | Actual result |
|---|---|
| `git pull --rebase origin main` before work | `Already up to date.` at `baa88807b609d152905638dfdc95611038dbb20c`. |
| `python test_geometry_corpus.py` | Passed twice: initially `5` tests, then `6` tests after split/schema failure coverage was added. Final run: `Ran 6 tests in 0.360s`, `OK`. |
| `python -m py_compile src\geometry_corpus\__init__.py src\geometry_corpus\intake.py src\geometry_corpus\baselines.py test_geometry_corpus.py` | Passed with no output. |
| `git diff --cached --check` | Passed before the factual implementation commit. |
| `git pull --rebase origin main` before push | `Current branch main is up to date.` |
| `git push origin main` | Pushed `baa8880..497935f` to `origin/main`. |

The final focused test proves that the fixture intake is hash pinned and
noun-free, nested forbidden keys fail even when the altered fixture's hashes are
otherwise internally matching, corpus tampering fails at load and again before
baseline evaluation, split and schema pin mismatches fail, structural partitions
are disjoint and program-payload-independent, and all three baseline families
emit metrics for both holdouts.

## Concurrent-Lane Boundary

The pre-edit worktree was clean and no Lane B package existed. During Lane B
implementation, `CCF_Sovereign/test_no_recipe_guard.py` appeared as an untracked
file. That path belongs exclusively to Lane C. I neither read its content,
staged it, edited it, deleted it, nor included it in either commit. I recorded
its SHA-256 with the repository state, then staged only the four Lane B files
listed above.

Consequently, the shared worktree was not globally empty after the Lane B code
push solely because of `?? CCF_Sovereign/test_no_recipe_guard.py`. Lane B's
committed paths were clean and `HEAD == origin/main` at the factual commit. The
central integration pass must allow Lane C to commit or otherwise preserve its
owned file before asserting an empty shared worktree.

## Not Run and Remaining Boundaries

No full Primus test suite, BridgeData test, model training, candidate lifecycle,
promotion gate, corpus-generation run, Blender invocation, renderer test,
installer operation, or no-recipe guard test was run. The no-recipe guard is
Lane C's owned file and is still untracked at this handoff point.

A real corpus does not yet exist in this lane. Lane A owns corpus production
after its scorer-separation gate; this consumer is ready to load an artifact that
conforms exactly to the frozen written contract. Before any training or
performance assertion, the consumer must receive a real hash-pinned corpus and
the Phase 0 learner must be evaluated against these declared baselines on the
two structural holdouts.

## Next Sequence

1. Preserve and integrate Lane C's owned guard file without editing it from this lane.
2. Obtain a real `geometry_program_corpus_v1` JSONL, split definition, and
   manifest from Lane A's authorized sampler only after Lane A's scorer gate
   passes.
3. Run `load_geometry_corpus_intake(corpus, manifest, splits)` and archive the
   verified hashes outside the mutable corpus location.
4. Run `evaluate_declared_baselines(intake)` to produce the pre-model reference
   metrics, then keep those results split separated.
5. Do not train, promote, or claim geometry understanding until an authorized
   Phase 0 learner beats every declared baseline on the structural holdouts.
