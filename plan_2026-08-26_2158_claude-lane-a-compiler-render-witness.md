# Plan — Claude Lane A, Phase 1 compiler and render witness

**Created:** 2026-08-26 21:58 CDT
**Owner:** Claude (Opus 5) — Lane A, also acting director
**Charter lane:** A — Grounding, Phase 1 compiler + render witness
**Repository:** `C:\Primus` (write), `C:\chronos2` (read-only)
**Starting HEAD:** `856df203dbb3adeff10e351eaee20f3ba8063166`
**Starting parent SHA-256:** `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`
**Status:** COMPILER WITNESS COMPLETE — render witness blocked pending operator approval; commit window blocked by classifier

## Goal

Prove, by execution, whether Stage 2 `WorldProgram` fixtures actually compile
and render through the real ChronoSophia compiler — and record precisely where
they do not. Produce compiler receipts, S3V hashes, render hashes, and an
enumerated failure taxonomy, with evidence labels obeying charter §6.

Synthetic output is never labelled `observed`. A receipt is `observed` only if
`chronos.exe` actually ran and its output was hashed.

## Conflict of interest

I own this lane and also direct. Per charter §2, **Codex re-runs this lane's
gates before any Lane A commit.** I do not self-certify Lane A.

## Files read (no plan required)

- `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`
- `CCF_Sovereign/src/world_schema/{model,tokens,s3v_bridge,trajectory_generator}.py`
- `C:\chronos2\crates\chronos_s3v\src\lib.rs` (read-only)
- `C:\chronos2\crates\chronos_cli\src\main.rs` (read-only)
- `C:\chronos2\data\capability_ledger.json` (read-only)

## Owned paths — nothing else is edited

- `CCF_Sovereign/src/world_compile/__init__.py`
- `CCF_Sovereign/src/world_compile/witness.py`
- `CCF_Sovereign/compile_world_programs.py`
- `CCF_Sovereign/test_world_compiler.py`
- `docs/defense_evidence/grounding/**`
- this plan file, and `handoff_claude_2026-08-26_lane-a-compiler-witness.md`

## chronos2 boundary

**Read-only, and no build.** A prebuilt release binary already exists at
`C:\chronos2\target\release\chronos.exe` (2026-08-25, 27,752,448 bytes).
Lane A executes that existing binary and writes **no** output inside chronos2.
`cargo build` is NOT run — it would write `target/` inside another builder's
active repository. All compiler outputs go to an explicit new directory outside
both repos, or to an ignored `CCF_Sovereign/tmp/` path.

## Finding already established by reading (pre-work)

`trajectory_generator.py:436-437` hardcodes every operation's capability:

```python
capability_id="geometry_core_primitives",
capability_status=CapabilityStatus.AVAILABLE,
```

No file under `src/world_schema/` references `capability_ledger.json`. The
ledger's identifier is `geometry.core_primitives` (dot), the fixtures emit
`geometry_core_primitives` (underscore), so the two do not bind even by string
equality. All 21 smoke programs assert `available` across four distinct
geometry families — `box_grammar`, `lathe`, `compound`, `sweep` — under that
one identifier. The ledger records 12 available and 17 unavailable routes.

`WORLD_SCHEMA_V1.md` states the design law: *the world schema does not turn an
unavailable ledger entry into an executable promise*, and its non-claims
section is honest that fixtures have not been compiled or rendered. The
boundary is documented. **The enforcement mechanism does not exist.** Building
it is this lane's job. This is not a defect introduced by Lane B; it is the
open gap Phase 1 was created to close.

## Ordered steps

1. Confirm `chronos.exe` invocation surface (`s3v --help`, `s3v validate`).
   Record exact usage. No writes to chronos2.
2. Lower a Stage 2 fixture to S³V via the existing `s3v_bridge.py`; write the
   artifact to an explicit new scratch directory.
3. Run the real `s3v validate` against it. Capture stdout, stderr, exit code
   verbatim. Do not summarize.
4. Build `world_compile/witness.py`: bind each operation's `capability_id` to
   `capability_ledger.json`, run the compiler, and emit a hash-bound receipt
   recording command, exit code, artifact hashes, and evidence label.
5. Enumerate failure classes from real failures — unbound capability, ledger
   `unavailable`, S³V validation rejection, compiler error, renderer absent.
   A class is only listed once something actually produced it.
6. Attempt a render witness on a program whose capability is genuinely
   `available`. If pixels are produced, hash them and label `observed`. If the
   route does not exist, record that plainly and label nothing `observed`.
7. Write fail-hard tests covering each realized failure class plus the success
   path.
8. Write the handoff with a TRUTH-SURFACE REQUEST block. Request a commit
   window; have Codex re-run the gates first.

## Test gate

```powershell
cd C:\Primus\CCF_Sovereign
python -m compileall -q src\world_compile compile_world_programs.py test_world_compiler.py
python test_world_compiler.py
python test_world_schema.py
python test_world_trajectory_generator.py
```

The gate must include failure cases, not only successes. A gate that proves
only that valid input validates has not tested the boundary.

## Non-claims

This lane does not train, does not touch checkpoints, does not promote, does
not certify visual quality, and does not assert that any fixture is physically
or visually correct. Compiler validity is not visual correctness. A passing
`s3v validate` proves structural acceptance only.

## Rollback path

Only Lane A paths are created. No git state changes without a director-granted
window and Codex gate reproduction. Scratch artifacts live outside tracked
paths and are preserved, not deleted, unless the operator approves per item.

## Next-agent pickup notes

If interrupted, the first unfinished numbered step above is the pickup point.
The capability-binding finding stands regardless of how far the lane gets and
should be carried into any handoff.
