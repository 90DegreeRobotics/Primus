# Plan — Primus-to-Chronos Transition Evidence Contract

**Status:** ACTIVE

**Date:** 2026-08-28 11:40 CDT

## Goal

Define, implement, and test a schema-only contract for exporting bounded Primus 7D action-conditioned state-transition evidence into a future Chronos2 consumer. The contract carries numeric prediction provenance and explicit non-control/non-renderer semantics. It does not integrate or modify Chronos2 runtime code.

## Current Constraints

- `C:\chronos2` has inherited and active untracked renderer/primitive-bootstrap work. It remains untouched.
- The user rejected recipe rendering. No primitive templates, defaults, opaque-note parsing, or automatic scene/command generation is allowed.
- Candidate `001` and `002`, parent, intake, and local evidence remain frozen and rejected from promotion.
- The BridgeData state/action coordinate semantics are insufficient to claim a direct Chronos scene transform or a robot command. The contract must preserve that semantic gap rather than invent a mapping.

## Contract Requirements

- Versioned canonical JSON with SHA-256 digest and source evidence/candidate/checkpoint/intake bindings.
- Numeric 7D observed initial state, 7D observed action sequence, 7D predicted state sequence, explicit horizon, and finite-vector validation.
- An explicitly unknown `state_coordinate_semantics` field; no transform, geometry, selector, renderer primitive, or executable action fields.
- `control_permitted: false`, `promotion_performed: false`, `artifact_scope: offline_observational_prediction_evidence`, and required limitations.
- Schema rejects unknown fields, destination reuse, hash omissions, candidate lifecycle that is not rejected/no-promotion, invalid dimensions, nonfinite values, and any control/render/program payload.
- A later Chronos2 adapter must validate this object first and remain blocked until it supplies independently verified coordinate semantics.

## Files To Read

- Primus `AGENTS.md`, Charter, README, STATUS, latest context/strict handoffs, candidate output and frozen manifests.
- Existing BridgeData transition, rollout, evidence-hash, and candidate-lifecycle modules/tests.
- Chronos2 `AGENTS.md` and read-only S3V/film/orchestrator interfaces for consumer boundary understanding only.

## Files To Edit

- A new isolated `CCF_Sovereign/src/real_data/chronos_transition_contract.py`, package export, focused test, and optional ignored contract-witness exporter.
- `.gitignore` only if a fresh local contract-witness root is required.
- This plan and, only after validation, handoff/README/STATUS.

## Ordered Steps

- [x] Read both repository laws and identify the Chronos2 dirty/in-flight boundary.
- [x] Inspect existing frozen prediction/evidence payload shapes and write a fail-closed non-recipe contract plus focused tests. The strict evidence retains paired case errors but not predicted vectors, so the exporter reconstructs one frozen verified h5 prediction read-only from its source-bound rollout case; it carries no scene or executable payload.
- [x] Compile/run focused regression tests; audit and explicitly commit/push only Primus contract code before exporting a single local witness. The focused BridgeData suite passed 67 tests.
- [ ] Export and verify one bounded ignored contract witness derived read-only from frozen local evidence; no Chronos invocation.
- [ ] Record contract limits and consumer acceptance gate in handoff/README/STATUS; audit, explicit-path commit, and push.

## Test Gate

Run compileall on touched files; focused contract tests plus existing BridgeData regression modules; verify canonical hashes and rejection behavior; run `git diff --check --cached` and Markdown hygiene checks before commits.

## Safety and Rollback

No Chronos2 edits, build, runtime invocation, renderer, scene generation, video, robot action, manufacturing, download, training, tuning, candidate creation, checkpoint/parent/intake mutation, promotion, deletion, reset, amend, or bulk staging. Contract witness output must be fresh, local, Git-ignored, and below 5 MiB. On any semantic/evidence mismatch, preserve a failure receipt and stop rather than adding mappings/defaults.

## Next-Agent Pickup Notes

A valid Primus contract witness is not a native Chronos integration or a visual world model. It creates a checkable handoff boundary only. Chronos must later demonstrate independently that it can consume a schema-valid object without inventing 7D-to-scene semantics, and any visual bridge must be labelled clearly as offline diagnostic evidence.

