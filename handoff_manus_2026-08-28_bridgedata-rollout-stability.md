# Handoff — BridgeData Frozen-Checkpoint Rollout Stability Gate

**Status:** Completed; both frozen rejected candidates passed the bounded short-horizon open-loop comparison. Neither candidate was promoted, retrained, renamed, or mutated.

## Scope

This gate evaluated the two existing local BridgeData state-transition candidates, `bridge-real-20260827-001` and `bridge-real-20260827-002`, without creating a candidate or changing a checkpoint. The only task was open-loop observational state prediction: start from an observed seven-dimensional robot state, advance through the recorded observed action sequence, recursively pass each predicted state—not the next observed state—to the next model step, then compare the terminal state to observation.

The evaluator operated on the candidates' existing whole-episode, leakage-safe train, held-out-episode, and strict held-out-task partitions. It first re-verified each terminal lifecycle manifest, checkpoint, one-step metric receipt, raw-prediction receipt, split receipt, frozen data inputs, protected parent copies, and re-extracted transition receipt. It rejected any file hash, split hash, lifecycle status, normalization training-IDs, source continuity, or split-coverage disagreement.

No robot policy, action selection, control, actuation, safety process, manipulation task, counterfactual intervention, video prediction, renderer, Chronos runtime, 6FR implementation, manufacturing operation, data download, training run, candidate creation, parent mutation, or promotion was performed.

## Predeclared Evaluation Contract

Each candidate/partition/horizon measurement used only episode-contained, source-continuous transition sequences. All links required a consistent episode/task lineage, no skipped source frame or global index, continuous source timestamp, and state continuity from one observed transition target to the next observed transition source.

Rollouts used fixed horizons **1, 2, 5, and 10**. At every candidate/partition/horizon, the evaluator selected at most 256 valid rollout starts using stable SHA-256 ordering with fixed case-selection seed `20260827`; every measurement below therefore represents exactly 256 deterministic cases, not the entire acquired shard. It reported each candidate, partition, and horizon separately. No pooled protected score was emitted.

The three declared baselines were open-loop versions of: persistence/copy-state; repeated train-only action-only mean delta; and repeated train-only nearest state/action delta. Baseline inputs after rollout start were each baseline's own predicted state and the recorded action—never an observed intermediate state.

A narrow positive temporal signal required exact coverage and strictly lower terminal RMSE than the strongest explicit baseline on both protected partitions at horizons 1, 2, and 5. Horizon 10 was measured descriptively only. A nonfinite output, coverage discrepancy, or weaker score would have been retained as a stability limitation rather than leading to retuning or a new candidate.

## Preserved Initial Evaluator Failure

The first evaluator invocation reached a valid case where horizon-one error was exactly zero for a baseline, then exited with `BridgeDataRolloutError: horizon-one RMSE must be finite and positive for growth ratios`. Zero error is valid; the ratio to a nonzero later error is mathematically undefined, not a model failure.

That invocation created **no** rollout evidence directory and wrote no checkpoint, candidate manifest, source data, or parent. Its ignored local stdout/stderr logs remain preserved under `CCF_Sovereign/tmp/`. The evaluator was corrected and tested to report growth `1.0` for a zero-error later horizon and `null` for any nonzero later error when the horizon-one denominator is exactly zero. Commit `c442356de3f6858daa756f7877d01e935ea1efd0` records the correction. The corrected invocation retained the same frozen candidates, horizons, case-cap, ordering seed, device, and no-mutation scope.

## Measured Protected Results

All listed metrics have exact coverage `1.0`, finite prediction rate `1.0`, 256 cases per candidate/partition/horizon, zero unknown cases, and zero excluded cases.

### Candidate `bridge-real-20260827-001`

