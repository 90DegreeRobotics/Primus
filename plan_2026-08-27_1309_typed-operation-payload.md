# Plan — typed Stage 2 operation payload

**Status:** ACTIVE
**Owner:** Manus
**Goal:** Carry declared Stage 2 operation semantics from `WorldProgram` into typed S3V actions so native Chronos can reproduce geometry without parsing opaque notes or inventing defaults.

## Contract

Each bridge-authored S3V action will contain an explicit `operation` object with `operation_id`, `kind`, `subject_id`, optional `object_id`, optional `relation_id`, `parameters`, and evidence/provenance references. Values remain canonical JSON primitives. `notes` may retain human/audit metadata but is not an execution interface.

## Files to read

- `AGENTS.md`
- `CCF_Sovereign/src/world_schema/model.py`
- `CCF_Sovereign/src/world_schema/s3v_bridge.py`
- `CCF_Sovereign/test_world_schema.py`
- `CCF_Sovereign/test_world_trajectory_generator.py`

## Files to edit

- `CCF_Sovereign/src/world_schema/s3v_bridge.py`
- Focused Primus S3V bridge regression test(s)
- `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md` if contract behavior changes

## Ordered steps

- [ ] Define the exact payload schema and invariants.
- [ ] Emit the payload from every `WorldOperation`.
- [ ] Recover it in `from_s3v_dict` and preserve canonical round trip.
- [ ] Add fail-hard tests covering `extrude_face` parameters and non-opaque execution fields.
- [ ] Run focused bridge/schema tests and `git diff --check`.
- [ ] Commit only verified Primus paths; preserve unrelated untracked plans.

## Acceptance gate

The emitted action for `extrude_face` must expose the declared selector and parameter mapping in typed JSON. `assert_lossless_round_trip` must pass. No Dreamer consumer may require parsing `notes`.

## Rollback

Revert only this logical commit; do not alter datasets, compiler receipts, candidates, checkpoints, or existing direct Blender evidence.

## Next-agent note

Chronos currently has uncommitted native bootstrap/import wiring. Do not run another native witness until the typed payload has passed both producer and consumer gates.
