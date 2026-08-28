# Chronos typed-operation payload integration plan

**Status:** ACTIVE
**Owner:** Manus
**Goal:** Extend the native typed S3V action contract and Dreamer action dispatcher so `extrude_face` is executed only from declared upstream payload fields.

## Prerequisites

The Primus bridge must emit `action.operation` containing declared Stage 2 operation semantics. The bootstrap/import changes remain uncommitted in `C:\chronos2`; retain them as one integration unit and do not run the native witness until the S3V payload contract is wired and tested.

## Contract

Native S3V action decoding accepts an optional typed operation payload. For `ActionVerb::Other("extrude_face")`, Dreamer requires the payload, validates its declared operation kind, subject identity, selector, finite axis, and distance, then issues one sealed Blender `execute_code` action. Missing/malformed payload produces a specific fail-closed error; no defaults and no `notes` parsing.

## Gates

- Add S3V decode/round-trip coverage in Chronos.
- Add Dreamer accepted/rejected extrusion payload tests with a sealed fake caller.
- Run focused `cargo test` for the typed S3V and Dreamer modules.
- Run `cargo check` for the CLI path.
- Apply only a fresh native witness after all source gates pass.

## Rollback

Revert only the typed payload/extrusion logical commit. Preserve compiler receipts, direct Blender PNGs, candidate checkpoints, bootstrap-failure directories, and all unrelated untracked audit files.
