# Handoff — Cross-Candidate Rollout Uncertainty Audit

**Status:** Completed. The point-estimate cross-candidate record remains preserved; a signed-evidence-bound paired bootstrap adds an uncertainty-aware interpretation. No model, candidate, checkpoint, parent, input data, or promotion state was changed.

## Scope and Boundary

This audit addressed a narrow question left by the linear-amended cross-candidate rollout audit: whether candidate `002`'s h5 point-estimate deficit on candidate `001`'s target held-out-task partition (`0.00068158315279232` RMSE) was distinguishable from sampling uncertainty.

The audit did **not** train, tune, select, or promote a model. It did not create a candidate, modify a checkpoint, mutate a parent/input, issue an action, use a renderer, access Chronos2, run 6FR, or claim policy, control, safety, causality, vision, manufacturing, native Chronos integration, or product readiness.

The source candidates remain exactly `bridge-real-20260827-001` and `bridge-real-20260827-002`, both terminally `rejected` with promotion `false`. The audit is episode-disjoint robustness analysis only. Every target partition had source-train task overlap, so no row is a strict unseen-task test relative to the source candidate.

## Why a New Audit Was Needed

The signed linear-amended cross-rollout report stores aggregate RMSE/MAE metrics but not per-case prediction vectors. A paired uncertainty claim cannot responsibly be inferred from a `0.00068158` RMSE difference alone on 256 selected cases. The new evaluator therefore re-created only the already predeclared deterministic rollout cases from frozen checkpoints and recorded actions, re-computed candidate and strongest-baseline predictions read-only, and refused to bootstrap any row unless each reconstructed aggregate metric matched the signed report.

The signed report is:

| Input | Value |
|---|---|
| Source path | `C:\Primus\CCF_Sovereign\evaluation\bridgedata_cross_rollouts\cross-rollout-20260828-linear-001\cross_rollout_stability.json` |
| Signed file SHA-256 | `2c8dd8c8930b968cebbac7c75403150a9ec1b861d14719171da6fbea088ac484` |
| Signed payload SHA-256 | `60b066d31bca385a28e9ae644d359e6c64470a50495dec5520c99afad8f7635e` |
| Required metric parity | Exact integer/coverage/case-set identity fields; aggregate RMSE absolute tolerance `1e-12` |

The auditor verified that the signed rows contain 256 deterministic rollout cases each and 54–62 distinct selected episode clusters per row. All exceed the predeclared minimum of 10 clusters.

## Fixed Statistical Protocol

For every ordered source-target pair, protected target partition, and horizon 1, 2, and 5, the comparison response was each case's mean squared seven-dimensional terminal-state error: **candidate MSE minus the MSE of the strongest baseline recorded in the signed report**. Negative values favor the candidate.

The audit used a deterministic episode-clustered nonparametric paired bootstrap: resample selected episode IDs with replacement, preserve all selected rollout cases for each drawn episode, compute a case-weighted mean MSE difference, repeat 10,000 times with seed `20260828`, and report a two-sided percentile 95% interval. This quantifies uncertainty within the fixed selected case sets; it is not a causal, safety, or population-level guarantee.

| Label | Fixed criterion |
|---|---|
| Pass | Candidate point RMSE is lower and the 95% interval's upper candidate-minus-baseline MSE endpoint is below zero. |
| Fail | Candidate point RMSE is higher and the 95% interval's lower endpoint is above zero. |
| Indistinguishable | Exact finite coverage, but neither interval/direction criterion above holds. |
| Ineligible | Any source, hash, signed-metric parity, continuity, coverage, or minimum-cluster check fails. |

## Measured Results

Every listed row has exact 256-case coverage, finite predictions, zero unknown/excluded cases, and signed-metric parity before bootstrap. The strongest baseline was the train-only linear state/action delta predictor except for the final `002 -> 001` target held-out-task h5 row, where train-only nearest-neighbor was the signed strongest baseline.

