# Plan — intermediate-delta representation ablation

**Created:** 2026-08-27 08:01 CDT
**Owner:** Manus, under Michael Holt’s autonomous-progress directive
**Repository:** `C:\Primus` / `main`
**Status:** ACTIVE — intermediate-delta representation and equal-budget runner passed the complete 65-test matrix; audit, code commit, and isolated candidate execution remain

## Goal

Determine whether the normalized temporal-context MLP’s poor protected-split coordinate accuracy arises from asking it to learn both a context-dependent generated delta rule and state composition jointly. This ablation will retain the exact same eight allowed pre-state/context inputs, train partition, source dataset, MLP capacity, seed, optimizer, epochs, batch size, and 25-mm final-state metric. It will change the **output representation only**: the model predicts the declared generated x/y/z transform delta as an intermediate supervised target, and a fixed nonlearned layer composes that predicted delta with the known pre-state to form the final translation. Relation outputs remain learned as before.

The transform delta is an **output target**, never an input. The candidate receives no direct target/delta, final state, final relations, split, object class, operation family, ID, evidence URI, or hash. It remains a generated rule-learning ablation, not observed/physical world learning. No promotion is permitted.

## Fixed inputs and budget

| Item | Reference |
|---|---|
| Dataset JSONL | `3fbcedd9a7b5316945bec224d1ab09a59dcef4b5e5c4ff1d2ca22db59afbfb2a` |
| Dataset manifest | `1ee427195a3922c9e51f56a48a87311f5b974a109f9a25a042b2406c3bd46a41` |
| Temporal witness set | `18a408d656b62a08029b76cfca25d8a4b0ee930e561ff84a64c76ad830cf5de8` |
| Raw-context baseline | `temporal-context-20260827-0742-mlp` |
| Normalized baseline | `temporal-context-20260827-0752-normalized-mlp` |
| Model/budget | MLP 8→32→32→5; seed 20260827; 300 epochs; batch 16; AdamW 0.01; 4,800 updates |
| Parent/frozen hash | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |

## Files to add or edit

- [x] `CCF_Sovereign/src/world_data/delta_witness.py` — derive and validate delta outputs only from manifest-bound temporal witnesses and source declared operations
- [x] `CCF_Sovereign/train_temporal_delta.py` — equal-budget isolated output-delta candidate runner with fixed pre-state composition and separate split metrics
- [x] `CCF_Sovereign/test_delta_witness.py` — no-delta-input, exact rederivation, and split-preservation tests
- [x] `CCF_Sovereign/test_temporal_delta_candidate.py` — exact coverage, output composition, train-only fit, and candidate metric tests
- [ ] `plan_2026-08-27_0801_intermediate-delta-ablation.md` and final handoff

No parent/frozen checkpoint, source dataset, existing candidate, corpus, compiler/render surface, `chronos2`, or foreign worktree file may be changed. Candidates, helpers, logs, and outputs remain ignored and local.

## Ordered work

- [x] Implement a typed delta witness that accepts a manifest-bound temporal witness result and rederives each declared `SET_TRANSFORM` delta. Feature names remain the current eight-feature context contract; target names identify the three delta outputs plus final relations.
- [x] Implement a runner with the exact MLP and resource budget. It trains on train-only delta targets, composes predicted delta plus known pre-state through fixed addition, and scores final state and relations per split without pooled holdouts.
- [x] Add fail-hard tests and run all relevant prior gates. The preserved complete gate passed: compile plus 65 tests across current schema/generator/ingestion/witness/metric/candidate contracts and the two new delta suites. Audit, commit, and push remain.
- [ ] Execute one fresh-ID candidate against the fixed dataset after clean parity, source hashes, parent hashes, destination absence, CUDA, and process checks. Preserve baseline/model predictions, manifests, checkpoint, restore smoke, non-mutating promotion decision, and source/artifact hashes.
- [ ] Publish only the factual outcome. A high score demonstrates a generated, typed context-to-delta mapping under held-out families; it does not prove observed or physical world dynamics, rendering, general intelligence, or promotion eligibility.

## Rollback and next-agent notes

Do not reuse candidate IDs or output directories. Preserve failures. Do not reset, force-push, clean, amend pushed commits, or promote. The normalized ablation is sealed at `a0902e68b4d66f884e84b15c599015ad3a193dbb` and shows modest train improvement but worse protected positional RMSE, so this plan isolates the output representation as the next causal variable.
