# Handoff — temporal-context normalization ablation

**Date:** 2026-08-27 CDT
**Prepared by:** Manus
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\Primus` / `main`
**Ablation code commit:** `28f0e5b473661ed9ae519b362e8718c4e5e1edf5`
**Candidate:** `temporal-context-20260827-0752-normalized-mlp`
**Lifecycle:** `completed`; promotion not performed

## Executive status

This fixed-data, fixed-split, equal-budget ablation tested whether train-only feature and positional-target normalization resolves the contextual generated-transition MLP’s underfitting. It does not resolve it. Normalization improved strict train complete-transition accuracy from 3.90625% to 7.03125% and reduced train position RMSE from 72.1068 mm to 50.3891 mm. But position generalization degraded across all three protected whole-family splits, and strict held-out complete-transition accuracy remained only 1.5625%–3.125%.

The factual diagnosis is therefore narrower than either success or failure rhetoric: **the original low score was not solely a raw numerical-scaling problem**. Train-only normalization gives a modest train-fit improvement but hurts all protected-split positional RMSE under the fixed 300-epoch, 8→32→32→5 budget. The relation outputs are learned well by both candidates. The remaining gap is a nontrivial transition-function/representation problem, not a result about observed dynamics, physical behavior, visual grounding, rendering, or a promotable replacement model.

## Fixed evidence contract

| Item | Value |
|---|---|
| Dataset JSONL SHA-256 | `3fbcedd9a7b5316945bec224d1ab09a59dcef4b5e5c4ff1d2ca22db59afbfb2a` |
| Dataset manifest SHA-256 | `1ee427195a3922c9e51f56a48a87311f5b974a109f9a25a042b2406c3bd46a41` |
| Temporal witness set SHA-256 | `18a408d656b62a08029b76cfca25d8a4b0ee930e561ff84a64c76ad830cf5de8` |
| Baseline candidate | `temporal-context-20260827-0742-mlp` |
| Baseline candidate configuration | MLP 8→32→32→5; 300 epochs; batch 16; learning rate 0.01; seed 20260827 |
| Ablation candidate configuration | Identical budget/configuration; only train-only input/position normalization added |
| Parent and frozen parent SHA-256 | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |

The new immutable normalization receipt was fitted on exactly 256 train witnesses. It binds its feature/position means, scales, train-program-set hash `5d2fa30abe08c90760698b550b46b42b939def48ceeda667d6287e22ad4176a7`, and SHA-256 `7788a78f52efa6e2d9834cd4f2f7e1c012f934a14c78d018969d8e3c36bb2984` into the candidate manifest. No held-out witness is used for receipt fitting.

## Result comparison

| Split | Raw MLP complete / RMSE | Normalized MLP complete / RMSE | Diagnosis |
|---|---:|---:|---|
| Train, 256 cases | 0.0390625 / 72.1068 mm | 0.0703125 / 50.3891 mm | Better train fit |
| Held-out object, 64 cases | 0.0625000 / 77.7611 mm | 0.0312500 / 88.7798 mm | Worse protected positional generalization |
| Held-out operation, 64 cases | 0.0156250 / 67.5604 mm | 0.0156250 / 89.3096 mm | Same strict score, worse positional generalization |
| Held-out composition, 64 cases | 0.0312500 / 70.8652 mm | 0.0156250 / 83.8121 mm | Worse protected positional generalization |

The static no-change baseline is identical for both arms, with zero strict complete-transition accuracy in every partition and position RMSE of 213.89–223.14 mm. The normalized candidate still materially beats that weak baseline and scores support accuracy 1.0 plus near accuracy 0.953125–1.0 in every split. Its strict coordinate target behavior is the limiting factor.

No pooled holdout score was calculated.

## Candidate evidence

| Signal | Observed value |
|---|---:|
| Device | NVIDIA GeForce RTX 3060 / CUDA |
| Candidate checkpoint SHA-256 | `acd89e1dc7791670afabf745022c5f20e8cf7dafa69c8b8c859a907acff0f8ac` |
| Checkpoint bytes | 12,008 |
| Epochs / batch / LR / updates | 300 / 16 / 0.01 / 4,800 |
| Training time | 20.921008399978746 seconds |
| Final normalized training loss | 0.014257696457207203 |
| Candidate status | `completed` |
| Promotion performed | false |

The strict restore smoke verified the candidate checkpoint hash and loaded the saved model with `weights_only=True`; it produced finite output shape `[1, 5]`. No matching process remains active.

The non-mutating policy decision is ineligible. It records no valid parent/candidate behavioral comparison, no `CANDIDATE_IMPROVES` verdict, non-positive pass delta, and no specific promotion authorization. It has `performs_mutation=false` and `automatic_promotion=false`. No promotion command was run.

## Commands and tests

| Gate | Result |
|---|---|
| Normalization code gate | Compile passed; 61 tests passed across schema, generator, ingestion, witness, metric, candidate safety, and both temporal-context candidate arms. |
| Candidate preflight | Clean synchronized repository, fixed source hashes, absent fresh candidate destination, unchanged live/frozen parent, CUDA available, no matching process. |
| Candidate execution | Completed with exit code 0; all baseline/model predictions, per-split metrics, normalization receipt, run summary, manifest, and checkpoint are isolated beneath the candidate directory. |
| Restore smoke | Completed with exit code 0. |
| Promotion policy | Completed with exit code 0; explicit ineligible non-mutation decision. |

## TRUTH-SURFACE REQUEST

**Target:** `STATUS.md` (director/operator-owned)

> **Generated temporal-context normalization ablation completed; no learned-world or promotion claim.** On the fixed 448-program generator-v1.1 dataset and identical 8→32→32→5, 300-epoch candidate budget, train-only feature/target normalization improved train strict complete-transition accuracy from 3.90625% to 7.03125% and reduced train position RMSE from 72.1068 mm to 50.3891 mm. It worsened positional RMSE in all three protected whole-family splits and did not achieve high strict held-out accuracy. Both arms beat the static no-change baseline and learned generated relation outcomes, but neither solves the generated contextual coordinate rule. This diagnoses numerical scaling as insufficient under the tested budget. It does not demonstrate observed/physical dynamics, visual or compiler/render correctness, general world learning, or a promotable candidate. Parent/frozen hashes are unchanged and no candidate was promoted.

## Next factual action

Do not scale this MLP or claim capability. The next clean experiment should preserve this source data and metric while testing **rule-compatible representation**: predict the context-derived action delta as a structured intermediate latent target from the allowed inputs, then compose it with the pre-state through a fixed nonlearned addition layer. The model still would not receive the delta as an input; it would predict it as an output. This separates deterministic state composition from learning the branch/modulo/context rule and makes errors attributable. Use equal resource budgets and fresh candidate IDs, report intermediate-delta and final-state metrics by split, and retain no promotion.

Before that work begins, commit this handoff and the updated ablation plan as a documentation-only closure unit. Keep all datasets, candidate artifacts, helper scripts, logs, and checkpoints local and ignored.