| Source → target | Target partition | Horizon | Candidate RMSE | Strongest baseline RMSE | RMSE difference | Episode clusters | 95% CI, candidate-baseline MSE | Result |
|---|---|---:|---:|---:|---:|---:|---|---|
| `001 → 002` | Held-out episode | 1 | 0.0255309951 | 0.0295028921 | -0.0039718970 | 58 | [-0.0003943262, -0.0000655992] | Pass |
| `001 → 002` | Held-out episode | 2 | 0.0397249006 | 0.0462105572 | -0.0064856566 | 60 | [-0.0009558664, -0.0002023630] | Pass |
| `001 → 002` | Held-out episode | 5 | 0.0632727615 | 0.0741754863 | -0.0109027248 | 58 | [-0.0024607629, -0.0006280400] | Pass |
| `001 → 002` | Target held-out task* | 1 | 0.0275996891 | 0.0321935513 | -0.0045938622 | 59 | [-0.0004944710, -0.0000188841] | Pass |
| `001 → 002` | Target held-out task* | 2 | 0.0388953815 | 0.0490500849 | -0.0101547034 | 62 | [-0.0012593081, -0.0005111409] | Pass |
| `001 → 002` | Target held-out task* | 5 | 0.0722573487 | 0.0869020725 | -0.0146447238 | 62 | [-0.0043788009, -0.0003014043] | Pass |
| `002 → 001` | Held-out episode | 1 | 0.0243369066 | 0.0289614687 | -0.0046245621 | 58 | [-0.0004347558, -0.0000378728] | Pass |
| `002 → 001` | Held-out episode | 2 | 0.0415129512 | 0.0475668289 | -0.0060538777 | 57 | [-0.0009748663, -0.0001370518] | Pass |
| `002 → 001` | Held-out episode | 5 | 0.0729569041 | 0.0868304670 | -0.0138735629 | 59 | [-0.0035377587, -0.0008036641] | Pass |
| `002 → 001` | Target held-out task* | 1 | 0.0252822769 | 0.0322231707 | -0.0069408938 | 54 | [-0.0005655544, -0.0002331865] | Pass |
| `002 → 001` | Target held-out task* | 2 | 0.0436641441 | 0.0546690339 | -0.0110048898 | 56 | [-0.0015461078, -0.0006218015] | Pass |
| `002 → 001` | Target held-out task* | 5 | 0.2607642879 | 0.2600827048 | +0.0006815832 | 56 | [-0.0052464923, +0.0096194831] | **Indistinguishable** |

\* The partition name is inherited from the target candidate's split. Each source candidate's train task set overlaps its target task set, so this naming does not establish a strict unseen-task result relative to the source candidate.

The final row preserves the former point-estimate ordering: candidate `002` is worse than nearest-neighbor by `0.0006815832` RMSE. But the episode-clustered paired 95% interval includes zero, and therefore the evidence does **not** support classifying it as a robust statistical failure. It is correctly **indistinguishable** under the predeclared three-way rule.

## Interpretation

The defensible update is:

> On the two fixed episode-disjoint cross-candidate selections, the frozen models retain a statistically supported bounded short-horizon advantage over their signed strongest baseline at horizons one and two in both transfer directions. At horizon five, `001 → 002` retains that advantage on both target partitions; `002 → 001` retains it on held-out episodes, while its target held-out-task-named row is statistically indistinguishable from the source-train nearest-neighbor baseline under the declared episode-clustered bootstrap.

This is stricter and more accurate than calling the results symmetric or asymmetric robustness. It does not overturn the signed point estimate; it reports the uncertainty around that near-zero difference.

There is a remaining strong limitation: cross-target target-task labels do not denote strict unseen tasks for the source model because source-train task overlap is nonzero in every row. The evidence is therefore **bounded, episode-disjoint, short-horizon robustness**, not compositional task generalization or a learned world model in the broad sense.

## Implementation and Tests

New code was isolated from existing candidate and synthetic-world interfaces:

