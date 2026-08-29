# Plan — Executable `extrude_face` Contract

**Date:** 2026-08-28 1901 CDT
**Status:** ACTIVE
**Scope:** Make the Primus-declared `extrude_face` geometry invocation carry the
parameters the operation actually needs to execute, so a Chronos2 native witness
can consume a Primus-emitted typed S3V without notes parsing or invented values.
Paired with `C:\chronos2\plan_2026-08-28_1901_native-witness-engine-fix.md`.

## Goal

Close a measured cross-repo contract split.

Primus emits a typed `action.operation` payload whose `parameters` are
`{extent_mm, bevel_q, variant}`. Chronos2 `validate_typed_extrude_face` requires
the parameter key set to be exactly `{selector, axis, distance_mm}`. The sets are
disjoint, so every Primus emission is refused before dispatch. This was measured,
not inferred — see "Measured Starting Evidence".

The fix is to separate two things that are currently conflated in one dict:

- **Executable geometry contract** — what the macro needs in order to run.
  Belongs in `GeometryInvocation.parameters`.
- **Declared trajectory knobs** — synthetic dataset values consumed by the
  temporal-witness learning path. Belongs in `WorldOperation.parameters`.

No learning feature value changes. No new random draw is introduced, so the
generator's RNG stream is unchanged.

## Non-Goals

This plan does not train, evaluate, promote, or mutate a candidate. It does not
touch `src/real_data`, the frozen BridgeData intake, or any rejected candidate.
It makes no claim about learned world modeling, policy, control, safety, or
product readiness.

## Measured Starting Evidence

Primus `main` at `994e7b2f9bad69e0af9a1faae573d29082486692`, clean,
`HEAD == origin/main`.

A fresh emission from the current committed path produced:

```json
"operation": {
  "schema_version": 1,
  "kind": "geometry_macro",
  "macro": "extrude_face",
  "family": "box_grammar",
  "subject_id": "entity_subject",
  "target_id": "entity_subject",
  "parameters": {"bevel_q": 30, "extent_mm": 656, "variant": 0}
}
```

Pre-existing on-disk S3V artifacts under `CCF_Sovereign/tmp/` (38 files) predate
the typed-emission commit `7057d459` and contain no `operation` key at all. They
are not usable as witness input and are not modified by this plan.

## Files to Read

- `AGENTS.md`, `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `README.md`, `STATUS.md`
- `CCF_Sovereign\src\world_schema\model.py`
- `CCF_Sovereign\src\world_schema\trajectory_generator.py`
- `CCF_Sovereign\src\world_schema\s3v_bridge.py`
- `CCF_Sovereign\src\world_data\temporal_witness.py`
- `C:\chronos2\crates\chronos_dreamer\src\typed_operation.rs`

## Files to Edit

- `CCF_Sovereign\src\world_schema\trajectory_generator.py`
- `CCF_Sovereign\src\world_data\temporal_witness.py`
- `CCF_Sovereign\test_world_schema.py`
- `CCF_Sovereign\test_world_trajectory_generator.py`
- `CCF_Sovereign\test_temporal_state_witness.py`
- `README.md`, `STATUS.md`, this plan, and a dated handoff

## Contract

The geometry invocation for `extrude_face` declares exactly:

| Key | Value | Rule |
|---|---|---|
| `selector` | `face_by_normal` | The only selector the consumer accepts |
| `axis` | signed cardinal token | Derived from existing declared state |
| `distance_mm` | `geometry_extent` | Integer already drawn in `120..680` |

`axis` is derived deterministically from state the generator already holds, so
no new RNG draw shifts the stream:

```text
axis = f"{'positive' if direction > 0 else 'negative'}_{'xyz'[variant % 3]}"
```

with the existing `direction = -1 if variant in (1, 4) else 1`.

The trajectory knobs move, unchanged in value, to the geometry operation's own
`parameters` dict:

```text
{"extent_mm": geometry_extent, "bevel_q": bevel_q, "variant": variant}
```

`temporal_witness` reads them from that dict instead. Feature values, ranges, and
the witness vector are numerically identical before and after.

## Known Consequence

Moving a value inside `WorldProgram` changes `program_sha256` and the structural
signature for regenerated synthetic programs. No tracked Primus document pins a
synthetic `program_sha256`, and the frozen BridgeData real-data evidence is in a
separate package that this plan does not touch. Any local synthetic dataset must
be regenerated to be consumed; existing local trees under `CCF_Sovereign/tmp/`
are left in place, not deleted.

## Ordered Steps

1. [ ] Capture clean baseline in both repos.
2. [ ] Record the measured refusal and the fresh-emission payload.
3. [ ] Edit `trajectory_generator.py` to split executable contract from knobs.
4. [ ] Edit `temporal_witness.py` to read knobs from the operation dict.
5. [ ] Update focused tests to assert the executable contract explicitly, and to
   prove the knobs still reach the witness unchanged.
6. [ ] Run `python -m compileall -q` on touched paths.
7. [ ] Run the focused suites: `test_world_schema`,
   `test_world_trajectory_generator`, `test_temporal_state_witness`,
   `test_world_compiler`.
8. [ ] Emit a fresh typed S3V and confirm the payload matches the Chronos2
   accepted shape by inspection.
9. [ ] Stage explicit paths, `git diff --check --cached`, commit, push `origin main`.
10. [ ] Update `README.md`, `STATUS.md`, and write the handoff.

## Test Gate

```pwsh
python -m compileall -q src\world_schema\trajectory_generator.py src\world_data\temporal_witness.py
python -m unittest test_world_schema test_world_trajectory_generator test_temporal_state_witness test_world_compiler
```

Baseline before edit: 35 tests passed.

## Rollback

No deletion, no history rewrite. If a gate fails, retain the dirty diff and the
failure record; do not stage or push. If the contract proves wrong downstream,
supersede it with a new forward commit.

## Next-Agent Pickup

After this pushes, the Chronos2 side must fix the Blender 4.5 render-engine
identifier before the native witness can run. Both bare `BLENDER_EEVEE`
assignments on the witness path are measured failures on Blender 4.5.4 LTS,
which reports `['BLENDER_EEVEE_NEXT']` as its only valid engine.
