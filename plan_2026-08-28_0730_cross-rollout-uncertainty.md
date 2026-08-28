# Plan — Cross-Candidate Rollout Uncertainty Audit

**Status:** COMPLETE — one signed-evidence-bound paired uncertainty audit completed; one cross-task h5 row is statistically indistinguishable

**Date:** 2026-08-28 07:30 CDT

## Goal

Harden the bounded BridgeData cross-candidate rollout interpretation without training, candidate creation, checkpoint mutation, or promotion. The audit will determine whether each candidate-versus-strongest-baseline difference at protected horizons one, two, and five is statistically distinguishable under a predeclared, episode-clustered paired bootstrap. It will replace no prior point-estimate record; it will add a second, uncertainty-aware interpretation layer.

## Files to Read

- `AGENTS.md`, `README.md`, `STATUS.md`, Charter, and the latest BridgeData rollout/cross-rollout handoffs and plans.
- `CCF_Sovereign/evaluate_bridgedata_cross_candidate_rollout.py` and the frozen-candidate/rollout/baseline modules it imports.
- Existing cross-rollout evidence file and its SHA-256/payload binding.
- The current focused BridgeData tests and `.gitignore` rules for local numeric evidence.

## Files to Edit

- A separate `CCF_Sovereign/src/real_data/bridgedata_rollout_uncertainty.py` pure statistical module and focused fixture test.
- A separate read-only `CCF_Sovereign/evaluate_bridgedata_cross_rollout_uncertainty.py` entrypoint and focused integrity test.
- `.gitignore` only to exclude the declared local uncertainty-evidence root before invocation, if no existing rule covers it.
- This plan, a root handoff, and truth surfaces only after a measured audit result exists.

## Predeclared Contract

The audit subjects are exactly `bridge-real-20260827-001` and `bridge-real-20260827-002`, both terminally rejected no-promotion candidates. It will bind and hash-check the existing linear-amended cross-rollout evidence at `CCF_Sovereign/evaluation/bridgedata_cross_rollouts/cross-rollout-20260828-linear-001/cross_rollout_stability.json` before evaluating any residuals. The file is expected to remain SHA-256 `2c8dd8c8930b968cebbac7c75403150a9ec1b861d14719171da6fbea088ac484`.

Existing cross-rollout evidence stores aggregate metrics but not per-case prediction vectors. The audit therefore must **reconstruct only the predeclared deterministic 256-case rollout selections** from verified frozen candidate checkpoints and source-train baselines, read-only, then require its recomputed aggregate RMSE to agree with the signed existing evidence for each candidate/pair/protected-split/horizon before calculating uncertainty. This is a read-only recomputation, not a training or new candidate run.

For every ordered candidate pair, protected target partition, and acceptance horizon 1, 2, and 5, compare the frozen model to the baseline already recorded as strongest in the signed cross-rollout evidence. The paired response is **case-level mean squared state error across the seven dimensions**, calculated as candidate MSE minus baseline MSE. Positive values favor the baseline; negative values favor the candidate.

Use an episode-clustered nonparametric paired bootstrap: resample distinct selected episode IDs with replacement, retain all selected cases belonging to each drawn episode, calculate the case-weighted average MSE difference, and repeat exactly **10,000** times with seed `20260828`. The bootstrap must fail closed if fewer than 10 distinct selected episodes appear in a scored row. It must report the selected case count, distinct episode count, point MSE difference, equivalent point RMSE difference, bootstrap standard error, and two-sided percentile 95% confidence interval for the MSE difference. It must not report a p-value as causal or safety evidence.

The interpretation for every row is fixed before implementation:

| Label | Requirements |
|---|---|
| **Pass** | Exact finite coverage; point candidate RMSE is lower; and the upper endpoint of the two-sided 95% paired bootstrap interval for candidate-minus-baseline MSE is below zero. |
| **Fail** | Exact finite coverage; point candidate RMSE is higher; and the lower endpoint of the two-sided 95% paired bootstrap interval is above zero. |
| **Indistinguishable** | Exact finite coverage but the 95% interval includes zero, or the point direction and interval do not meet either stronger label. |
| **Ineligible** | Source/evidence/hash/coverage/continuity check fails, or fewer than 10 selected episodes exist. Stop and preserve the failure; do not reinterpret. |

