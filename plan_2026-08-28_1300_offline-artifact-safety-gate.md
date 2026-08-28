# Plan — Offline Artifact Safety and Control Gate

**Status:** COMPLETE — one immutable offline-only safety receipt verified; no execution authorization

**Date:** 2026-08-28 13:00 CDT

## Goal

Create a fail-closed mechanical gate for the frozen Primus transition contract witness and offline diagnostic receipt. It must prove those artifacts retain offline-only metadata and reject unsafe reinterpretation as executable program, renderer, policy, control, actuation, manufacturing, or promotion inputs.

## Scope and Fixed Inputs

- Witness: `bridge-real-20260827-002-h5-witness.json`, hash `1a431b8b957ea9082795b4a202d781afa528144c76232997e9a7ac00c55043aa`.
- Accepted diagnostic: `diagnostic-20260828-002-complete`, PNG hash `7f1eaac33b74d6b463921159981dab81017d2b1cdd582101072047a06f2a4af8`; diagnostic receipt hash `685616efdc605d65b9bab322e6f4cde282253faa32f2c40a5f378cc890bf542f`.
- Candidate `002`, parent, intake, source evidence, and both candidate lifecycles remain frozen; candidate status stays rejected and promotion false.
- This adds verification only. No policy/action/model/renderer/Chronos implementation or invocation is allowed.

## Required Gate

- Reverify witness canonical contract schema, unknown coordinate semantics, controls false, promotion false, and no program/scene/render/control payload.
- Reverify diagnostic receipt source witness hash/payload, required visible disclaimer, flags all false, opaque-state scope, and nonempty PNG hash.
- Reject unknown safety-sensitive keys, altered artifact digest, label removal, nonfalse flags, and unsafe consumer-intent strings.
- Emit one fresh ignored local safety receipt with `execution_authorized: false`; it must never emit an action or execution target.

## Files To Read

- Primus AGENTS/Charter; contract and diagnostic modules/tests; accepted witness/receipt; candidate lifecycle manifests.

## Files To Edit

- A separate offline-artifact safety validator, focused tests, a local receipt CLI, `.gitignore` only if required, this plan, then handoff/README/STATUS after results.

## Ordered Steps

- [x] Freeze scope to the existing contract witness and accepted diagnostic only.
- [x] Implement fail-closed cross-artifact validation and focused unsafe-payload/flag/label/hash tests. The validator accepts only the canonical contract plus exact diagnostic-receipt schema and refuses unsafe intent, nonfalse flags, unknown fields, digest drift, binding drift, label drift, and unsafe output paths.
- [x] Compile/run focused existing and new tests, audit, explicit-path commit, and push before invoking the safety receipt. The full focused BridgeData suite passed 73 tests.
- [x] Run exactly one local safety verification; confirm no process, candidate, input, checkpoint, renderer, or Chronos mutation. Receipt SHA-256 `be26dd831518a070d0c939f62b0dab513a2d411ac63bd88f08b4a6934d8c5511`, payload SHA-256 `056b14ef1d400362a273f9e4f676e094f486815c842e4e85e7c22af5afb719ab`; execution/control/renderer/Chronos execution/promotion are all false.
- [x] Record exact safety receipt and limits in handoff/README/STATUS; audit, explicit-path commit, and push.

## Safety and Rollback

No external command dispatch, policy inference, robot action, manufacturing, renderer, Chronos2 edit/build/run, training/tuning, candidate creation, candidate/checkpoint/parent/input mutation, promotion, deletion, reset, amend, or bulk staging. Safety outputs remain below 1 MiB in an ignored local evidence root. Preserve failures as receipts; never relax a false control/promotion check.

## Next-Agent Pickup Notes

A passing gate only proves the current artifact schema refuses unsafe interpretation. It cannot prove runtime safety, physical safety, authorization, policy correctness, or downstream consumer compliance. A buyer-facing demo must use this gate and display the offline-only limitation.


