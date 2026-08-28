# Plan — Offline Transition Diagnostic Visual

**Status:** ACTIVE

**Date:** 2026-08-28 12:00 CDT

## Goal

Generate one deterministic, data-faithful visual diagnostic from the frozen schema-only Primus transition witness. The visual will compare observed and recursively predicted values for the seven opaque BridgeData state coordinates across a five-step observed-action sequence. It is not a render, scene reconstruction, video, or native Chronos output.

## Fixed Visual Contract

- Input: only the validated `bridge-real-20260827-002-h5-witness.json` contract witness and its hash-bound provenance.
- Output: one 1600x1050 PNG plus a local JSON receipt under an explicit ignored diagnostic root.
- Layout: seven small multiples, one per unlabeled state coordinate; observed versus predicted state traces; a clearly labelled absolute-error strip; a title that calls it an offline diagnostic.
- Labels: `State coordinate 1` through `State coordinate 7`, not physical pose, position, orientation, object, world, or scene labels.
- Required visible disclaimer: `Opaque 7D BridgeData state coordinates — not a Chronos scene, render, policy, or control signal.`
- No interpolation, denoising, synthesis, transform mapping, renderer, AI image generation, or decorative interpretation.

## Files To Read

- Primus AGENTS/Charter, transition contract module/test, validated local witness, and relevant local evidence policy.

## Files To Edit

- A standalone deterministic diagnostic plotter and focused test; `.gitignore` for the local diagnostic root; this plan; later handoff/README/STATUS only after visual verification.

## Ordered Steps

- [x] Select deterministic precise-chart route and preserve the unknown-coordinate/non-renderer boundary.
- [x] Implement and test input hash/schema verification, numeric trace/error computation, fixed layout, and fresh local output restrictions. Raw observed lineage now rejects duplicate transition identifiers explicitly; the focused duplicate fixture initially expected a generic error and was corrected to assert the stronger dedicated guard.
- [x] Compile/run focused chart and contract tests; audit and explicitly commit/push only owned source/test/ignore/plan paths before generating the diagnostic. The focused BridgeData suite passed 70 tests. A first post-commit export attempt preserved a `ModuleNotFoundError` because the workstation Python lacks Matplotlib; it generated no PNG or receipt and altered no evidence. The exporter is corrected to use already installed Pillow with the same deterministic layout and all chart/contract tests pass.
- [ ] Generate exactly one visual from the frozen witness, verify its receipt/hash/dimensions and visible disclaimer, and attach it to the final report labelled offline diagnostic — not a renderer PNG.
- [ ] Record the visual evidence and limitations in handoff/README/STATUS; audit, explicit-path commit, and push.

## Safety and Rollback

No Chronos2 modification or invocation, renderer, video, image-generation model, robot action, manufacturing, download, training, candidate/checkpoint/parent/intake mutation, promotion, deletion, reset, amend, or bulk staging. The PNG is a deterministic numeric plot and must never be called native Chronos or direct-Blender output. If schema/hash/coordinate semantics fail, preserve a local failure receipt and stop rather than inferring a world mapping.

## Next-Agent Pickup Notes

This only creates visible state-trajectory evidence, not visible world evidence. Any future object/world visualization needs independently verified coordinate semantics and may not derive geometry or primitives from this witness.


