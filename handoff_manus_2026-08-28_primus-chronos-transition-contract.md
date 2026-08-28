# Handoff — Primus-to-Chronos Transition Evidence Contract

**Status:** Completed as a **schema-only consumer boundary**. A single local witness was exported and validated from frozen candidate `bridge-real-20260827-002` and strict task-disjoint h5 evidence. No Chronos2 code, build, runtime, renderer, scene, or product integration was invoked or changed.

## What Changed

Primus now contains a versioned fail-closed contract at `CCF_Sovereign/src/real_data/chronos_transition_contract.py`. The contract is designed to give a future Chronos2 consumer a checkable, local, provenance-bound numeric evidence object without pretending that a BridgeData 7D robot-state vector is a Chronos world/scene coordinate system.

The contract carries only the observed initial 7D state, observed 7D action sequence, recursively predicted 7D state sequence, horizon, case ID, episode/task IDs, and immutable bindings to the candidate, checkpoint, parent, frozen intake, and source evidence. It rejects unknown fields, including program, render, scene, geometry, primitive, control, actuation, and command payloads. It requires `control_permitted: false`, `promotion_performed: false`, scope `offline_observational_prediction_evidence`, and exact limitation text.

| Consumer condition | Required contract behavior |
|---|---|
| Numeric state/action shape | Exact finite 7D vectors; action and predicted sequence count must equal horizon. |
| Coordinate semantics | `unknown_not_a_chronos_scene_transform`; no mapping to entity, transform, geometry, material, camera, or renderer primitive. |
| Control and promotion | Permanently false in every valid artifact. |
| Provenance | Candidate/checkpoint/manifest, protected parent, intake, source evidence file, and source evidence payload each hash-bound. |
| Serialization | Canonical JSON SHA-256; unknown, missing, altered, nonfinite, or wrong-dimensional fields are refused. |
| Persistent write | Fresh destination only, beneath an explicit local evidence root, then immediately revalidated. |

## Witness Verified

The one witness is local and Git-ignored:

`C:\Primus\CCF_Sovereign\evidence\chronos_transition_contracts\bridge-real-20260827-002-h5-witness.json`

| Binding | Value |
|---|---|
| Witness file SHA-256 | `1a431b8b957ea9082795b4a202d781afa528144c76232997e9a7ac00c55043aa` |
| Witness payload SHA-256 | `e2195592ed0912cf76e21be011279b30df91a90857725c57b50d70b2a10b65e2` |
| Source candidate | `bridge-real-20260827-002`, terminal `rejected`, promotion false |
| Source strict evidence SHA-256 | `218748de489ebc0b921566c21fd8a712898ba77efd1e2251e764c86f90d2ba1f` |
| Source strict evidence payload SHA-256 | `445caddf9fb884dae35499a59a856a175d90ff6fee2b03862da7f303c30d172c` |
| Witness rollout case | `bridgedata-rollout-held_out_task-e10519-f4-i287110-h5` |
| Episode / task / horizon | `10519` / `134` / `5` |
| Observed action count | 5 finite 7D vectors |
| Predicted state count | 5 finite 7D vectors |
| Protected parent SHA-256 | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |
| Intake manifest SHA-256 | `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a` |

The post-export verifier recomputed and accepted the canonical payload digest. It observed `chronos_consumer_status: schema_only_coordinate_adapter_required`, the exact unknown coordinate-semantics sentinel, control false, promotion false, and five actions/five predicted states. The candidate manifest remained rejected and promotion false. Parent and intake hashes remained unchanged. No relevant process was active.

## Tests and Preserved Failure

The full focused BridgeData test suite passed with **67 tests** before export. Contract tests cover canonical round-trip, digest drift, unknown renderer/control fields, attempted coordinate semantics, control/promotion changes, invalid vector dimension, root-bound fresh writes, and reload verification.

An inline validation command was attempted after export but supplied a Windows backslash path through a Python string and therefore failed only with an invalid local path escape. It did not alter the witness, inputs, candidates, or repositories. A saved verifier script replaced it and passed. This is preserved as a scripting/path-validation failure, not a contract/evidence failure.

## Consumer Acceptance Gate for Chronos2

A future Chronos2 adapter may **read but not execute** a contract witness only if all of the following hold:

1. It verifies the canonical contract digest, all provenance hashes, `control_permitted: false`, and `promotion_performed: false` before parsing numeric vectors.
2. It rejects every artifact whose coordinate semantics are not exactly unknown/adapter-required. It must not invent or default a 7D-to-scene mapping.
3. It treats the vectors as offline diagnostic data only. It must not create or execute S3V programs, primitives, geometry, camera transforms, render requests, manufacturing instructions, or robot commands from the artifact.
4. It records a separate immutable receipt showing schema validation and no execution.
5. Any later coordinate adapter requires independently captured calibration/semantic evidence and its own held-out validation gate. The current BridgeData 7D representation does not supply it.

## Correct Claim and Non-Claims

> Primus can now emit a hash-bound, schema-valid, non-executable local handoff containing a frozen predictor's bounded 7D state-transition evidence, while explicitly preserving that its state coordinates have no verified Chronos scene meaning.

This is not native Chronos integration, renderer evidence, visible world evidence, scene generation, a world model with object semantics, policy/control/safety evidence, actuation, manufacturing, product readiness, or promotion. It does not free the product from large models in broad domains; it establishes an auditable local contract for one narrow learned-transition module.

## Repository State and Next Boundary

The contract implementation was pushed before witness export at `5e1c9bd65596e08bbdf6b938db026f791147fd0c`. The contract witness remains local and ignored. The existing `C:\chronos2` working tree remains untouched: its inherited untracked primitive-bootstrap, audit, and renderer-plan files were neither staged nor modified.

The next permitted phase is a **visible diagnostic bridge**, not a renderer. It can chart observed and predicted 7D state components and per-step error for the same frozen witness, labelled as an offline state-trajectory diagnostic with unknown physical/scene coordinate semantics. It must not look like a native Chronos render or claim object/world reconstruction. A separate safety/control boundary must then make the non-executable nature mechanically obvious before any buyer-facing demonstration gate.
