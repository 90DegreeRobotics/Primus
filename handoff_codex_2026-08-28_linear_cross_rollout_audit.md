# Handoff - Linear-Amended Cross-Candidate BridgeData Rollout Audit

**Agent:** Codex
**Date:** 2026-08-28
**Status:** Completed, mixed result pending commit
**Branch:** `main`

## What Changed

- Added a train-only ordinary least-squares `LinearStateActionDeltaBaseline` in `CCF_Sovereign\src\real_data\bridgedata_evaluation.py`.
- Added `linear_state_action_delta_predictor` in `CCF_Sovereign\src\real_data\bridgedata_rollouts.py`.
- Exported the baseline and rollout predictor through `CCF_Sovereign\src\real_data\__init__.py`.
- Added the linear baseline to future one-step BridgeData candidate evaluation in `CCF_Sovereign\train_bridgedata_real_transition.py`.
- Added the linear baseline to frozen rollout stability and cross-candidate rollout evaluators.
- Added `CCF_Sovereign\evaluate_bridgedata_cross_candidate_rollout.py`.
- Added focused tests for the linear baseline, linear recursive rollout, and cross-candidate eligibility/semantics.
- Added `CCF_Sovereign\evaluation\bridgedata_cross_rollouts\` to `.gitignore`.
- Updated `README.md`, `STATUS.md`, and `plan_2026-08-28_0641_cross-candidate-rollout-audit.md`.

## Evidence Artifacts

Own-split rollout with linear baseline:

- Path: `CCF_Sovereign\evaluation\bridgedata_rollouts\rollout-20260828-linear-001\rollout_stability.json`
- Size: 1,598,206 bytes
- File SHA-256: `177fc39adecd5c86d12d029cfcb3feb3787e49f935065c249cbba758d0ce8ed5`
- Payload SHA-256: `daf0e64091ba4112c8f8474688a05d4f254567434bc22466383b9e84a574b536`

Cross-candidate rollout with linear baseline:

- Path: `CCF_Sovereign\evaluation\bridgedata_cross_rollouts\cross-rollout-20260828-linear-001\cross_rollout_stability.json`
- Size: 171,856 bytes
- File SHA-256: `2c8dd8c8930b968cebbac7c75403150a9ec1b861d14719171da6fbea088ac484`
- Payload SHA-256: `60b066d31bca385a28e9ae644d359e6c64470a50495dec5520c99afad8f7635e`

Both evidence runs recorded `no_training = true`, `no_candidate_creation = true`,
`no_checkpoint_mutation = true`, and `promotion_performed = false`.

## Own-Split Rollout Result

Acceptance was exact finite 256-case coverage plus strictly lower terminal RMSE
than the strongest explicit baseline at horizons 1, 2, and 5 on both protected
partitions. The new linear baseline became the strongest baseline in every
protected acceptance row.

| Candidate | Protected partition | h1 candidate / baseline | h2 candidate / baseline | h5 candidate / baseline | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| `001` | held-out episode | `0.02330470 / 0.02869983` | `0.03621472 / 0.04752394` | `0.06871445 / 0.08473087` | Pass |
| `001` | held-out task | `0.02560269 / 0.03217676` | `0.04416267 / 0.05435434` | `0.25796188 / 0.26388081` | Pass, fragile |
| `002` | held-out episode | `0.02743651 / 0.02959757` | `0.04146190 / 0.04651763` | `0.06704565 / 0.07559100` | Pass |
| `002` | held-out task | `0.02813865 / 0.03218402` | `0.04052966 / 0.04906598` | `0.07452113 / 0.08877005` | Pass |

## Cross-Candidate Result

Acceptance used the same h1/h2/h5 rule, but the source candidate supplied the
model and train-only baseline bank while the target candidate supplied protected
episode selections.

| Source -> Target | Target partition | h1 candidate / baseline | h2 candidate / baseline | h5 candidate / baseline | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| `001 -> 002` | held-out episode | `0.02553100 / 0.02950289` | `0.03972490 / 0.04621056` | `0.06327276 / 0.07417549` | Pass |
| `001 -> 002` | held-out task | `0.02759969 / 0.03219355` | `0.03889538 / 0.04905008` | `0.07225735 / 0.08690207` | Pass |
| `002 -> 001` | held-out episode | `0.02433691 / 0.02896147` | `0.04151295 / 0.04756683` | `0.07295690 / 0.08683047` | Pass |
| `002 -> 001` | held-out task | `0.02528228 / 0.03222317` | `0.04366414 / 0.05466903` | `0.26076429 / 0.26008270` | Fail |

The symmetric cross-candidate robustness claim is not established. Candidate
`002` failed candidate `001`'s target held-out-task h5 split by
`0.0006815841557626` RMSE.

## Cross Semantics

| Source -> Target | Target partition | Selected episode overlap | Train episode overlap | Source-train task overlap | Strict unseen task relative to source |
| --- | ---: | ---: | ---: | ---: | --- |
| `001 -> 002` | held-out episode | 0 | 0 | 30 | false |
| `001 -> 002` | held-out task | 0 | 0 | 12 | false |
| `002 -> 001` | held-out episode | 0 | 0 | 26 | false |
| `002 -> 001` | held-out task | 0 | 0 | 5 | false |

This is episode-disjoint robustness evidence. It is not strict unseen-task
evidence relative to the source models.

## Commands Run

- `git status --short --branch`
- `git diff --stat`
- `git ls-files --deleted`
- `Get-Content -Raw C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `Get-FileHash -Algorithm SHA256 C:\Primus\CCF_Sovereign\evaluation\bridgedata_rollouts\rollout-20260827-001\rollout_stability.json`
- Parsed Manus rollout JSON and confirmed candidate IDs, horizons, flags, exact coverage, finite predictions, and protected metrics.
- `python -m compileall -q src\real_data\__init__.py src\real_data\bridgedata_evaluation.py src\real_data\bridgedata_rollouts.py train_bridgedata_real_transition.py evaluate_bridgedata_rollout_stability.py evaluate_bridgedata_cross_candidate_rollout.py test_bridgedata_evaluation.py test_bridgedata_rollouts.py test_train_bridgedata_real_transition.py test_evaluate_bridgedata_rollout_stability.py test_evaluate_bridgedata_cross_candidate_rollout.py`
- `python -m unittest -v test_bridgedata_evaluation test_bridgedata_rollouts test_train_bridgedata_real_transition test_evaluate_bridgedata_rollout_stability test_evaluate_bridgedata_cross_candidate_rollout`
- `python evaluate_bridgedata_rollout_stability.py --candidate-id bridge-real-20260827-001 --candidate-id bridge-real-20260827-002 --output-dir evaluation\bridgedata_rollouts\rollout-20260828-linear-001 --device cpu`
- `python evaluate_bridgedata_cross_candidate_rollout.py --candidate-id bridge-real-20260827-001 --candidate-id bridge-real-20260827-002 --output-dir evaluation\bridgedata_cross_rollouts\cross-rollout-20260828-linear-001 --device cpu`
- `Get-FileHash -Algorithm SHA256 C:\Primus\CCF_Sovereign\evaluation\bridgedata_rollouts\rollout-20260828-linear-001\rollout_stability.json`
- `Get-FileHash -Algorithm SHA256 C:\Primus\CCF_Sovereign\evaluation\bridgedata_cross_rollouts\cross-rollout-20260828-linear-001\cross_rollout_stability.json`

## Not Claimed

- No candidate promotion.
- No retraining.
- No checkpoint mutation.
- No parent mutation.
- No robot policy, robot control, safety, actuation, visual prediction, renderer,
  native Chronos integration, or product-readiness result.
- No reliable long-horizon claim; horizon 10 remains descriptive only.
- No strict unseen-task cross-candidate claim relative to the source model.
- No symmetric cross-candidate robustness claim.

## Remaining Dirty Or Untracked At Handoff Time

Known inherited items not part of this work:

- `CCF_Sovereign\README.md` shows modified in `git status`, but `git diff -- CCF_Sovereign/README.md` produced no content.
- `chronos_typed_operation_payload_plan.md`
- `plan_2026-08-27_0830_blender-renderer-witness.md`
- `plan_2026-08-27_1309_typed-operation-payload.md`

## Next Boundary

The next useful boundary is a stricter cross-candidate task split with zero
source-train task overlap, or a deliberately scoped Chronos integration step.
Do not promote either rejected candidate from this evidence.