The audit may revise the **uncertainty-aware interpretation** of cross-candidate robustness. It may not erase the prior predeclared point-estimate result. It remains episode-disjoint only; source-train task overlap prevents a strict unseen-task claim relative to the source model. No conclusion authorizes promotion.

## Ordered Steps

- [x] Capture exact repository, concurrent-work, process, candidate, input, and existing-evidence baseline. Preserve all inherited dirty/untracked files.
- [x] Verify the existing cross evidence has no per-case vectors and probe the selected case episode counts read-only before implementation. All signed 256-case rows contain 54–62 distinct selected episodes, exceeding the predeclared minimum of 10.
- [x] Implement deterministic cluster-bootstrap and exact interpretation labels in a separate pure module with temporary-fixture tests.
- [x] Implement a separate read-only evidence-bound auditor that recomputes only signed rows, validates aggregate RMSE parity, and writes raw paired-error evidence only below a fresh ignored local destination.
- [x] Run compile and focused tests, audit this plan, explicitly stage only owned paths, commit and push `origin/main` before the audit invocation. The combined focused regression suite completed with 48 tests passed before audit.
- [x] Run exactly one audit invocation, then verify no process and no protected artifact/candidate/lifecycle drift. The 1,142,125-byte local evidence file has SHA-256 `6cff7a762adf7e4e15da98ca1bee6a72e52f24bbf714d8e743fb0ae50bab2b04` and binds the signed cross-evidence file SHA-256 `2c8dd8c8930b968cebbac7c75403150a9ec1b861d14719171da6fbea088ac484`.
- [x] Write a handoff and narrow truth-surface amendment from actual measured results, audit it, explicitly commit/push it, and report all pass/indistinguishable/fail labels.

## Test Gate

Run `python -m compileall -q` for all touched source and test files. Run a focused `python -m unittest -v` suite covering existing BridgeData extraction/evaluation/candidate/rollout/cross-rollout tests plus new paired-bootstrap and auditor integrity tests. Before each commit run `git diff --check --cached`; audit Markdown plan/handoff before staging.

## Storage and Safety

No download, video, model training, model selection, candidate creation, checkpoint write, data mutation, parent mutation, promotion, renderer, Chronos integration, 6FR work, robot command, actuation, manufacturing operation, or external deployment is authorized. Local numeric audit evidence is expected to be below 5 MiB and must remain Git-ignored in a fresh named directory. Do not delete, overwrite, reset, amend, bulk-stage, or modify Codex-owned in-flight work.

## Measured Result Boundary

All 12 ordered-pair/protected-partition/horizon rows had exact finite coverage for 256 deterministic cases and 54–62 selected episode clusters. The point-estimate result is unchanged: the `002 -> 001` held-out-task horizon-five model RMSE is `0.26076428791202466`, higher than its signed strongest nearest-neighbor baseline `0.26008270475923234` by `0.00068158315279232`. Under the predeclared 10,000-resample episode-clustered paired bootstrap, however, candidate-minus-baseline MSE has 95% interval `[-0.005246492287060185, 0.009619483092465034]`, which includes zero. That row is therefore **indistinguishable**, not a statistically supported fail. Every other audited acceptance row has a negative 95% upper MSE endpoint and is labeled pass.

This narrows cross-candidate interpretation to episode-disjoint bounded short-horizon evidence with one indeterminate strict-task-named target row. Source-train task overlap persists in all rows, so it remains invalid to call this strict unseen-task generalization relative to either source model.

## Rollback Path

Preserve every failed audit log or partial local evidence receipt. Do not rerun against altered thresholds, sources, baselines, or candidates. Do not delete prior cross-rollout evidence. If raw residual reconstruction cannot reproduce the signed aggregate evidence exactly within documented floating-point tolerance, record an ineligible result and stop.

## Next-Agent Pickup Notes

The key question is not whether the point-estimate h5 failure of `002 -> 001` exists; it does. The question is whether the observed `0.0006815841557626` RMSE deficit against nearest neighbor is distinguishable from episode-clustered uncertainty on the 256 selected cases. The current cross JSON provides aggregate metrics but no raw per-case predictions; the separate auditor must reconstruct and bind them to the signed file before computing any statistical label. Never call the outcome symmetric robustness, policy learning, control, safety, visual world modeling, native Chronos integration, or product readiness.