| Protected partition | Horizon | Candidate RMSE | Strongest baseline | Baseline RMSE | Improvement | Candidate growth from h1 | Rule status |
|---|---:|---:|---|---:|---:|---:|---|
| Held-out episode | 1 | 0.0233047044 | Nearest train state/action | 0.0353570645 | 0.0120523601 | 1.00× | Passed |
| Held-out episode | 2 | 0.0362147188 | Nearest train state/action | 0.0592501866 | 0.0230354678 | 1.55× | Passed |
| Held-out episode | 5 | 0.0687144457 | Nearest train state/action | 0.0995679869 | 0.0308535412 | 2.95× | Passed |
| Held-out episode | 10 | 0.0999690248 | Descriptive only | — | — | 4.29× | Descriptive |
| Strict held-out task | 1 | 0.0256026919 | Nearest train state/action | 0.0372130366 | 0.0116103447 | 1.00× | Passed |
| Strict held-out task | 2 | 0.0441626707 | Nearest train state/action | 0.0620604938 | 0.0178978232 | 1.72× | Passed |
| Strict held-out task | 5 | 0.2579618763 | Nearest train state/action | 0.2719944710 | 0.0140325946 | 10.08× | Passed, narrow margin |
| Strict held-out task | 10 | 0.2829567238 | Descriptive only | — | — | 11.05× | Descriptive |

### Candidate `bridge-real-20260827-002`

| Protected partition | Horizon | Candidate RMSE | Strongest baseline | Baseline RMSE | Improvement | Candidate growth from h1 | Rule status |
|---|---:|---:|---|---:|---:|---:|---|
| Held-out episode | 1 | 0.0274365122 | Nearest train state/action | 0.0400362021 | 0.0125996899 | 1.00× | Passed |
| Held-out episode | 2 | 0.0414619042 | Nearest train state/action | 0.0629380991 | 0.0214761949 | 1.51× | Passed |
| Held-out episode | 5 | 0.0670456486 | Nearest train state/action | 0.1050089792 | 0.0379633307 | 2.44× | Passed |
| Held-out episode | 10 | 0.0979831813 | Descriptive only | — | — | 3.57× | Descriptive |
| Strict held-out task | 1 | 0.0281386466 | Nearest train state/action | 0.0401927053 | 0.0120540586 | 1.00× | Passed |
| Strict held-out task | 2 | 0.0405296632 | Nearest train state/action | 0.0623226315 | 0.0217929684 | 1.44× | Passed |
| Strict held-out task | 5 | 0.0745211324 | Nearest train state/action | 0.1126893219 | 0.0381681895 | 2.65× | Passed |
| Strict held-out task | 10 | 0.1038816382 | Descriptive only | — | — | 3.69× | Descriptive |

Both candidates passed their predeclared acceptance rule. Candidate `001` remains more fragile on its strict held-out-task evaluation: its error at horizon five was about 10.08 times its horizon-one error and its margin over nearest-neighbor was only `0.0140325946`. Candidate `002` had substantially lower strict-task horizon-five error and a larger margin, but these are still two measurements on the same bounded external data shard rather than proof of robust long-horizon world modeling.

## Interpretation

The evidence now supports a narrow temporal statement: two frozen, independently episode-disjoint, locally trained from-scratch predictors retained a measured advantage over three stated train-only/persistence baselines through five recursively predicted, observed-action steps on their own protected held-out episodes and strict task partitions.

It also establishes an explicit stability limit. Errors compound materially by horizon five and ten. The worst measured curve was candidate `001` on strict held-out tasks, where horizon-five RMSE reached `0.2579618763` and horizon-ten RMSE `0.2829567238`. The results therefore do **not** establish reliable long-horizon rollouts, causal understanding, safe action selection, robot control, visual world models, native Chronos integration, or product readiness.

## Code and Verification

The frozen-checkpoint evaluator was added in commit `9dea80b5f4ac0ab68266ac7b15670acb4b5aa698` (`feat(real-data): add frozen rollout evaluation`). It provides a separate pure rollout module, a read-only evaluator, artifact/split/normalizer verification, deterministic bounded case selection, and train-only open-loop baselines. Commit `281db792a0dd23d3cca587f99173d203328de994` excludes rollout evidence from Git before invocation. Commit `c442356de3f6858daa756f7877d01e935ea1efd0` corrects the valid zero-error growth-ratio edge case.

