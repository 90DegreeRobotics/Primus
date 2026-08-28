# Plan — Buyer-Facing Evidence Demonstration Gate

**Status:** COMPLETE — one local evidence packet verified; no external publication or execution

**Date:** 2026-08-28 14:00 CDT

## Goal

Build one deterministic, local, inspectable buyer-evidence packet from existing frozen strict-task metrics, accepted opaque-state diagnostic, and offline-only safety receipt. It must fail closed on provenance/safety drift and state its limits prominently. It is not an autonomous product demo, native Chronos demo, robot demonstration, or renderer showcase.

## Fixed Demonstration Contract

- Inputs: accepted local diagnostic/receipt, offline safety receipt, frozen candidate `002` lifecycle, and strict task-disjoint cross-rollout evidence only.
- Output: fresh local ignored directory with one `index.html`, a copy of the already accepted deterministic chart, and a hash-bound `demo_receipt.json`.
- Demo page: exact h1/h2/h5 strict source-train-task-disjoint summary for both frozen candidates; source-train-only strongest linear baseline at h5; explicit offline-only, unknown-coordinate, no-control/no-Chronos/no-renderer/no-promotion statement.
- Gate: validate the safety receipt mechanically before writing any output; verify copied PNG digest; never make an external request, run a model, create a candidate, or execute downstream code.

## Files To Read

- Primus AGENTS/Charter; offline safety validator/receipt; strict task evidence; candidate lifecycle; accepted diagnostic receipt/PNG; local evidence ignore policy.

## Files To Edit

- Standalone demo-packet generator and focused test; `.gitignore` for the local demo root; this plan; later handoff/README/STATUS after verified output.

## Ordered Steps

- [x] Limit the demo to frozen evidence presentation and require the offline safety gate as a prerequisite.
- [x] Inspect strict-evidence schema and implement a deterministic evidence-card generator with fail-closed bindings. The generator accepts only two complete passing strict source reports at h1/h2/h5, source-train task/episode overlap zero, exact coverage, canonical source digests, and an independently valid offline safety prerequisite.
- [x] Test metric parsing, safety gating, fresh output, disclaimer/claim restrictions, and copied-chart digest; audit, explicit-path commit, and push before the one demo-packet invocation. A static HTML formatting defect caused by CSS braces was corrected before integration; the full focused BridgeData suite passed 76 tests. The first post-commit packet invocation correctly refused an assumed nested coverage schema before any packet directory was created. Actual strict evidence stores `cases`, `predictions`, scalar `coverage`, `unknown_prediction_count`, `excluded_case_count`, and `finite_prediction_rate`; the parser and fixture were corrected to require that exact complete-coverage contract, and the full focused suite again passed 76 tests.
- [x] Create exactly one fresh local packet; inspect the HTML source, receipt, and copied chart; attach the chart only with the offline-diagnostic label. Accepted packet `buyer-evidence-20260828-002-complete` is 65,657 bytes; copied-chart hash matches its source, strict evidence/safety receipt bindings match, and execution/control/renderer/Chronos-execution/promotion are all false.
- [x] Record the accepted evidence packet and all limits in handoff/README/STATUS; audit, explicit-path commit, and push.

## Safety and Rollback

No web publication, external browser post, action/policy/control/robot command, manufacturing, Chronos2 modification/build/run, renderer, image generation, training/tuning, candidate/checkpoint/parent/input mutation, promotion, deletion, reset, amend, or bulk staging. The packet must be local, under 2 MiB, and Git-ignored. Preserve failed packets/receipts. A passing packet only shows that existing narrow evidence is presented without losing its limits.

## Next-Agent Pickup Notes

A buyer-facing packet does not increase model evidence. It must never be presented as a world-model product, robot demo, or native Chronos proof. Any future product demonstration needs independently verified scene semantics and integration.



