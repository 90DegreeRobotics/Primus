# Handoff — Lane A, Phase 1 compiler witness

**Date:** 2026-08-26
**Prepared by:** Claude (Opus 5) — Lane A owner, acting director
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\Primus` (write), `C:\chronos2` (read-only, no build)
**Starting HEAD:** `856df203dbb3adeff10e351eaee20f3ba8063166`
**Promotion status:** No candidate promoted, no training started, no checkpoint touched

## 1. What this proves, and what it does not

**Proven by execution:** all 21 Stage 2 smoke programs are accepted by the real
ChronoSophia compiler, and their Primus envelopes survive the S³V round trip.
The receipts are labelled `observed` because `chronos.exe` actually ran.

**Not proven, and not claimed:** nothing was rendered. No pixels were produced,
no render hash exists, and no visual-correctness claim is made. Compiler
validity is structural acceptance only.

## 2. Two measured findings

### 2.1 Capability status was asserted, never verified

`src/world_schema/trajectory_generator.py:436-437` hardcodes every operation:

```python
capability_id="geometry_core_primitives",
capability_status=CapabilityStatus.AVAILABLE,
```

No module under `src/world_schema/` reads `data/capability_ledger.json`. The
ledger identifier is `geometry.core_primitives` (dot); the fixtures emit
`geometry_core_primitives` (underscore), so the two never bound, even by string
equality. All 21 programs assert `available` across four distinct geometry
families — `box_grammar`, `lathe`, `compound`, `sweep` — under that single
identifier. The ledger holds 12 available and 17 unavailable routes.

`WORLD_SCHEMA_V1.md` already stated the design law — *the world schema does not
turn an unavailable ledger entry into an executable promise* — and its
non-claims section was honest that fixtures had not been compiled. **The
boundary was documented; the enforcement did not exist.** This is the gap
Phase 1 was created to close, not a defect introduced by Lane B.

Now enforced: `bind_capabilities()` resolves every declared capability against
the ledger, records ledger status, and marks whether the match was exact or
only normalized. Every receipt in this dataset records `exact_match: false`.

**Residual risk, not resolved here:** four geometry families all claim the one
`core_primitives` capability. The ledger cannot confirm that `sweep` or
`compound` legitimately fall under it. Family-level capability binding is
follow-on work.

### 2.2 Compiler acceptance does not imply Primus payload integrity

Measured against the real binary:

| Artifact | `s3v validate` exit | Meaning |
|---|---:|---|
| Unmodified fixture | 0 | accepted |
| `version` set to 99 | **0** | unknown version not checked |
| Title envelope destroyed | **0** | **envelope not checked at all** |
| Malformed JSON | 1 | rejected |
| Entity map replaced by list | 1 | rejected on type |

The Primus `WorldProgram` is carried inside the S³V *title* envelope. The
compiler accepts a plan whose envelope has been destroyed, reporting
`valid: 4 entities, 9 actions`. **A zero exit code therefore says nothing about
whether the Primus payload survived.** The witness verifies envelope round trip
independently and only reports `witnessed` when both hold. This is covered by
`test_compiler_acceptance_does_not_prove_envelope_integrity`, which runs the
real binary and will fail loudly if the compiler is ever hardened.

## 3. What was built

| Path | Purpose |
|---|---|
| `CCF_Sovereign/src/world_compile/witness.py` | Ledger binding, compiler execution, hash-bound receipts, failure taxonomy |
| `CCF_Sovereign/src/world_compile/__init__.py` | Package exports |
| `CCF_Sovereign/compile_world_programs.py` | Explicit-destination CLI; refuses an existing output directory |
| `CCF_Sovereign/test_world_compiler.py` | 13 fail-hard tests including real-compiler cases |

`FailureClass` contains only classes a real execution has produced. Nothing was
added speculatively.

## 4. Verification performed

Every command run from `C:\Primus\CCF_Sovereign`.

| Gate | Result |
|---|---|
| `python -m compileall -q src\world_compile compile_world_programs.py test_world_compiler.py` | exit 0 |
| `python test_world_compiler.py` | **13 tests, OK** |
| `python test_world_schema.py` | 8 tests, OK |
| `python test_world_trajectory_generator.py` | 7 tests, OK |
| `python test_candidate_training.py` | 4 tests, OK |
| `python test_mvp.py` | 6 tests, OK |

**38 tests across five suites, all passing.**

## 5. Witness artifact

Ignored local artifact at `CCF_Sovereign/tmp/compiler_witness_20260826_2210/`.

| Signal | Result |
|---|---:|
| Programs witnessed | 21 |
| Compiler accepted | 21 |
| Envelope round trip intact | 21 |
| `witnessed` (both conditions) | 21 |
| Capability-executable | 21 |
| Failure histogram | `{"none": 21}` |
| Report SHA-256 | `727d7ae7c65483bcaabc4485a710e85a45a734c8215cf418b5f07b87e88b492f` |
| Ledger SHA-256 | recorded in report |
| `render_observed` | **false** |

## 6. chronos2 boundary honoured

Read-only. **No `cargo build` was run** — the existing release binary
`C:\chronos2\target\release\chronos.exe` (2026-08-25, 27,752,448 bytes) was
executed instead, so nothing was written into another builder's `target/`. No
file under `C:\chronos2` was created, modified, or deleted.

## 7. Render witness — deliberately not attempted

The render path is `chronos.exe first-light`, which requires the full
ChronoSophia stack (a local model plus Blender) and writes into the product
output tree. That is outside the Lane A read-only boundary and needs per-item
operator approval. **No render was attempted, no render hash is claimed, and
nothing is labelled `observed` on the basis of rendering.** The witness report
records `render_witness_attempted: false` with the reason inline.

Phase 1 is therefore **half delivered by design**: the compiler witness is real
and complete; the render witness is blocked pending operator approval to run
the render stack.

## 8. TRUTH-SURFACE REQUEST

For the director (Lane D) to merge. Proposed additions:

**`STATUS.md`** — new subsection under Stage 2:

> ### Phase 1 compiler witness
>
> Stage 2 world programs have been executed against the real ChronoSophia
> compiler. All 21 smoke programs are accepted by `chronos.exe s3v validate`
> and their Primus envelopes survive the S³V round trip. The witness binds each
> declared capability to `data/capability_ledger.json` rather than trusting the
> generator's hardcoded `available` status.
>
> Two boundaries are recorded. Capability status was previously asserted by the
> generator and bound to nothing; it is now resolved against the ledger, and
> every current fixture matches only after identifier normalization. Compiler
> acceptance does not imply Primus payload integrity — `s3v validate` accepts a
> plan whose title envelope has been destroyed — so envelope round trip is
> verified separately.
>
> **Nothing has been rendered.** No render hash exists, no visual-correctness
> claim is made, no training was started, no checkpoint was modified, and no
> candidate was promoted.

**`README.md`** — one line under the developer commands:

> `python compile_world_programs.py --dataset <jsonl> --output <new-dir> --workdir <scratch>`
> — witness Stage 2 programs through the real ChronoSophia compiler.

## 9. Non-claims

This lane did not train, did not touch checkpoints, did not promote, did not
render, and does not assert that any fixture is physically or visually correct.
The protected parent remained `5e36cc9a…` throughout.

## 10. Commit window

**Per charter §2, Codex must re-run this lane's gates before any Lane A
commit. I do not self-certify Lane A.**

Requested pathspecs:

```text
CCF_Sovereign/src/world_compile/__init__.py
CCF_Sovereign/src/world_compile/witness.py
CCF_Sovereign/compile_world_programs.py
CCF_Sovereign/test_world_compiler.py
plan_2026-08-26_2158_claude-lane-a-compiler-render-witness.md
handoff_claude_2026-08-26_lane-a-compiler-witness.md
```

**Blocked:** `git add` is currently denied by the session's auto-mode
classifier. No staging, commit, or push has occurred. The operator must either
grant the permission or perform the commit. Nothing in this handoff assumes it
landed.

## 11. Next-agent pickup notes

1. Render witness needs operator approval to run the ChronoSophia render stack.
2. Family-level capability binding — four geometry families share one
   capability identifier (§2.1).
3. Consider raising the identifier mismatch with Lane B: emitting
   `geometry.core_primitives` verbatim would make the binding exact.
4. `s3v validate` ignores the `version` field. That is a chronos2 observation,
   filed here, not acted on — chronos2 is read-only for this lane.
