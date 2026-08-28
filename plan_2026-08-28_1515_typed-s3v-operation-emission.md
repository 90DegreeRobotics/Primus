# Plan — Typed S3V Geometry-Operation Emission

**Date:** 2026-08-28 CDT  
**Status:** ACTIVE  
**Scope:** Add a direct, versioned typed `action.operation` payload to the Primus S3V bridge for existing `WorldOperation.geometry` records. This plan is paired with `C:\chronos2\plan_2026-08-28_1453_typed-operation-payload-integration.md`.

## Goal

Preserve the already structured geometry invocation—macro, family, target, and declared parameters—inside the native S3V action rather than relying on `verb.other` or opaque `notes`. The output must remain a general typed data contract; it must not introduce profiles, defaults, templates, opaque-note parsing, a scene mapping, a renderer execution path, robot control, or candidate/promotion activity.

## Files Read

- `AGENTS.md` and `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `README.md`, `STATUS.md`, `CCF_Sovereign\README.md`, `CCF_Sovereign\MVP_STATUS.md`, and `CCF_Sovereign\requirements.txt`
- `CCF_Sovereign\src\world_schema\model.py`
- `CCF_Sovereign\src\world_schema\s3v_bridge.py`
- Existing focused world-schema/S3V bridge tests
- Paired Chronos2 typed-operation integration plan and handoff

## Files to Edit

- `CCF_Sovereign\src\world_schema\s3v_bridge.py`
- Focused S3V bridge test file(s), adding a geometry-operation contract fixture and refusal coverage as needed
- `README.md`, `STATUS.md`, this plan, and a dated handoff only after measured source gates pass

## Contract

For each action generated from an operation with `operation.geometry`, emit a JSON object in `action.operation` with exactly:

| Field | Source | Rule |
|---|---|---|
| `schema_version` | Bridge constant | Exact current typed-operation version |
| `kind` | `operation.kind` | Must be `geometry_macro` for geometry invocation payloads |
| `macro` | `operation.geometry.macro` | Exact declared macro; no aliases or templates |
| `family` | `operation.geometry.family` | Exact declared family |
| `subject_id` | `operation.subject_id` | Must equal `action.subject` |
| `target_id` | `operation.geometry.target_id` | Exact declared target |
| `parameters` | `operation.geometry.parameters` | Canonical primitive values only; never invented defaults |

Actions with no geometry invocation must emit `operation: null`. The current action `notes` remain non-authoritative compatibility metadata; no consumer may derive geometry meaning from them.

## Ordered Steps

1. [x] Captured the Primus clean/dirty baseline. The only new item at start was this plan; no inherited source or evidence was staged.
2. [x] Located `test_world_schema.py` and added a focused `EXTRUDE_FACE` fixture with explicitly declared `selector`, `axis`, and `distance_mm` values. The production trajectory generator currently declares only `distance_mm`; no selector or axis default was introduced.
3. [x] Implemented direct typed `action.operation` serialization from `WorldOperation.geometry` in `s3v_bridge.py`.
4. [x] Added tests proving exact emission, `operation: null` for non-geometry actions, deterministic output, absence of parameter recovery from `notes`, and failure when geometry is attached to a non-geometry operation kind.
5. [x] Ran `python -m compileall -q src\\world_schema\\s3v_bridge.py test_world_schema.py`, `python -m unittest test_world_schema.py` (10 passed), and `python -m unittest test_world_trajectory_generator.py` (7 passed).
6. [ ] Update plan, handoff, and Primus truth surfaces with the narrow source-contract result only after the factual source commit exists.
7. [ ] Explicitly stage the owned Primus paths, commit on `main`, and push `origin main`.
8. [ ] Hand the pinned source contract to Chronos2 for guarded parsing/validation. Do not run BlenderMCP or rendering in this plan.

## Acceptance and Failure Criteria

**Pass:** The generated S3V action contains direct typed geometry meaning that round-trips inside the pre-existing lossless envelope, is deterministic, and supports Chronos2 validation without opaque-note parsing.

**Fail:** Any attempt requiring macro-specific default values, action templates, inferred selectors/axes/distances, `notes` parsing, loss of parameter values, or mutation of a frozen renderer/candidate path stops the plan and records the failure.

## Rollback

No deletion or history rewrite. If focused gates fail, retain the narrow dirty diff and test record; do not stage or push it. If the contract later proves wrong, supersede it through a new forward commit.

## Next-Agent Pickup

After a passing pushed Primus source gate, Chronos2 may consume only the typed geometry payload. A native execution witness remains a separate authorized gate and must remain blocked until Chronos2 validates all accepted and rejected payloads without recipe logic.
