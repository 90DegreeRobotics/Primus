# Handoff — No-Recipe Geometry Understanding (planning)

**Agent:** Claude
**Date:** 2026-08-29
**Status:** Planning complete. No implementation authorized or performed.
**Repos:** tandem. Paired handoff in `C:\chronos2` at the same filename. The
recipe surfaces named below live in Chronos2; Primus records them because under
rule 10 neither repo may hold half the picture.

## Operator Directive

> No recipes. Again I state, no recipes. The system will be able to learn or not
> exist.

Now repo law: `AGENTS.md` non-negotiable 8 (chronos2), rule 9 (Primus). The
tandem obligation is non-negotiable 9 (chronos2), rule 10 (Primus).

## Why The Rule Was Needed

The constraint was already stated exactly, on 2026-08-15, in
`plan_2026-08-15_2046_shape-thinking-not-recipes.md`:

> A book of recipes (Pagoda, Ship, Eiffel, House…) is the wrong product.

It lived only in that plan. The plan was marked COMPLETE, and completed plans
stop being read. `AGENTS.md`, `CLAUDE.md`, the build doctrine, and the Charter
contained no normative mention of recipes — the doctrine's hardcoding rules are
all about deployment (engines, DPI, paths), not architecture.

So agents read the law, the law was silent, and agents wrote recipes. That is an
unencoded constraint, not a misunderstood one. It is now encoded with a test an
agent can apply: **ask what decided this value; if the answer is a literal, an
index, a variant number, or a modulo of one, it is a recipe.**

## Recipe Surface Inventory — measured, not asserted

| # | Surface | Evidence |
|---:|---|---|
| 1 | `chronos_geometry_plan::shape_thinking::think_from_brief` | 5 keyword matchers over noun lists; 3 replay a stored seed; vessel branch selects between 4 hardcoded magic-number profiles |
| 2 | `chronos_priors::classify_prompt` | noun→`ShapeFamily` table, 194 `ShapeFamily::` references, documented in `MASTER_GUIDE.md` 12.7 as the "Universal Noun Path" |
| 3 | Named `PrimitiveKind`s | compiled nouns; the 2026-08-15 plan called them "a floor, not the ceiling" — the ceiling was never built |

Measured behaviour of `think_from_brief`, by running it:

- "a gnarled tree root", "a bicycle chainring", "a differential gearbox housing"
  → **byte-identical** plans. Everything outside the dictionary gets one default:
  `CreateCube` → `PullFace +X` → `ExtrudeRegion +Z` → `BevelEdges all`.
- "a coffee mug holder for a car dashboard" → matches token `mug` → a single
  `RevolveProfile`. It builds a cup when asked for a bracket.
- `is_structure_brief` contains "pagoda" and "house" verbatim — the exact nouns
  the 2026-08-15 plan named as the wrong product.
- The module header already concedes it: *"the compiler invents the plan. The LLM
  does not yet choose which faces to extrude."*

**How this passed review.** The test is named
`sword_brief_is_cube_extrude_bevel_not_a_noun_lookup` and it passes honestly —
the *output* is face operations, not a `PrimitiveKind::Sword`. The *dispatch* is
a noun lookup. The recipe moved down one level and the test only checked the
level it moved out of.

Surface 2 is the more serious one: it is documented as a feature, and its test
`every_noun_classifies_into_a_buildable_family` asserts the dictionary is
*complete*. Under the directive, dictionary completeness is not a goal — the
dictionary is the defect.

## What Is Genuinely Built And Is Not A Recipe

| Piece | State |
|---|---|
| `MeshEditStep` vocabulary | `CreateCube`, `PullFace`, `SubdivideFace`, `ExtrudeRegion`, `BevelEdges`, `TaperRegion`, `SubtractShape`, `UnionShape`, `RevolveProfile`, `ShellSolid` — general operations, not nouns |
| `MeshEditPlan::validate` | real structural enforcement; `plan_uses_face_ops` rejects a lone cube |
| Sealed BlenderMCP executor | verified end-to-end 2026-08-28, commit `d97c7a58` |
| `chronos_vision` `silhouette_v0.1` | silhouette IoU 0.65 + bbox IoU 0.35 |
| Acceptance gate | calibrated `MIN_VIEW_SCORE` 0.15; blank renders score 0.0 |
| Codex sealing | `geometry_training_sample_accepted` |
| `curriculum.rs` | already declares itself "Primus → Sophia"; `primus_curriculum_genome_declared` exists and was never used |

Four of the five parts of a learning system exist. **Missing: a program sampler,
and a learned policy.**

## Critical Measured Constraint

