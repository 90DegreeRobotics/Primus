# Plan — Wine-Glass Create Recovery

**Date:** 2026-09-05 1143 CDT
**Status:** COMPLETE — source repair and Git finalization landed on `origin/main`; live Foundry click-through remains UI-pending
**Scope:** Correct the Create/Object path that declined `a wine glass` before producing a rateable draft. This is a focused product defect repair, not a geometry-capability expansion.

## Governing constraints

- Work only on `main`; do not create a branch, worktree, or clone.
- Do not delete, install, uninstall, or launch an installer.
- The active Create path must preserve a rateable, rerunnable draft attempt whenever readable segmented input exists. A quality or material limitation may be recorded as evidence but may not erase the attempt.
- Do not add a noun recipe, named-object generator, hardcoded parameter profile, or a new shape-thinking dictionary branch. The solution must route according to already-general capabilities: vessel/measured geometry, material intent, and generic fallback behavior.
- A render-facing source change requires focused tests, inspected generated artifacts where possible, and an explicit UI-witness boundary.

## Baseline evidence

| Item | Evidence | State |
|---|---|---|
| Repository | `C:\chronos2` is the product checkout governed by `AGENTS.md`. | Read from disk |
| Branch/status/upstream | Desktop Git restored 2026-09-05 1303 CDT: `main`, dirty tree held this repair plus an unrelated Cradle IP note. | Measured |
| User-visible failure | Create selected **Object** for `a wine glass`; UI records **CARVED GEOMETRY — DECLINED**, produces no buyer-ready image, and says the carve cannot make glass/glow. | Screenshot, 2026-09-05 11:41 CDT |
| Existing correct capability | `desktop/precision_build.py` supplies generic, measured vessel geometry and verified glass material profiles. A prior Create witness shows a glass finish applied after geometry validation. | Source + witness log |
| Requirement violation | A material limit in the carve route suppresses the required draft instead of routing or preserving a material-capable attempt. | Screenshot + `AGENTS.md` rule 6 |
| Scope boundary | The no-recipe geometry plan is planning-only and forbids new keyword/noun recipes. | `plan_2026-08-29_0552_no-recipe-geometry-understanding.md` |

## Diagnosis hypothesis and falsification

**Hypothesis:** Object mode applies a `carved geometry` material refusal before a generic vessel/material-capable route is selected for a glass vessel. The failure is routing/control flow, not a Blender rendering crash.

**Falsification:** Trace the Create argument builder, the Object-mode material gate, and `names_a_vessel` / material classification. If `a wine glass` already reaches `desktop.precision_build`, diagnose the precision worker/logging path instead; do not change routing based only on the screenshot.

## Work items

- [x] Read repo law, product truth, the no-recipe plan, and available Create evidence.
- [x] Locate the exact Object-mode decline guard and saved recovery evidence for the wine-glass run.
- [x] Confirm whether generic vessel/material detection routes `a wine glass` to the precision worker.
- [x] Implement the narrowest routing/fallback correction that guarantees a preserved draft attempt without adding recipes.
- [x] Add regression tests covering glass-vessel Object-mode routing and corrected carve recovery semantics.
- [x] Run the focused Python test gate and syntax/static validation available in this environment.
- [x] Inspect the fixture-backed glass artifact evidence; label live Blender/UI witness status accurately.
- [x] Update present-tense truth surfaces only if the code changes a documented product claim.
- [x] Stage, commit, push, and verify `HEAD == origin/main` after desktop Git access is restored.

## Verification standard

The focused regression must demonstrate that `a wine glass` in Object mode takes a generic material-capable route (or otherwise emits a persistent, rateable draft) rather than returning the `CARVED GEOMETRY — DECLINED` no-image state. The result must preserve the buyer's material intent or state any material limitation alongside an actual draft; it may not substitute an unlabelled solid stand-in.

## Implemented repair and evidence

The original failure has two contributing control-flow defects. First, `names_a_vessel()` only recognised a fixed list of container terms. `a wine glass` therefore did not reach `desktop.precision_build`, even though that generic route already creates a hollow mesh and applies a verified glass shader. It instead entered `first-light --geometry-forge`. Second, `resolve_carved_body()` treated every transmission/emission word as a pre-dispatch decline, so it emitted **CARVED GEOMETRY — DECLINED** and deliberately produced no draft.

The repair makes a terminal `glass` a generic hollow-vessel head noun while leaving material modifiers such as `a red glass dragon` and `a stained glass window` on the creative route. This is a grammatical route choice; it adds neither a named-object generator nor a geometry profile. Consequently, `a wine glass` in Object mode launches `desktop.precision_build`, which shells and measures the generic outer form, applies the existing glass profile (transmission 0.86, IOR 1.45), writes an STL, `.blend`, hero, and rotation evidence.

The carve material gate now records transmission/emission as an advisory through `carve_cannot_hold()` instead of declining before Comfy reference capture. For a non-vessel material-bearing subject, the limitation is stated accurately—surface-colour approximation rather than a glass/refraction/emission shader—while readable reference views can still yield a rateable draft. The only remaining early carve decline is openwork with no connected solid silhouette, where the required reconstruction input genuinely does not exist.

## Truth-surface decision

No present-tense product claim changed. `docs/CAPABILITY_MAP.md` already states that Object mode uses the measuring engine for vessels and stated sizes, otherwise the visual-hull carve. The map does not enumerate vessel head nouns, and it does not claim that carve declines glass or emission. `STATUS.md` and `README.md` likewise do not assert the old no-image decline as current behaviour. The repair makes the existing vessel claim cover a grammatical class it had missed; it does not invent a new capability row. Truth surfaces were therefore left unchanged.

Unrelated dirty file left unstaged: `docs/windows/DEMO_LAPTOPS_CONNECT.md` (Cradle DHCP IP `192.168.4.34` → `192.168.4.45`). `desktop/chronos_foundry.py` showed a CRLF-only dirty bit with no content diff and was not staged.

## Verification run (2026-09-05, desktop restored)

- `python -m pytest desktop/tests/test_dimension_reading.py desktop/tests/test_create_acceptance.py desktop/tests/test_create_tab_witness.py desktop/tests/test_stage_channel.py -q` → **60 passed, 146 subtests**.
- `cargo test -p chronos_cli --bin chronos -- geometry_forge_declines_only_openwork light_transport_is_recorded` → **2 passed** (174 filtered).
- The new tests prove `a wine glass` selects the precision worker, `a red glass dragon` is not misclassified as a vessel, and light transport is advisory rather than a carve gate.
- Live Blender wine-glass render and interactive Foundry confirmation were not performed in this close-out. Blender 4.5 is present; a Create click-through remains the buyer witness. Prior precision Create logs remain supporting artifact evidence of generic hollow-vessel construction and a glass finish, not a fresh wine-glass witness.

## Known remaining boundary

Paired plan copy lands in `C:\Primus` in the same unit of work. Installed-application confirmation still requires the operator to open Foundry, choose **Create → Object**, enter `a wine glass`, and judge the hero. Until that click happens, this repair is **terminal-verified, UI-pending**.

## Paired implementation

The executable repair is in `C:\chronos2`. This Primus file is the tandem-repo plan copy required by both `AGENTS.md` contracts. No Primus trainer or corpus behavior changes in this unit of work.
