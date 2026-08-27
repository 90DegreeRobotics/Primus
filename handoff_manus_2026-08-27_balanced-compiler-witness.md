# Handoff — balanced compiler witness

**Repository:** `C:\Primus` / `main`

A fresh bounded sample selected four manifest-bound generated programs from train and each whole-family holdout. The real local Chronos validator executed **16/16** successfully. The ignored local report is `CCF_Sovereign/tmp/compiler_witness_balanced_20260827_0820/compiler_witness.json`.

| Evidence | Result |
|---|---:|
| Programs | 16 total; 4 per split |
| Compiler present | true |
| Observed receipts / witnessed envelope round trips | 16 / 16 |
| Compiler failures | 0 |
| Executable capability bindings | 16 |
| Render observed | false |
| Model training started / candidate promoted | false / false |

The fixed source JSONL and manifest are SHA-256 `3fbcedd9a7b5316945bec224d1ab09a59dcef4b5e5c4ff1d2ca22db59afbfb2a` and `1ee427195a3922c9e51f56a48a87311f5b974a109f9a25a042b2406c3bd46a41`. Every receipt has exit code zero, failure `none`, `observed` compiler-execution evidence, and true independent title-envelope round trip. Every capability binding is a recorded normalized—not exact—match from declared `geometry_core_primitives` to available ledger `geometry.core_primitives`.

This demonstrates only deterministic local compiler validation of the selected typed generated programs. It does not demonstrate renderer output, visual correctness, physical dynamics, external-world observation, learned dynamics, or promotion eligibility. No `chronos2` path, parent, frozen checkpoint, candidate, source data, or corpus was modified.

The next experiment must not silently broaden the claim. A complete compiler witness may be useful as a data-integrity artifact, but it adds little learning evidence beyond this balanced sample. The highest-value next frontier is renderer/observation integration with a separately authorized artifact destination; absent that safe surface, record the limit rather than manufacture observed visual evidence.
