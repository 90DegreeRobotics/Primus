# Primus

Primus is the local-first NeuroCognica textual-mind workspace. This repository
is being brought under git governance from an existing local tree rather than a
fresh scaffold.

## Current Truth

- Canonical branch: `main`.
- Remote: `https://github.com/90DegreeRobotics/Primus.git`.
- Repo-law surface: `AGENTS.md`.
- Current status ledger: `STATUS.md`.

The local tree contains research documents, `CCF_Sovereign`, and
`NeuroCognica_Primus` material. Those surfaces must be imported intentionally
after audit. Do not bulk-stage the whole tree.

## Verified CCF world-core substrate

`CCF_Sovereign` now has fail-closed candidate isolation, a domain-general typed
world schema, a lossless S3V v1 bridge, and a memory-bounded chunked selective
scan. These are **substrate and evidence capabilities**, not proof of a learned
world-builder. The August 26 RTX 3060 ladder completed full 5.34M, 16.21M, and
53.93M parameter passes; the 155.35M rung completed one step and then recorded a
CUDA out-of-memory limit. No candidate was promoted and the frozen parent
remained protected.

The schema contract is documented in
`CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`. Non-confidential measurements are
recorded in the status and CCF audit ledgers; raw run manifests, checkpoints,
and local benchmark JSON remain ignored.

## Stage 2 trajectory data

`CCF_Sovereign` now includes a deterministic generator for synthetic, typed,
multi-frame world trajectories. It produces canonical JSONL and a hash-bound
manifest, preserves generated-versus-inferred evidence labels, reserves whole
object-class, operation-family, and composition holdouts, and measures
structural-program coverage. The first ignored local smoke dataset produced 21
validated programs with 21 unique structural signatures.

This is **data-generation infrastructure**, not learned capability. The generated
fixtures have not yet been compiled and rendered as a dataset, ingested by the
learner, scored as model predictions, or used to authorize a checkpoint
promotion.

## Bounded real state-transition evidence

On August 27, 2026, Primus completed one bounded, manifest-bound experiment on
observed BridgeData V2 LeRobot state/action rows. A compact 19,591-parameter MLP
trained from scratch on 11,999 one-step transitions achieved exact coverage and
lower aggregate RMSE than the strongest explicit baseline on two protected
partitions: `0.0249904402` versus `0.0399958638` on 1,998 held-out episodes and
`0.1087545187` versus `0.1124550702` on 1,996 transitions from 48 strict
held-out task identities. The frozen intake manifest is SHA-256
`a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a`.

An independent episode-disjoint replication then reserved all 453 episodes
selected by the first candidate, selected 476 different complete episodes with
zero overlap, and again passed the exact-coverage protected comparison. Its
aggregate RMSE was `0.0264679426` versus `0.0402912793` on 1,999 held-out
episode transitions and `0.0273437551` versus `0.0404739780` on 1,997 strict
held-out-task transitions. Both candidates remain separate local evidence and
were explicitly rejected from promotion.

A subsequent evaluation-only open-loop measurement froze both rejected
checkpoints, started from observed held-out states, and recursively fed only each
predictor's own state output plus recorded observed actions. On deterministic
256-case protected samples, both candidates remained below their strongest
stated baseline through horizons one, two, and five. A later amendment added a
train-only ordinary least-squares state/action delta baseline and reran the
gate. Both candidates still passed, but with narrower margins: candidate `001`
strict-task h5 was `0.2579618763` versus linear baseline `0.2638808140`, and
candidate `002` strict-task h5 was `0.0745211324` versus linear baseline
`0.0887700524`. Horizon-ten measurements were descriptive only. The details and
frozen artifact hashes are in the rollout handoffs.

The same linear-amended audit scored each frozen model against the other
candidate's protected episode selections, using only the source candidate's
train partition for baselines. It found zero protected episode overlap and exact
finite 256-case coverage. Candidate `001` on candidate `002` passed the
predeclared h1/h2/h5 rule on both target protected partitions. Candidate `002`
on candidate `001` passed target held-out episodes but failed target
held-out-task h5 by `0.00068158` RMSE (`0.26076429` versus nearest-neighbor
baseline `0.26008270`). Every cross-target split had source-train task overlap,
so the cross audit is episode-disjoint robustness evidence, not a strict
unseen-task claim relative to the source model.

This is narrow **replicated real-data short-horizon open-loop prediction
evidence**, not proof of robot policy learning, robot control/safety, reliable
long-horizon rollout, visual world models, native Chronos integration, or
product readiness. The committed handoffs name the local ignored evidence paths
and hashes.

## Operator Rules

Read `AGENTS.md` before changing anything. The short version:

- work on `main`
- no worktrees
- no force-push or history rewrite
- no deletion without explicit per-item approval
- no stubs or random-output demos reported as real
- stage by explicit pathspec
- run the gate before claiming done
- push verified units to `origin/main`

## Verification

For this initial governance seed, the relevant gate is:

```pwsh
git diff --check --cached
git status --short --branch
```

Future Python/code work must run the relevant command named in `AGENTS.md`.
For the current world-core surfaces, the focused gates are:

```pwsh
cd CCF_Sovereign
python test_world_schema.py
python test_chunked_scan.py
python test_candidate_training.py
python test_scaling_ladder.py
python test_mvp.py
```
