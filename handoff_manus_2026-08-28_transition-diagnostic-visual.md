# Handoff — Offline Opaque State-Transition Diagnostic

**Status:** Completed. One accepted deterministic visual diagnostic was generated from a frozen, schema-valid Primus transition witness and visually inspected. It is an **offline numeric chart**, not a direct-Blender render, native Chronos render, scene reconstruction, video, policy, or control artifact.

## Purpose and Route

The chart makes one bounded local prediction trace visible without pretending that the BridgeData 7D state vector describes a Chronos scene. It uses observed and recursively predicted values across the same five recorded actions in candidate `bridge-real-20260827-002`'s strict task-disjoint witness. Each component is labelled only `State coordinate 1` through `State coordinate 7` because the contract deliberately retains unknown coordinate semantics.

The plotter verifies the witness's canonical schema and hash first, re-extracts only the source episode from the frozen manifest-bound intake, and matches a **unique raw observed transition lineage** by episode/task IDs, initial state, recorded action sequence, consecutive frame position, and transition IDs. It never uses predicted values to choose an observed continuation. It rejects duplicate source transition identifiers, absent/ambiguous continuation, wrong dimensions, nonfinite values, invalid witness coordinate semantics, non-fresh output locations, or missing local evidence root.

## Accepted Visual Evidence

![Offline opaque 7D transition diagnostic](CCF_Sovereign/evidence/transition_diagnostics/diagnostic-20260828-002-complete/opaque_state_trajectory_diagnostic.png)

| Binding | Value |
|---|---|
| Accepted diagnostic path | `C:\Primus\CCF_Sovereign\evidence\transition_diagnostics\diagnostic-20260828-002-complete\opaque_state_trajectory_diagnostic.png` |
| PNG dimensions | 1600 × 1050 |
| PNG SHA-256 | `7f1eaac33b74d6b463921159981dab81017d2b1cdd582101072047a06f2a4af8` |
| Receipt SHA-256 | `685616efdc605d65b9bab322e6f4cde282253faa32f2c40a5f378cc890bf542f` |
| Receipt payload SHA-256 | `dd2d7d42a47750eb19c75d4d3b959570dcd9c1419f5423fd9612768d9c95794b` |
| Witness SHA-256 | `1a431b8b957ea9082795b4a202d781afa528144c76232997e9a7ac00c55043aa` |
| Witness payload SHA-256 | `e2195592ed0912cf76e21be011279b30df91a90857725c57b50d70b2a10b65e2` |
| Candidate / lifecycle | `bridge-real-20260827-002`; terminal `rejected`, promotion false |
| Observed witness episode / task / horizon | `10519` / `134` / `5` |
| Observed raw lineage | `bridgedata-e10519-f4-i287110` through `bridgedata-e10519-f8-i287114` |
| Overall component/step MAE | `0.0175019109528541` |
| Required visible disclaimer | `Opaque 7D BridgeData state coordinates — not a Chronos scene, render, policy, or control signal.` |
| Runtime invocation flags | Chronos false; renderer false; control false; promotion false |

The chart shows all seven labelled coordinate panels above a separate absolute-error strip. Blue circle traces are observed data; orange square traces are the frozen predictor. It does not assign physical meaning to any coordinate and does not depict objects, geometry, space, materials, robots, or actions beyond the source action-step index.

## Preserved Failures and Corrections

Three issues arose during visual delivery and were preserved rather than hidden:

| Event | Effect | Correction / status |
|---|---|---|
| Initial post-commit export imported unavailable Matplotlib. | `ModuleNotFoundError`; no PNG and no receipt were created. | Exporter was corrected to use already installed Pillow and committed before retry. |
| First Pillow diagnostic layout placed the error strip over part of State coordinate 7. | A local image existed but did not meet the complete-panel visual contract. It remains preserved at `diagnostic-20260828-001`. | The committed three-column layout keeps all seven panels above the error strip. |
| A focused duplicate-lineage fixture expected a generic error after the implementation added a stronger explicit guard. | Test expectation mismatch; no data/evidence impact. | The test now asserts duplicate transition identifier refusal. |

The accepted `diagnostic-20260828-002-complete` visual was checked visually. All seven coordinate labels/traces are visible, the error strip is visible, and the red non-render/non-control disclaimer is legible.

## What the Visual Does and Does Not Establish

> The visual is a faithful chart of one frozen model's five-step numeric transition prediction versus the corresponding observed state trace, with raw lineage and provenance verified.

It makes existing local predictive evidence legible. It does **not** demonstrate a world model with semantic objects, physical coordinate interpretation, vision, scene reconstruction, native Chronos integration, renderer output, robot behavior, policy/control, safety, reliable long-horizon prediction, manufacturing capability, product readiness, or promotion. It is not a renderer PNG. The earlier direct-Blender witness remains a separate historical artifact and should never be conflated with this chart or native Chronos output.

## Code, Tests, and Repository State

The raw-lineage diagnostic module and initial plotter were committed at `ca7dae0454fc33db55a91a75aa1a06cd4d5d624a`. The local-library correction was committed at `4f4498c6078921b667df6e3f79358ee411af30cd`; the complete-panel correction was committed at `3376fb3e93c02052136185c8db7f4b8cfa2d8e11`. The focused BridgeData gate passed 70 tests before visual execution; the post-correction focused lineage/contract gate passed 8 tests.

The protected parent SHA-256 remains `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`. The intake manifest SHA-256 remains `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a`. The accepted PNG, receipts, witness, logs, and visual-check note are all local and Git-ignored. No relevant Primus process remains active.

## Next Boundary

The next phase is not a renderer or visual-world bridge. First harden the **safety/control boundary** mechanically: require all local prediction artifacts—including contract witnesses and visible diagnostics—to carry explicit offline-only metadata and provide an executable-path refusal test for prohibited control, render, and program payloads. Only after that can a buyer-facing demo gate package the existing evidence in a route that cannot be misread as autonomous robot control or native Chronos integration.