- `CCF_Sovereign/src/real_data/bridgedata_rollout_uncertainty.py` implements exact paired residual construction, episode-clustered resampling, deterministic percentile intervals, and predeclared pass/indistinguishable/fail labels.
- `CCF_Sovereign/evaluate_bridgedata_cross_rollout_uncertainty.py` binds the signed cross-evidence file and payload, re-verifies frozen candidates, rebuilds only fixed cases, checks signed aggregate parity, and emits local ignored paired residual evidence.
- `CCF_Sovereign/test_bridgedata_rollout_uncertainty.py` covers deterministic bootstrap pass/fail/indistinguishable outcomes, the minimum-cluster refusal, and exact prediction coverage.
- `CCF_Sovereign/test_evaluate_bridgedata_cross_rollout_uncertainty.py` covers signed file/payload drift refusal and aggregate-metric parity refusal.
- `.gitignore` now excludes `CCF_Sovereign/evaluation/bridgedata_cross_rollout_uncertainty/`.

The integration code was committed and pushed before the audit:

```text
467f62a15f8d7ebdbd5f2d6277b76db4f775e32b feat(real-data): audit rollout uncertainty
```

The exact verification command completed successfully with exit code 0 and **48 focused tests passed**:

```text
python -m compileall -q src\real_data\__init__.py src\real_data\bridgedata_evaluation.py src\real_data\bridgedata_rollouts.py src\real_data\bridgedata_rollout_uncertainty.py train_bridgedata_real_transition.py evaluate_bridgedata_rollout_stability.py evaluate_bridgedata_cross_candidate_rollout.py evaluate_bridgedata_cross_rollout_uncertainty.py test_bridgedata_transitions.py test_bridgedata_evaluation.py test_real_data_candidate.py test_train_bridgedata_real_transition.py test_bridgedata_rollouts.py test_evaluate_bridgedata_rollout_stability.py test_evaluate_bridgedata_cross_candidate_rollout.py test_bridgedata_rollout_uncertainty.py test_evaluate_bridgedata_cross_rollout_uncertainty.py
python -m unittest -v test_bridgedata_transitions test_bridgedata_evaluation test_real_data_candidate test_train_bridgedata_real_transition test_bridgedata_rollouts test_evaluate_bridgedata_rollout_stability test_evaluate_bridgedata_cross_candidate_rollout test_bridgedata_rollout_uncertainty test_evaluate_bridgedata_cross_rollout_uncertainty
```

## Local Evidence and Integrity

The audit executed once on CPU and wrote only local ignored evidence:

| Artifact | Value |
|---|---|
| Evidence path | `C:\Primus\CCF_Sovereign\evaluation\bridgedata_cross_rollout_uncertainty\cross-rollout-uncertainty-20260828-001\cross_rollout_uncertainty.json` |
| Evidence bytes | 1,142,125 |
| Evidence file SHA-256 | `6cff7a762adf7e4e15da98ca1bee6a72e52f24bbf714d8e743fb0ae50bab2b04` |
| Canonical payload SHA-256 | `16b92e45cd476bc260919bbd96cbd7342d5b29bbb36fb45f4ca462a013d38952` |
| Protected Council parent copies | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |
| Frozen BridgeData intake manifest | `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a` |
| Candidate 001 checkpoint | `ed03de679a4ae7304fc7ce2179f35fce1cc8ee4b0fb5e15f1198ac6595e87099` |
| Candidate 002 checkpoint | `209bf7ef3e2ff6faf3f25b4cd12f9711edb7d9227f686ce5a8627a215d09c7bb` |

Post-audit checks found no active relevant Python process. Both lifecycle manifests remained `rejected` and promotion remained `false`. The signed input evidence, protected parent, frozen intake, and candidate checkpoints retained their stated hashes.

## Repository State and Next Boundary

Before this documentation closure, `main` and `origin/main` both resolved to `467f62a15f8d7ebdbd5f2d6277b76db4f775e32b`. `CCF_Sovereign/README.md` remained an inherited status-cache artifact: Git reports modification, but its worktree blob equals `HEAD` and `git diff` has no content. It was untouched and unstaged. The following inherited root plans also remain preserved and unstaged:

- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`

The next valid Primus boundary is not repeated bootstrap testing or candidate retuning. It is a separately planned **strict source-train task-disjoint cross-evaluation** using an approved data allocation capable of zero source-train task overlap. The current bounded shard/splits may not support that allocation at sufficient episode count; feasibility must be measured before a run. Until that evidence exists, do not call the cross result task generalization, broad robustness, intelligence, control, safety, or product readiness. Do not reopen frozen renderer recipe work.
