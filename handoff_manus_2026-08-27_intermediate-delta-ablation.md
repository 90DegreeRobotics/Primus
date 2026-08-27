# Handoff — intermediate-delta representation ablation

**Repository:** `C:\Primus` / `main`
**Code commit:** `b78696f917ca2967cd6f745d6db7c4b01064c2f0`
**Candidate:** `temporal-delta-20260827-0801-mlp` / `completed`
**Promotion:** not performed; policy ineligible and non-mutating

## Result

This equal-budget generated ablation changes only the output representation: the MLP predicts a typed transform delta from the existing eight safe pre-state/context features; fixed addition composes that output with known pre-state to form the final translation. The generated transform delta is an output target only, never an input. The source is the fixed 448-program manifest-bound dataset (`3fbcedd9a7b5316945bec224d1ab09a59dcef4b5e5c4ff1d2ca22db59afbfb2a` / manifest `1ee427195a3922c9e51f56a48a87311f5b974a109f9a25a042b2406c3bd46a41`).

| Split | Delta MLP complete accuracy | Delta MLP RMSE | Raw-context MLP complete accuracy / RMSE |
|---|---:|---:|---:|
| Train (256) | 0.04296875 | 51.6716 mm | 0.0390625 / 72.1068 mm |
| Held-out object (64) | 0.03125000 | 54.8293 mm | 0.0625000 / 77.7611 mm |
| Held-out operation (64) | 0.07812500 | 53.0897 mm | 0.0156250 / 67.5604 mm |
| Held-out composition (64) | 0.09375000 | 56.2789 mm | 0.0312500 / 70.8652 mm |

The arm improves position RMSE across train and every protected split against the raw-context arm and increases strict complete-transition accuracy in operation and composition holdouts. It remains poorly fitted in absolute terms: train accuracy is only 4.3%, so this is not a robust generalization result. Support accuracy is 1.0 and near accuracy 0.953125–1.0 in all splits. The static no-change baseline still has zero complete-transition accuracy and 213.89–223.14 mm RMSE.

## Integrity and gates

The full representation gate passed: compile plus **65 tests** across the affected schema, generator, ingestion, witness, metric, candidate safety, temporal-context, normalization, and delta paths. The candidate ran on CUDA with the fixed MLP budget (8→32→32→5; 300 epochs; batch 16; learning rate 0.01; 4,800 updates). Final loss was `0.0031039416790008545`.

The candidate checkpoint is SHA-256 `d405bace1d1448c96261e0a38384f029bbb632aa8dcb7a6c254491dd5c4e70f7`; strict restore succeeded with finite output shape `[1, 5]`. Live and frozen parent SHA-256 remain `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`. No matching process remains active. The non-mutating policy record is SHA-256 `606ea5cb68e401fa0f086a318c4045add0179f26661fc0080d80a9b5fa27fc4e`; it is ineligible and has no mutation path.

## Boundary and next action

This demonstrates a **generated typed context-to-delta positive-control improvement**, not observed dynamics, physics, rendering, general world learning, or a promotable candidate. The persistent low train strict accuracy means a larger MLP is not yet the right next move.

The next high-value work should add one compiler-executed/renderer-verified witness slice and retain the exact manifest/whole-family contracts. First validate compiler availability and identify an executable, deterministic artifact whose observation hashes can enter the existing compiler-witness path. If no compiler/render surface is executable, record that blocker rather than manufacturing `observed` evidence.
