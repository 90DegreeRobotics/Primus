# Handoff — Local Buyer Evidence Demonstration Gate

**Status:** Completed. One local, deterministic, limitation-forward evidence packet was created from existing frozen strict task-disjoint evaluation evidence, accepted opaque-state diagnostic, and offline-only safety receipt. It was not published, served, posted, or presented as a product demonstration.

## What Changed

Primus now has a local static buyer-evidence packet generator. It cannot run unless it first validates the frozen contract witness plus accepted diagnostic through the offline safety gate, validates the stored safety receipt's canonical digest/false flags, and validates the strict cross-rollout payload digest.

The generator then accepts exactly two frozen source reports, each with h1/h2/h5 rows, exact finite coverage, source-train task overlap zero, selected-episode overlap zero, point-estimate and episode-clustered bootstrap all-horizon passes, and a candidate RMSE strictly below its declared strongest source-train-only baseline. It copies the already accepted data chart, verifies that copied hash, and writes a static HTML page plus a local canonical receipt. It has no web publication, network, model, renderer, Chronos2, robot, policy, command, or control interface.

## Accepted Packet

| Binding | Value |
|---|---|
| Packet directory | `C:\Primus\CCF_Sovereign\evidence\buyer_demo_packets\buyer-evidence-20260828-002-complete` |
| Packet size | 65,657 bytes, below the declared 2 MiB limit |
| HTML SHA-256 | `3533118023d7046cd1b7ff06eca27463d58bcdfc5ee52587788e349acb49127b` |
| Copied chart SHA-256 | `7f1eaac33b74d6b463921159981dab81017d2b1cdd582101072047a06f2a4af8` |
| Strict evidence SHA-256 | `218748de489ebc0b921566c21fd8a712898ba77efd1e2251e764c86f90d2ba1f` |
| Strict evidence payload SHA-256 | `445caddf9fb884dae35499a59a856a175d90ff6fee2b03862da7f303c30d172c` |
| Safety receipt SHA-256 | `be26dd831518a070d0c939f62b0dab513a2d411ac63bd88f08b4a6934d8c5511` |
| Safety receipt payload SHA-256 | `056b14ef1d400362a273f9e4f676e094f486815c842e4e85e7c22af5afb719ab` |
| Packet receipt status | Execution false; control false; renderer false; Chronos execution false; promotion false |

The page has a prominent `OFFLINE EVIDENCE REVIEW ONLY` label; the required opaque-coordinate disclaimer; six exact h1/h2/h5 rows from the strict task-disjoint evaluation; one raw-lineage-verified data chart; a limitation panel; and strict/safety evidence hashes. It makes no claim beyond the frozen evidence.

## Exact Measured Table Presented

| Frozen source | Horizon | Candidate RMSE | Strongest source-train baseline | Baseline RMSE | Candidate margin | Exact cases |
|---|---:|---:|---|---:|---:|---:|
| `bridge-real-20260827-001` | h1 | 0.0262880795 | `linear_state_action_delta` | 0.0321352989 | 0.0058472195 | 256 |
| `bridge-real-20260827-001` | h2 | 0.0442830141 | `linear_state_action_delta` | 0.0497162224 | 0.0054332084 | 256 |
| `bridge-real-20260827-001` | h5 | 0.0681601396 | `linear_state_action_delta` | 0.0853185955 | 0.0171584559 | 256 |
| `bridge-real-20260827-002` | h1 | 0.0282176356 | `linear_state_action_delta` | 0.0326730810 | 0.0044554454 | 256 |
| `bridge-real-20260827-002` | h2 | 0.0396570520 | `linear_state_action_delta` | 0.0504707503 | 0.0108136983 | 256 |
| `bridge-real-20260827-002` | h5 | 0.0679752241 | `linear_state_action_delta` | 0.0802132039 | 0.0122379798 | 256 |

## Verification and Preserved Failure

The full focused BridgeData suite passed **76 tests** before the final packet run. It included the real-data parser/splits/baselines/candidate lifecycle, one-step/rollout/cross/uncertainty/strict/context gates, schema contract, raw-lineage chart, offline safety gate, and buyer-packet tests.

The initial post-commit buyer invocation refused before output creation because the packet parser assumed a nested coverage shape. Inspection found the signed strict rollout uses scalar `coverage` alongside `cases`, `predictions`, `unknown_prediction_count`, `excluded_case_count`, and `finite_prediction_rate`. The parser and fixture were corrected to require that exact real contract; the full suite passed again; only then was the accepted packet created. The failed log remains local and ignored. A sandbox-browser request could not access the connected workstation's local `file:` path; the HTML source, receipt, copied-chart digest, and previously visually checked chart were inspected directly instead. No output was altered by this failed browser access.

## Claim Boundary

> This is a deterministic, local evidence packet for two frozen compact predictors that beat the stated strongest local baseline at three short rollout horizons under source-train task-ID and selected-episode separation. The page preserves the evidence's offline-only and non-executable boundaries.

It is not a product demo, robot demo, autonomous system, control/policy/actuation signal, safety certification, renderer/native Chronos evidence, scene reconstruction, visual world model, long-horizon reliability proof, general intelligence claim, or promotion decision. It does not increase the underlying measured model capability.

## Repository State and Next Boundary

The generator was committed in `de9bcf536b391dc986e3d121a56528ca57634f2d`; its strict-coverage correction was committed in `2fd595282b521c32b7bbe977cdc8f9bab5cddef5` before accepted output. The packet, copied chart, and all receipts remain local and Git-ignored.

The next step is a final integrated handoff, not another model run. It should summarize the complete evidence ladder, identify broader-context failures/indeterminacy, keep the frozen candidates rejected, and state that native Chronos work remains limited to a schema-only consumer contract. No renderer or policy activity is justified by the buyer packet.
