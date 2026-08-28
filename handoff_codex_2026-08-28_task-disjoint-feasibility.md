# Handoff - Task-Disjoint BridgeData Cross-Rollout Feasibility

**Agent:** Codex
**Date:** 2026-08-28
**Status:** Completed, feasible pending commit
**Branch:** `main`

## What Changed

- Added `CCF_Sovereign\evaluate_bridgedata_task_disjoint_feasibility.py`.
- Added `CCF_Sovereign\test_evaluate_bridgedata_task_disjoint_feasibility.py`.
- Added `CCF_Sovereign\evaluation\bridgedata_task_disjoint_feasibility\` to `.gitignore`.
- Updated `README.md`, `STATUS.md`, and `plan_2026-08-28_0845_task-disjoint-cross-feasibility.md`.

The scanner verifies the two frozen rejected BridgeData candidate manifests and
the frozen intake, then counts task-disjoint target episode capacity. It does
not derive predictions, train, evaluate a model, create a candidate, mutate a
checkpoint, or authorize promotion.

## Evidence Artifact

- Path: `CCF_Sovereign\evaluation\bridgedata_task_disjoint_feasibility\task-disjoint-feasibility-20260828-001\task_disjoint_feasibility.json`
- Size: 6,844 bytes
- File SHA-256: `c56fb16e1fa6a45691af1d95240721c949d0bdcf3641a951315538fad8bcff54`
- Payload SHA-256: `cef9aa4e3ce14dd8ea6883d8e373a332dc570537218a990727de6851f18bd62a`

The evidence records `no_training = true`, `no_candidate_creation = true`,
`no_checkpoint_mutation = true`, and `promotion_performed = false`.

## Result

Strict target pools exclude all source-selected episodes and all source-train
task IDs. Feasibility requires at least 256 rollout cases and at least 10
distinct episode clusters at horizons 1, 2, and 5.

| Source candidate | Source selected episodes | Source train tasks | Strict target episode clusters | Strict target tasks | h5 case capacity | Feasible |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `001` | 453 | 269 | 23,124 | 14,480 | 715,495 | yes |
| `002` | 476 | 293 | 23,973 | 14,462 | 732,461 | yes |

Both source reports had zero selected-episode overlap and zero source-train task
overlap in the strict target pool.

## Commands Run

- `git status --short --branch`
- `git diff --stat`
- `git ls-files --deleted`
- `rg -n "C:\\Primus|Primus repo law|candidate|BridgeData|rollout uncertainty|linear rollout" C:\Users\m\.codex\memories\MEMORY.md`
- `Get-Content -Raw AGENTS.md`
- `Get-Content -Raw C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `Get-Content -Raw handoff_manus_2026-08-28_cross-rollout-uncertainty.md`
- `Get-FileHash -Algorithm SHA256 C:\Primus\CCF_Sovereign\evaluation\bridgedata_cross_rollout_uncertainty\cross-rollout-uncertainty-20260828-001\cross_rollout_uncertainty.json`
- Parsed the uncertainty JSON and confirmed the 12 audited rows, exact 256-case coverage, 54-62 clusters, and the final row's `indistinguishable` label.
- `python -m compileall -q evaluate_bridgedata_task_disjoint_feasibility.py test_evaluate_bridgedata_task_disjoint_feasibility.py`
- `python -m unittest -v test_evaluate_bridgedata_task_disjoint_feasibility`
- `python evaluate_bridgedata_task_disjoint_feasibility.py --candidate-id bridge-real-20260827-001 --candidate-id bridge-real-20260827-002 --output-dir evaluation\bridgedata_task_disjoint_feasibility\task-disjoint-feasibility-20260828-001`
- `Get-FileHash -Algorithm SHA256 C:\Primus\CCF_Sovereign\evaluation\bridgedata_task_disjoint_feasibility\task-disjoint-feasibility-20260828-001\task_disjoint_feasibility.json`

## Not Claimed

- No strict task-disjoint model comparison has been run yet.
- No candidate promotion.
- No retraining.
- No checkpoint, parent, or input mutation.
- No robot policy, control, safety, actuation, visual prediction, renderer,
  native Chronos integration, reliable long-horizon, or product-readiness claim.

## Remaining Dirty Or Untracked At Handoff Time

Known inherited items not part of this work:

- `CCF_Sovereign\README.md` shows modified in `git status`, but `git diff -- CCF_Sovereign/README.md` produced no content.
- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`

## Next Boundary

The next valid boundary is a separately planned strict task-disjoint
cross-candidate evaluation that uses this feasible pool, freezes the allocation
before scoring, includes the linear and nearest baselines, and keeps the
terminal rejected candidates unpromoted.