The focused gate completed after the correction:

```text
python -m compileall -q src\real_data\__init__.py src\real_data\bridgedata_rollouts.py evaluate_bridgedata_rollout_stability.py test_bridgedata_transitions.py test_bridgedata_evaluation.py test_real_data_candidate.py test_train_bridgedata_real_transition.py test_bridgedata_rollouts.py test_evaluate_bridgedata_rollout_stability.py
python -m unittest -v test_bridgedata_transitions test_bridgedata_evaluation test_real_data_candidate test_train_bridgedata_real_transition test_bridgedata_rollouts test_evaluate_bridgedata_rollout_stability
```

The compile gate exited `0`; **35 focused tests passed**. The new tests cover deterministic bounded episode-contained rollout cases, frame/global-index and timestamp gap rejection, exact prediction coverage, recursive predicted-state feedback, zero-error ratio handling, terminal rejected/no-promotion candidate status, frozen file hash drift refusal, and split reconstruction.

## Local Evidence and Hashes

The corrected evaluation ran on CPU and wrote a 1,565,353-byte ignored receipt at `C:\Primus\CCF_Sovereign\evaluation\bridgedata_rollouts\rollout-20260827-001\rollout_stability.json`.

| Artifact | SHA-256 |
|---|---|
| Corrected rollout evidence file | `9cbd9458cac0926d572fb0130c06ca863996c9403d9f03ad6b7bdba8afce0920` |
| Canonical payload hash stored in evidence | `c4d186880976b98b039df0254815317f6d35fa4febb06868a04c67e7941dec4c` |
| Candidate 001 checkpoint | `ed03de679a4ae7304fc7ce2179f35fce1cc8ee4b0fb5e15f1198ac6595e87099` |
| Candidate 001 split evidence | `91056f918b490e9b222e6c27e46477279b20f9cfe39deea7d4c4437c338f7fb5` |
| Candidate 001 re-extracted transition set | `641082dbae338af2415feecc07120de9379d17f7603f983103fa4945e42051c9` |
| Candidate 002 checkpoint | `209bf7ef3e2ff6faf3f25b4cd12f9711edb7d9227f686ce5a8627a215d09c7bb` |
| Candidate 002 split evidence | `57b860ac23aeb30853a38b8ef08839d630087141ac6cf3f503c70e1fa4996566` |
| Candidate 002 re-extracted transition set | `eb1f6344f5af6680a31b58888d0bb1fccf3b1249e3f54acc1c99a7f0424a5d94` |
| Frozen BridgeData intake manifest | `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a` |
| Live and frozen Council parent copies | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |

At post-evaluation inspection, both candidate lifecycle manifests were still terminal `rejected`; promotion was `false`; their checkpoints and manifests retained their original hashes; the protected parent copies and intake manifest retained their original hashes; and no rollout or BridgeData process was active.

## Repository State and Next Boundary

Before this documentation closure, `main` and `origin/main` both resolved to `c442356de3f6858daa756f7877d01e935ea1efd0`. A `git status` metadata artifact reported `CCF_Sovereign/README.md` modified, but `git diff` was empty and the worktree blob exactly matched `HEAD`; it was not staged, changed, or included in any commit. The following inherited untracked plans also remained preserved and unstaged:

- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`

The next justified evidence boundary is not more one-step tuning. It is a separately planned **cross-candidate/cross-split robustness audit** that holds the two candidates fixed and asks whether their rollout advantage persists under the other candidate's protected episode/task selection where data/split semantics permit it, or whether task-space and horizon instability remain candidate/split-specific. It must remain evaluation-only and should predeclare task-overlap limitations. Only after such robustness evidence should an object-centric or visual real-data world-model design be considered. No renderer recipe work should resume.
