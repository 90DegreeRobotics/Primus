# Handoff — BridgeData Temporal and Action-Context Robustness

**Status:** Completed. One read-only broader robustness audit was run on the two frozen terminally rejected local predictors. The evidence is mixed: all 24 source/horizon/context rows had exact finite coverage and zero source-train task overlap; 19 paired-bootstrap rows passed, while five rows are indeterminate or a point-estimate failure. No candidate passes every declared context cell.

## Question Answered

This audit tested whether the existing strict source-train task-ID-disjoint short-horizon rollout advantage survives a predeclared partition of the same frozen target pools by **temporal position** and **recorded action-energy context**. It deliberately tests robustness rather than seeking another pooled favorable score.

Each frozen source candidate used its own strict 128-complete-episode target selection. Target task IDs were absent from that source model's train partition, and target episodes had no overlap with the source model's selected episodes. This is the same strict relative separation concept as the prior task-disjoint gate, extended with target-free context labels.

## Fixed Protocol

The evaluator used candidates `bridge-real-20260827-001` and `bridge-real-20260827-002` only, both terminally rejected with promotion false. Horizons were 1, 2, and 5. No horizon 10 result was sought.

A rollout case was labelled **early** or **late** by the episode-local source frame's relative position in its declared complete episode. It was labelled **low** or **high action energy** by its mean recorded action L2 norm relative to a median threshold fitted only from the corresponding source candidate's one-step training transitions. The source-train thresholds were approximately 1.0000000000005071 for candidate `001` and 1.000104155917288 for candidate `002`.

Each source/horizon/context cell selected exactly 128 deterministic episode-contained cases after strict eligibility. The case-selection seed was `20260828`; each cell required at least 10 distinct episode clusters. The model received an observed initial state and recorded actions, with all later state inputs recursively predicted. Baselines were copy-state, source-train action-only mean delta, source-train OLS state/action delta, and source-train nearest neighbor. The strongest baseline was selected separately per cell.

Every cell reported aggregate RMSE/MAE, coverage, finite prediction rate, source overlap checks, paired per-case residuals, and a 10,000-resample seed-`20260828` episode-clustered paired bootstrap. A positive interpretation requires both a lower point-estimate RMSE and a negative upper 95% paired MSE endpoint. A non-positive endpoint is **indistinguishable**, not silently counted as a pass.

## Measured Result

All 24 cells had exact finite 128-case coverage, zero source-selected episode overlap, zero source-train task overlap, and enough target episode clusters. Nineteen of 24 paired-bootstrap rows passed. The following five rows did not; all other declared rows passed.

| Source | Horizon | Context | Candidate RMSE | Strongest baseline | Baseline RMSE | RMSE margin | Point result | Paired MSE 95% interval | Bootstrap label | Selected episode clusters |
|---|---:|---|---:|---|---:|---:|---|---|---|---:|
| `001` | 1 | Early, high action energy | 0.0220184868404273 | Linear state/action delta | 0.0203473497560560 | -0.00167113708437127 | Fail | [-0.00000230116154814, 0.00015640362420915] | Indistinguishable | 79 |
| `001` | 2 | Early, high action energy | 0.0305523529197711 | Linear state/action delta | 0.0325004001838855 | 0.00194804726411440 | Pass | [-0.000270287576665781, 0.0000209228307912879] | Indistinguishable | 79 |
| `001` | 2 | Late, low action energy | 0.0500504379363793 | Linear state/action delta | 0.0535292365580626 | 0.00347879862168331 | Pass | [-0.000983740883073760, 0.000331531744714130] | Indistinguishable | 72 |
| `002` | 1 | Early, high action energy | 0.0199281037755165 | Linear state/action delta | 0.0208224284393072 | 0.000894324663790729 | Pass | [-0.000106583057978081, 0.0000249273982172637] | Indistinguishable | 78 |
| `002` | 5 | Late, low action energy | 0.0716559569750900 | Linear state/action delta | 0.0828037370117284 | 0.0111477800366384 | Pass | [-0.00335405183790542, 0.000456534572929651] | Indistinguishable | 76 |

