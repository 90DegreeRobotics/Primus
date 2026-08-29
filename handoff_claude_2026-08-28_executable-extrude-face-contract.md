# Handoff — Executable `extrude_face` Contract

**Agent:** Claude
**Date:** 2026-08-28
**Status:** Completed. Contract fixed, pushed, and consumed by a passing Chronos2 native witness.
**Branch:** `main`
**Starting commit:** `994e7b2f9bad69e0af9a1faae573d29082486692`
**Final commit:** see "Final Git State"

## The Problem, As Measured

Primus emitted a typed `action.operation` payload whose `parameters` were
`{extent_mm, bevel_q, variant}`. The native consumer in Chronos2,
`validate_typed_extrude_face`, requires the parameter key set to be exactly
`{selector, axis, distance_mm}` and refuses unknown keys. The sets were disjoint,
so **every** Primus emission was refused before dispatch.

This was measured, not inferred: a fresh emission from commit `994e7b2f` was
generated and its payload read directly.

```json
"parameters": {"bevel_q": 30, "extent_mm": 656, "variant": 0}
```

Two inherited claims were also corrected:

1. `plan_2026-08-28_1515_typed-s3v-operation-emission.md` states the production
   generator "currently declares only `distance_mm`". It declared none of the
   three required keys. The `selector`/`axis` values existed only in a test
   fixture, never in the production path.
2. The Chronos2 handoffs recorded that `rg --files` found no `.s3v.json` under
   `C:\Primus`. Thirty-eight exist, under the git-ignored `CCF_Sovereign/tmp/`
   root that ripgrep skips by default. The conclusion — no usable witness input —
   still held, because all thirty-eight predate typed emission and contain no
   `operation` key at all, but the stated reason was wrong.

## What Changed

One dict was doing two unrelated jobs. It is now two.

| Location | Holds | Consumer |
|---|---|---|
| `GeometryInvocation.parameters` | `{selector, axis, distance_mm}` | the native geometry executor |
| `WorldOperation.parameters` | `{extent_mm, bevel_q, variant}` | `temporal_witness` learning features |

The axis is derived from state the generator already holds, so no new RNG draw
shifts the stream:

```python
geometry_axis = f"{'positive' if direction > 0 else 'negative'}_{'xyz'[variant % 3]}"
```

`distance_mm` is the already-drawn `geometry_extent` (`120..680`, inside the
consumer's `1..=10000` bound). Nothing was invented per macro.

`temporal_witness` now reads the knobs from `operation.parameters`. Feature
values, ranges, and the emitted witness vector are numerically identical before
and after; only their location in the program moved.

`GENERATOR_VERSION` moved `1.1.0 → 1.2.0`.

## Files Touched

| File | Change |
|---|---|
| `CCF_Sovereign/src/world_schema/trajectory_generator.py` | contract split, axis derivation, `FACE_SELECTOR`, version bump |
| `CCF_Sovereign/src/world_data/temporal_witness.py` | read knobs from the operation, not the invocation |
| `CCF_Sovereign/test_world_trajectory_generator.py` | 2 new contract tests |
| `CCF_Sovereign/test_temporal_state_witness.py` | 2 new provenance tests |
| `plan_2026-08-28_1901_executable-extrude-face-contract.md` | new |
| `STATUS.md` | two new result sections |
| this handoff | new |

## Known Consequence

Moving a value inside `WorldProgram` changes `program_sha256` and the structural
signature of regenerated synthetic programs. Checked before committing: no
tracked Primus document pins a synthetic `program_sha256`. The frozen BridgeData
real-data evidence lives in the separate `src/real_data` package and was not
touched. Existing local synthetic trees under `CCF_Sovereign/tmp/` were left in
place, not deleted; regenerate before consuming them.

## Gates Run

```pwsh
python -m compileall -q src\world_schema\trajectory_generator.py src\world_data\temporal_witness.py
python -m unittest test_world_schema test_world_trajectory_generator test_temporal_state_witness test_world_compiler test_world_ingestion test_world_state_transition_metrics test_world_transition_candidate test_delta_witness test_transition_metrics
python -m unittest test_temporal_context_candidate test_temporal_context_normalization test_temporal_context_normalized_candidate test_temporal_delta_candidate test_chronos_transition_contract
```

Compile gate exited `0`. **66 tests passed**, then **14 tests passed** — 80
total across the affected surface. Baseline before the change was 35 passing on
the four core suites; those 35 still pass.

Worth noting honestly: the pre-existing tests all still passed **after** the
contract change, because nothing asserted the geometry parameters at all. Four
new tests now lock the contract in both directions — the invocation must carry
exactly the executable keys, and the witness must fail closed rather than fall
back to reading them.

## Downstream Result

The Chronos2 native witness consumed this contract and passed. Input SHA-256
`30ed34ef5dae11477f3771891d1b42214de2ef23ef3bbe66d1d7eae01ae96cb9`, exit `0`,
Codex chain valid over 26 events, exactly one sealed `execute_code` dispatch
carrying `{positive_x, 656, face_by_normal, entity_subject}`, and no
`world_core_v1` notes marker anywhere in the Codex. The target mesh spans X
`-0.5 .. 1.156` against `-0.5 .. 0.5` for every other entity.

Details, the four Chronos2 defects fixed to get there, and the Dreamer
verb-coverage limit are in `C:\chronos2` commit `d97c7a58`,
`handoff_claude_2026-08-28_native-extrude-face-witness.md`.

## Local-Only Generated Evidence

Under the git-ignored `CCF_Sovereign/tmp/native_witness_20260828_1901/`:

| File | Bytes | SHA-256 |
|---|---:|---|
| `primus_extrude_face_witness.s3v.json` | 16,299 | `1cca3019fee5eec22678edf89f2b7ba0b6d7d394f9e0229d758f4e83efacb58e` |
| `primus_extrude_face_geometry_only.s3v.json` | 5,653 | `30ed34ef5dae11477f3771891d1b42214de2ef23ef3bbe66d1d7eae01ae96cb9` |

The second is a Primus `WorldProgram` reduced to its single geometry operation
and emitted through the production `s3v_bridge`. It is not hand-authored: the
entity table, action id, and typed payload are generator-produced, and
`from_s3v_json(to_s3v_json(program))` round-trips it exactly. The reduction drops
only operations the Dreamer cannot execute today.

## What Was Not Run

No training, evaluation, candidate creation, checkpoint mutation, or promotion.
`src/real_data` and the frozen BridgeData intake were not touched. No BridgeData
suite was re-run — the change cannot reach that package. No full `CCF_Sovereign`
test sweep; only the affected surface. No renderer or BlenderMCP work in this
repo.

## What Remains

- `README.md` still describes the S3V bridge in general terms and was not
  changed; it is not wrong, but it does not yet mention the executable contract.
- The other declared geometry macros (`assemble_parts` and the rest of the
  `GeometryMacro` enum) still emit only trajectory knobs and would be refused by
  a native consumer. Only `extrude_face` has an executable contract today.
- The Dreamer verb-coverage decision, recorded on the Chronos2 side.

## Final Git State

```text
C:\Primus     main  clean  HEAD == origin/main
C:\chronos2   main  clean  HEAD == origin/main
```

Exact hashes are printed in the done report for this session.

## Next Step

Give the remaining geometry macros the same executable-contract treatment, one
at a time, each paired with a Chronos2 consumer gate. Do not widen the typed
contract ahead of a consumer that can actually execute it.
