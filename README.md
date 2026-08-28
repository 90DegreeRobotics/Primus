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
predeclared h1/h2/h5 point-estimate rule on both target protected partitions.
Candidate `002` on candidate `001` passed target held-out episodes but had a
point-estimate target held-out-task h5 deficit of `0.00068158` RMSE
(`0.26076429` versus nearest-neighbor `0.26008270`). A follow-on read-only,
10,000-resample episode-clustered paired bootstrap reconstructed the signed
case sets and found the corresponding candidate-minus-baseline MSE 95% interval
`[-0.00524649, 0.00961948]`, which includes zero. That row is therefore
**indistinguishable**, not a statistically supported robustness failure. All
other cross-audited h1/h2/h5 rows had negative 95% upper endpoints and passed
the uncertainty-aware rule. Every cross-target split had source-train task
overlap, so the cross audit remains episode-disjoint robustness evidence, not a
strict unseen-task claim relative to the source model.

The next feasibility check measured whether the same frozen BridgeData intake
can support a strict source-train-task-disjoint cross audit. It can. After
excluding source-selected episodes and every source-train task ID, candidate
`001` still had 23,124 eligible target episode clusters with 715,495 h5 rollout
case capacity; candidate `002` had 23,973 clusters with 732,461 h5 capacity.
At that point, this was feasibility evidence only; the strict task-disjoint
model comparison had not yet been run.

A subsequent strict source-train task-disjoint cross-rollout gate used a source-specific stable selection of 128 complete target episodes per frozen candidate, with zero source-selected episode overlap and zero source-train task-ID overlap. Both sources had exact finite 256-case coverage and passed the h1/h2/h5 point-estimate and 10,000-resample episode-clustered bootstrap rules. At h5, candidate `001` scored `0.0681601396` versus source-train linear baseline `0.0853185955`, while candidate `002` scored `0.0679752241` versus `0.0802132039`. This is a distinct strict task-ID separation result on the bounded intake; it remains short-horizon observational prediction evidence only.

A subsequent broader context audit kept the same frozen strict source-train task-ID separation and partitioned 24 bounded rollout rows by early/late episode position and low/high recorded action energy. All rows had exact finite coverage and zero source-train task overlap; 19 paired-bootstrap rows passed. Five rows remain visible as one point-estimate failure or four bootstrap-indistinguishable cells, so neither frozen candidate has universal context robustness. This is useful negative evidence as well as positive evidence: the local predictors are broadly competitive in this bounded audit, not established as reliable across every measured trajectory/action context.

Primus now also has a schema-valid, hash-bound **offline transition-evidence contract** for a future Chronos2 consumer. It carries one frozen predictor's observed 7D initial state/action sequence and recursively predicted 7D state sequence with explicit unknown scene-coordinate semantics. It rejects renderer, scene, program, control, actuation, and promotion fields. This is a consumer handoff boundary only: no Chronos runtime was invoked, and it establishes no 7D-to-scene mapping, native integration, render, or product capability.

A deterministic offline diagnostic now makes one frozen strict-task h5 trace inspectable: seven opaque state-coordinate panels compare observed values with recursive local predictions over five observed actions, with a separate absolute-error strip. It is derived only after raw lineage verification and visibly states that it is not a Chronos scene, render, policy, or control signal. The accepted PNG is a data chart, **not** a direct-Blender or native Chronos renderer PNG.

A mechanical offline-artifact safety gate now verifies the frozen contract witness plus accepted diagnostic as a pair before an evidence review. It refuses unsafe consumer intent, altered digests/bindings/labels, unknown fields such as a `program`, and nonfalse control, renderer, Chronos-execution, or promotion flags. Its output sets `execution_authorized: false`. This guards the current artifact schema; it does **not** certify runtime, physical, policy, or downstream-consumer safety.

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