The negative candidate `001` early/high h1 point result is a real limitation, not a defect to tune away. The other four rows show favorable point estimates but uncertainty that includes parity. Consequently the correct conclusion is not universal robustness. It is a **mixed context-robustness result**: broad support across most declared cells, with one measured local baseline loss and four statistically unresolved context/horizon cells.

## Preserved Preflight Finding

The initial no-model-scoring capacity probe correctly exposed a coordinate-assumption defect in the new evaluator. `BridgeDataRolloutCase.source_frame_index` is episode-local, whereas `EpisodeTask.dataset_from_index` is a global Parquet row offset. Subtracting the latter from the former falsely rejected valid cases.

The error receipt was preserved. A read-only lineage probe confirmed the local/global distinction from actual cases. The evaluator was corrected to use the episode-local `source_frame_index` with declared episode-length bounds retained. The focused regression fixture now uses a nonzero global metadata offset. A corrected capacity probe then established that every proposed source/horizon/context cell had 647–1,497 cases and 103–128 potential episode clusters prior to bounded selection.

The correction did not modify candidates, checkpoints, intake files, source-target eligibility, action-energy threshold rules, seeds, baseline definitions, or acceptance protocol.

## Evidence Binding and Integrity

| Binding | Value |
|---|---|
| Evaluator integration commit before audit | `bb657f57fb1dab9949b7b77c876b4c5bf1c8ffc9` |
| Context evidence path | `C:\Primus\CCF_Sovereign\evaluation\bridgedata_context_robustness\context-robustness-20260828-001\context_robustness.json` |
| Context evidence bytes | 1,289,065 |
| Context evidence SHA-256 | `692c80dfe9b0f958677f98c333c39afd021f7ed78714d910a219e1e793149f42` |
| Context evidence payload SHA-256 | `41ec2ab48567ebd65ecf6bd01d1835c2df652c6b99a91d405d402060d40470b3` |
| Strict feasibility receipt SHA-256 | `c56fb16e1fa6a45691af1d95240721c949d0bdcf3641a951315538fad8bcff54` |
| Frozen intake manifest SHA-256 | `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a` |
| Protected Council parent SHA-256 | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |
| Candidate 001 checkpoint SHA-256 | `ed03de679a4ae7304fc7ce2179f35fce1cc8ee4b0fb5e15f1198ac6595e87099` |
| Candidate 002 checkpoint SHA-256 | `209bf7ef3e2ff6faf3f25b4cd12f9711edb7d9227f686ce5a8627a215d09c7bb` |

The complete focused BridgeData gate passed: 62 tests, exit code 0. The evaluation remained local and ignored. Post-run verification found no active Primus Python process. Parent and intake hashes were unchanged. Both candidates remained rejected and promotion false.

## Correct Claim and Non-Claims

> On bounded source-train task-ID-disjoint observed rollout targets, the two frozen local predictors show broad but not universal advantage over explicit source-train-only baselines across predeclared temporal-position and recorded-action-energy contexts.

This is evidence for bounded short-horizon action-conditioned 7D state prediction under the described context partition only. It does not show a general local alternative to all large models, robust general-purpose world modeling, causal reasoning, semantic task understanding, vision, policy/control, safety, actuation, manufacturing, multi-step reliability beyond horizon five, native Chronos integration, product readiness, or promotion eligibility.

## Repository State and Next Steps

Before documentation closure, `main` and `origin/main` both point to `bb657f57fb1dab9949b7b77c876b4c5bf1c8ffc9`. The known zero-content-diff status artifact remains `CCF_Sovereign/README.md`; the three inherited root renderer/Chronos plans remain unstaged and unchanged.

The immediate next engineering boundary is **not** retuning the predictors to remove unfavorable cells. It is to define a semantic adapter contract between the 7D state/action predictor and Chronos2 that preserves numerical provenance and rejects unknown coordinate semantics. Native Chronos work must remain non-recipe, evidence-bound, and isolated from frozen predictor/candidate artifacts. A visible bridge, safety boundary, and buyer-facing demonstration must not overtake that contract or reinterpret mixed robustness as product readiness.
