# Plan — BridgeData Temporal and Action-Context Robustness

**Status:** ACTIVE

**Date:** 2026-08-28 10:00 CDT

## Goal

Run one bounded, read-only broader robustness audit on the two frozen rejected BridgeData candidates. The target episodes remain strictly source-train-task-disjoint. The audit will partition episode-contained observed rollouts by early/late trajectory position and low/high source-train action-energy context, then compare frozen recursive prediction against source-train-only explicit baselines.

## Evidence Boundary

The strict source-train task-disjoint evidence receipt `218748de489ebc0b921566c21fd8a712898ba77efd1e2251e764c86f90d2ba1f` is fixed prior evidence. This audit neither retrains nor creates candidates and does not replace any existing result. It uses source-specific complete target episodes already eligible under Codex feasibility receipt `c56fb16e1fa6a45691af1d95240721c949d0bdcf3641a951315538fad8bcff54`.

## Fixed Protocol

- Sources: frozen rejected candidates `bridge-real-20260827-001` and `bridge-real-20260827-002`, with promotion false.
- Strict targets: zero source-selected episode overlap and zero source-train task-ID overlap before transition extraction.
- Horizons: 1, 2, and 5.
- Context axes: early versus late trajectory position from declared episode range; low versus high cumulative recorded-action L2 energy using source-train median threshold only.
- Case budget: at most 128 deterministic complete-trajectory cases per source, horizon, and context cell; selection seed `20260828`; at least 10 distinct episode clusters per cell.
- Baselines: copy-state, source-train action-only mean delta, source-train OLS state/action delta, source-train nearest neighbor.
- Metrics: exact finite coverage, aggregate RMSE/MAE, strongest baseline, point margin, and predeclared 10,000-resample episode-clustered paired bootstrap.
- Interpretation: each cell is pass, indistinguishable, or fail. No aggregate success label can conceal a failed or indeterminate cell.

## Files To Read

- `AGENTS.md`, Charter, README, STATUS, strict rollout handoff, feasibility scanner, rollout/cross-rollout/uncertainty modules, candidate manifests, and intake manifest.

## Files To Edit

- A separate real-data context robustness evaluator and focused tests; `.gitignore` if a fresh local evidence root is not covered; this plan and, only after results, a handoff/README/STATUS.

## Ordered Steps

- [x] Capture repository/process/protected-hash baseline and preserve existing dirty/untracked paths.
- [x] Implement and fail-hard test context classification, source-train threshold fitting, strict target selection, deterministic bounded cases, baseline fitting, metric parity, and bootstrap labels. A preserved no-model-scoring preflight exposed that rollout `source_frame_index` is episode-local while episode metadata `dataset_from_index` is global; the evaluator now uses the episode-local coordinate and its regression fixture has a nonzero global metadata offset. The corrected capacity probe found every h1/h2/h5 temporal/action cell had 647–1,497 cases and 103–128 episode clusters for both sources.
- [x] Compile and run the focused BridgeData regression suite; audit and explicitly stage only owned evaluator/test/ignore/plan paths; commit and push before invocation. The focused suite passed 62 tests.
- [ ] Run exactly one fresh ignored local evaluation; verify candidate/input/parent hashes, zero overlap, finite exact coverage, and no active process after completion.
- [ ] Write exact evidence handoff and narrow truth surfaces; audit, explicit-path commit, and push.

## Safety and Rollback

No download, video work, model training/tuning, candidate/checkpoint/parent/input/lifecycle mutation, promotion, renderer/Chronos/6FR work, robot action, manufacturing, deletion, reset, amend, or bulk staging. Local evidence must be Git-ignored and under 5 MiB. Preserve failed probes and receipts; if a cell lacks strict disjointness, lineage, case capacity, exact coverage, or frozen hashes, record the ineligible condition and stop rather than changing thresholds or rerunning.

## Next-Agent Pickup Notes

This is an observational robustness measurement, not a product integration. It may establish or limit stability across declared temporal/action contexts only. It cannot prove compositional object reasoning, visual grounding, policy/control/safety, long-horizon world modeling, native Chronos integration, or product readiness.

