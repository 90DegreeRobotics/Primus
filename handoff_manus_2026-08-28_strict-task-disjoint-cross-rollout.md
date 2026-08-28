# Handoff — Strict Source-Train Task-Disjoint Cross-Candidate Rollout Evaluation

**Status:** Completed. Both frozen rejected BridgeData candidates passed the predeclared bounded strict source-train-task-disjoint rollout gate at horizons 1, 2, and 5 by point estimate and episode-clustered paired-bootstrap interpretation. No candidate was promoted.

## Question Answered

This evaluation answered a question the previous cross-candidate audit could not answer: whether each frozen source predictor retains a measured short-horizon action-conditioned state-prediction advantage on targets whose task identities were entirely absent from that source candidate's training partition.

The prior cross-candidate audit was episode-disjoint but had source-train task overlap in every row. This is a distinct, stricter evaluation. The strict target selection excludes every source-selected episode and every task ID present in the source candidate's train split before transition extraction or prediction.

## Fixed Protocol

The only source candidates were terminally rejected `bridge-real-20260827-001` and `bridge-real-20260827-002`. Candidate lifecycle state was verified as `rejected` with promotion `false` before and after evaluation.

For each source candidate, a stable source-ID-specific hash order selected 128 complete eligible target episodes from the committed feasibility pool. The selected target episodes had zero overlap with every source-selected episode and their task identities had zero overlap with source-train task identities. The evaluator extracted only manifest-bound, same-episode, consecutive, finite, expected-timestamp transitions for those selected episodes.

At each horizon 1, 2, and 5, the evaluator selected 256 deterministic episode-contained cases with seed `20260828`. It initialized each rollout from the observed first state, then fed only the frozen predictor's recursively predicted state plus recorded observed actions into subsequent steps. It compared copy-state, source-train action-only mean delta, source-train OLS state/action delta, and source-train nearest neighbor. The strongest baseline was chosen independently per source/horizon. Horizon 10 was deliberately excluded.

A point-estimate pass requires exact finite coverage and lower terminal aggregate RMSE than the strongest baseline. The established uncertainty protocol also resampled selected episode clusters 10,000 times with seed `20260828`, applying the paired candidate-minus-baseline terminal-state MSE rule. A bootstrap pass requires lower point RMSE and a negative upper 95% MSE endpoint.

## Measured Result

Every source/horizon row had 256 exact finite predictions, zero unknown/excluded predictions, and zero observed source-selected-episode and source-train-task overlap. Both frozen candidates passed all h1/h2/h5 point-estimate and bootstrap labels.

| Source candidate | Strict target complete episodes | Strict target task IDs | h5 selected case episodes | h5 selected case task IDs | h5 candidate RMSE | h5 strongest baseline | h5 baseline RMSE | h5 RMSE margin | h5 paired MSE 95% interval | h1/h2/h5 outcome |
|---|---:|---:|---:|---:|---:|---|---:|---:|---|---|
| `bridge-real-20260827-001` | 128 | 112 | 107 | 95 | 0.0681601395924661 | Linear state/action delta | 0.0853185955056040 | 0.0171584559131379 | [-0.00363248166347317, -0.00173388340505353] | Pass / Pass / Pass |
| `bridge-real-20260827-002` | 128 | 123 | 108 | 105 | 0.0679752241255209 | Linear state/action delta | 0.0802132038781987 | 0.0122379797526778 | [-0.00258723978344747, -0.00102852483738104] | Pass / Pass / Pass |

This is the first completed result in this workstream with zero **source-train task overlap** in a cross-candidate frozen-checkpoint rollout comparison. It is real evidence of bounded short-horizon predictive generalization across this task-identity separation, subject to the limits below.

## Source and Evidence Binding

| Binding | Value |
|---|---|
| Integration code commit before run | `2f8862d91cb09975ee4a74d0c381bb038d3174d5` |
| Feasibility receipt SHA-256 | `c56fb16e1fa6a45691af1d95240721c949d0bdcf3641a951315538fad8bcff54` |
| Strict evaluation evidence path | `C:\Primus\CCF_Sovereign\evaluation\bridgedata_strict_task_cross_rollouts\strict-task-cross-rollout-20260828-001\strict_task_cross_rollout.json` |
| Strict evaluation evidence bytes | 633,639 |
| Strict evaluation evidence SHA-256 | `218748de489ebc0b921566c21fd8a712898ba77efd1e2251e764c86f90d2ba1f` |
| Strict evaluation payload SHA-256 | `445caddf9fb884dae35499a59a856a175d90ff6fee2b03862da7f303c30d172c` |
| Frozen intake manifest SHA-256 | `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a` |
| Protected Council parent SHA-256 | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |
| Candidate 001 checkpoint SHA-256 | `ed03de679a4ae7304fc7ce2179f35fce1cc8ee4b0fb5e15f1198ac6595e87099` |
| Candidate 002 checkpoint SHA-256 | `209bf7ef3e2ff6faf3f25b4cd12f9711edb7d9227f686ce5a8627a215d09c7bb` |

Post-evaluation verification found no active relevant Python process. The protected parent, frozen intake manifest, feasibility receipt, candidate checkpoints, and both terminal no-promotion lifecycle states were unchanged.

## Preserved Implementation Findings

The evaluator implementation was tested before scoring. A full focused BridgeData suite completed with exit code 0 and 57 tests passed. The strict evaluator's initial unscored target-capacity probe preserved two genuine contract errors: first, it supplied a custom split label that the existing rollout case constructor correctly rejected; second, it attempted an unsupported unbounded case request. The evaluator was corrected to use the existing protected split label and its predeclared 256-case limit. A final no-model-scoring preflight then verified 128 observed target episodes and 256 h1/h2/h5 cases for each source before the scored run.

These preflight corrections did not change candidates, inputs, selection seed, strict eligibility rules, baseline definitions, or the eventual scoring protocol.

## Correct Claim and Non-Claims

> The two frozen local predictors beat their strongest source-train-only explicit baselines at horizons one, two, and five on two independently source-specific, complete-episode targets whose task identities were absent from the respective source training partitions. Each row had exact finite 256-case coverage and a negative upper paired-bootstrap 95% MSE endpoint.

This is **bounded short-horizon action-conditioned 7D robot-state prediction evidence** on a frozen public observational intake. It is not evidence of causal understanding, a general-purpose world model, policy learning, robot control, safety, actuation, manufacturing, visual prediction, long-horizon reliability, native Chronos rendering/integration, product readiness, or a basis for promotion. The two candidates remain rejected evidence artifacts.

The target episode pools are source-specific and their 128 selected episodes are not a new independent dataset. The task-disjoint property is relative to the source train task IDs; it does not prove semantic task novelty, camera/image generalization, physical transfer, or performance across the complete BridgeData population.

## Repository State and Next Boundary

Before documentation closure, `main` and `origin/main` both point to `2f8862d91cb09975ee4a74d0c381bb038d3174d5`. Local numeric evidence remains Git-ignored.

The untouched known status-cache artifact remains `CCF_Sovereign/README.md`: Git marks it modified, but it has no content diff and its blob matches `HEAD`. The following inherited root plans remain unstaged and unchanged:

- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`

The next useful Primus gate is **not** retuning or promoting either candidate. The next measurement should test a held-out time/context or more challenging compositional state distribution under predeclared selection rules, then determine whether strict task-disjoint short-horizon gains survive a more diverse frozen intake. That must be separately planned, resourced, and data-scale-approved. It must remain observational evaluation unless the user explicitly authorizes a different safety boundary.