`score_mesh_render(png, expected: &MeshEditExpectedMetrics)` scores a render
against metrics **derived from the plan**, not against a brief. It answers "did
the executor do what the program said." That is the right reward for learning
operation semantics and useless for supervising language. Any plan assuming the
current scorer can grade brief-to-shape correspondence is wrong.

## The Plan

`plan_2026-08-29_0552_no-recipe-geometry-understanding.md`, paired in
`C:\Primus`. Core ordering:

**Learn what operations do before learning which operations to choose.** Learning
what operations do requires no language, therefore no nouns, therefore a recipe
is not merely forbidden — it is unrepresentable, because the training data has
nowhere to put one.

- **Phase 0** — forward model: program → resulting geometry. Corpus from sampled
  programs, no class, no name, no brief. Holdouts by program structure.
- **Phase 1** — inverse model: shape → program. Evaluated by re-executing the
  prediction and scoring it.
- **Phase 2** — search using the forward model as a cheap evaluator, then
  distillation.
- **Phase 3** — language, attached last, attached to shape, never to programs. If
  it cannot be done without a dictionary, it does not ship.

**Tandem split:** Chronos2 is the world (operation space, executor, renderer,
scorer, sampler, corpus emission). Primus is the learner (frozen hash-pinned
inputs, candidate lifecycle, declared baselines, structural holdouts, promotion
governance). That split is not arbitrary — the BridgeData work is the only
genuinely non-recipe result in either repo, and its governance is the asset being
pointed at geometry.

## Primus's Obligations When Phase 0 Is Authorized

- Consume the Chronos2 corpus as a **frozen hash-pinned input**, under the same
  discipline as the BridgeData intake: SHA-256 over data, splits, and schema,
  verified before training, during training, and at evaluation.
- Hold out by **program structure** — sequence length, operation mix, nesting
  depth. Never by object class, because object classes are nouns.
- **Declare baselines before training:** training mean, operation-count-only,
  nearest-neighbour over programs.
- Report which baselines were beaten on which structural holdout, or report
  nothing. A number without its declared baseline and split is not a result.
- Reject from promotion by default. The BridgeData lane rejected two candidates
  that passed their acceptance rule; that discipline carries over unchanged.

## Primus Recipe Debt

`CCF_Sovereign/src/world_schema/trajectory_generator.py` is declared scaffolding
and is retiring — see `STATUS.md`. It is a fixed four-entity skeleton with
randomised numbers, and the transition it teaches is closed-form arithmetic a
linear model already recovered on 2026-08-27. The `extrude_face` axis committed
on 2026-08-28 also violates rule 9: `'xyz'[variant % 3]`. It retires with the
generator rather than being polished.

## Chronos2's First Step — a measurement, not a model

**Does `silhouette_v0.1` separate visibly different programs?**

Hand-build a few deliberately distinct valid plans, execute each through the
sealed path, and score every render against every other plan's expected metrics.
If the diagonal dominates, Phase 0 can proceed. If it does not, **the scorer is
the first thing to build** and no model should be trained against it.

Margin for concern: worst known-good sample scores 0.1837 against a 0.15
threshold. That is thin.

Those probe plans are permitted **only** as a scorer measurement. They are not a
seed library and must not be retained as plan sources — a kept set of named
example shapes is how a recipe book starts.

## Files Touched (Primus)

| File | Change |
|---|---|
| `AGENTS.md` | rule 9 gains learn-or-not-exist; rule 10 (tandem repos) |
| `README.md` | tandem section, two standing constraints |
| `STATUS.md` | no-recipe plan entry and Primus obligations |
| `plan_2026-08-29_0552_no-recipe-geometry-understanding.md` | new |
| this handoff | new |

Chronos2's paired handoff lists the files touched there, including the
`MASTER_GUIDE.md` 12.7 fence and the `CAPABILITY_MAP.md` `STUBBED` relabelling.

## Gates Run

- Documentation only; no Python or Rust touched in this repo, so no compile or
  test gate applies.
- The Chronos2 side ran `scripts\check_reachability.ps1` and verified against the
  committed baseline that its capability-map edit adds zero failures.

## What Was Not Done

No code changed. No corpus generated. No model trained. No recipe surface
deleted or edited — all three remain wired because the product calls them and
removal breaks it today. No installer, UI, or product-behaviour change. Nothing
here is a learned result or a capability claim.

## Standing Debt Not Addressed

The 4 pre-existing `LIVE` rows that fail the reachability gate. They predate this
work and were left alone deliberately rather than relabelled in a docs commit
that did not investigate them.

## Next Step

Run the scorer separation measurement. It is cheap, it uses machinery that
already works, and every downstream phase depends on the answer. Do not write a
model before it.
