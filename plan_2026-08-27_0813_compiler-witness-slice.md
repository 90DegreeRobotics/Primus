# Plan — deterministic compiler witness slice

**Created:** 2026-08-27 08:13 CDT
**Owner:** Manus, under Michael Holt’s autonomous-progress directive
**Repository:** `C:\Primus` / `main`
**Status:** EXECUTION COMPLETE — real compiler regression and one observed receipt passed; documentation handoff and closure remain

## Goal

Produce the smallest valid observed compiler witness from a typed generated `WorldProgram` without touching `chronos2`, rendering, training, candidates, or protected checkpoints. The existing witness path lowers a program to S3V, invokes `C:\chronos2\target\release\chronos.exe s3v validate`, independently verifies the Primus title-envelope round-trip, binds each declared capability against `C:\chronos2\data\capability_ledger.json`, and writes a hash-bound report only to a fresh ignored `Primus` destination.

Observed means only that the local compiler binary executed against the generated S3V artifact. It does not mean the scene was rendered, visually correct, physically simulated, learned, or promoted.

## Files to read

- [x] `AGENTS.md`, Charter, Git/process/parent-hash baseline
- [x] `CCF_Sovereign/src/world_compile/witness.py`
- [x] `CCF_Sovereign/test_world_compiler.py`
- [x] Compiler/ledger path presence on the workstation
- [ ] Existing compiler handoffs and result evidence relevant to active capability bindings

## Planned work

- [x] Run the existing real compiler regression suite. All 13 tests passed with no skips, including valid observed receipt, title-envelope counterexample, malformed JSON rejection, and whole-dataset hash binding.
- [x] Create a unique ignored temporary witness runner that loads one deterministic generated program, calls only the existing `witness_dataset` public API, and writes its report beneath `CCF_Sovereign/tmp/`.
- [x] Inspect the report: `trajectory_train_00000` compiled with exit code 0, `observed` evidence label, true envelope round trip, program SHA-256 `485dc18e60f0262258c5f685152a8bd8d927db4be122740a3257e01c31699983`, and S3V SHA-256 `4d8320693c2d107d5939442b793050ba8a149a6a75a353a2b9bdbe73b56232d4`. The ledger bound `geometry_core_primitives` only by explicit normalized match to available `geometry.core_primitives`; no render/learning/promotion claim exists.
- [x] Protected live/frozen parent hashes remain `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`; no `chronos2` path was modified. Preserve the real-suite and one-witness logs.
- [ ] Update this plan and write a handoff. If no repository code changed, do not create a code commit; commit only verified documentation closure if necessary.

## Constraints and rollback

No writes under `C:\chronos2`; no renderer/model invocation; no candidate creation; no checkpoint, corpus, capability-ledger, or source-dataset modification; no promotion. All generated S3V artifacts/reports go to a unique ignored `CCF_Sovereign/tmp/` directory that must not exist before execution. Any compiler rejection or unavailable capability is recorded as such and never relabeled observed success.

## Test gate

```powershell
cd C:\Primus\CCF_Sovereign
python test_world_compiler.py
```

A passing exit code is insufficient alone: the real compiler tests must not be skipped, the valid receipt must have `evidence_label="observed"`, exit code 0, and a true independent envelope round trip. The output report must retain `render_observed=false`, `visual_correctness_proven=false`, `learned_world_dynamics_proven=false`, `model_training_started=false`, and `candidate_promoted=false`.
