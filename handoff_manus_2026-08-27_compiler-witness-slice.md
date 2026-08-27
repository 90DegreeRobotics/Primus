# Handoff — deterministic compiler witness slice

**Repository:** `C:\Primus` / `main`
**Result:** one valid **observed compiler-execution** receipt; no render, model, candidate, or promotion work

The local `C:\chronos2\target\release\chronos.exe` was present and the existing real compiler suite completed **13 tests with no skips**. One bounded independent witness run then compiled generated program `trajectory_train_00000` through the repository public API. The report is ignored local evidence at `CCF_Sovereign/tmp/compiler_witness_one_20260827_0813/compiler_witness.json`.

| Signal | Observed value |
|---|---|
| Compiler command | `chronos.exe s3v validate trajectory_train_00000.s3v.json` |
| Exit / failure | `0` / `none` |
| Evidence label | `observed` |
| Envelope round trip | true |
| Program SHA-256 | `485dc18e60f0262258c5f685152a8bd8d927db4be122740a3257e01c31699983` |
| S3V SHA-256 | `4d8320693c2d107d5939442b793050ba8a149a6a75a353a2b9bdbe73b56232d4` |
| Ledger SHA-256 | `7c959240760bba54c384969e31ce3003aa4c311cc7165c72623cc8f4e07df15c` |
| Capability binding | normalized, not exact: `geometry_core_primitives` → available `geometry.core_primitives` |

The receipt is valid evidence that the local compiler executed and accepted one S3V lowering while the independent Primus envelope survived round trip. It is **not** evidence that the generated scene rendered, is visually/physically correct, was observed from an external world, trained a model, or merits promotion. The report explicitly preserves all those false claims as `false`.

Live and frozen parent SHA-256 remain `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`. No `chronos2` files were modified. The next safe scale-up is not rendering: execute a fresh bounded, partition-balanced multi-program compiler witness from the manifest-bound dataset, preserving individual receipts and never inferring renderer or physical evidence from validator success.
