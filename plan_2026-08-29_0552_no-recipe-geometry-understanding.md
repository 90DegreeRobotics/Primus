# Plan — No-Recipe Geometry Understanding (Primus side)

**Date:** 2026-08-29 0552 CDT
**Status:** PLANNING — no implementation authorized yet
**Repos:** tandem. Paired with
`C:\chronos2\plan_2026-08-29_0552_no-recipe-geometry-understanding.md`.
Both copies carry the same architecture. This copy owns the learner.

## Operator Directive

> No recipes. The system will be able to learn or not exist.

That is a build constraint, not a preference. Every phase below is designed so a
lookup table cannot be smuggled in, and each phase names the test that would
catch one.

## The Governing Insight

A system cannot choose which operations make a shape until it knows what
operations do to shapes.

That ordering is the whole plan, and it has a useful property: **learning what
operations do requires no language at all.** No language means no nouns. No nouns
means a recipe is not merely forbidden, it is unrepresentable. The training data
has no place to put one.

Every previous attempt started at the far end — brief to shape — where nouns are
the only available bridge, and a dictionary is the path of least resistance. That
is why `think_from_brief` became a noun dictionary, and why the synthetic
trajectory generator became a template. Neither failed from carelessness. They
failed because they were asked to cross the hardest gap first.

## What Already Exists (measured 2026-08-28/29, not assumed)

| Piece | Where | State |
|---|---|---|
| Operation vocabulary | `chronos_geometry_plan::MeshEditStep` | Real and general: `CreateCube`, `PullFace`, `SubdivideFace`, `ExtrudeRegion`, `BevelEdges`, `TaperRegion`, `SubtractShape`, `UnionShape`, `RevolveProfile`, `ShellSolid` |
| Plan validator | `MeshEditPlan::validate` | Enforces structure; `plan_uses_face_ops` rejects a lone cube |
| Executor | Dreamer → sealed BlenderMCP | Works as of 2026-08-28. Four defects fixed to get it there. |
| Consistency scorer | `chronos_vision::score_mesh_render` | Silhouette IoU 0.65 + bbox IoU 0.35, versioned `silhouette_v0.1` |
| Acceptance gate | `chronos_geometry_plan::acceptance_gate` | Calibrated `MIN_VIEW_SCORE` 0.15; blank renders score 0.0 |
| Sealed evidence | Codex `geometry_training_sample_accepted` | Exists |
| Tandem handshake | `curriculum.rs` | Declares itself "Primus → Sophia"; `primus_curriculum_genome_declared` event exists and was never used |
| **Program sampler** | — | **Missing. This is the organ that does not exist.** |
| **Policy** | `think_from_brief` | **Occupied by a noun dictionary. Fenced, see below.** |

Four of the five parts of a learning system are built. The corpus source and the
policy are the holes.

## Recipe Surface Inventory — measured 2026-08-29

The dictionary is not one file. Found by inspection, in order of discovery:

| # | Surface | What it is | Evidence |
|---:|---|---|---|
| 1 | `chronos_geometry_plan::shape_thinking::think_from_brief` | 5 keyword matchers over noun lists, 3 of which replay a stored seed; vessel branch picks between 4 hardcoded magic-number profiles | `is_structure_brief` contains "pagoda" and "house" verbatim; "gnarled tree root" == "bicycle chainring" == "differential gearbox housing", byte-identical plans |
| 2 | `chronos_priors::classify_prompt` | noun to `ShapeFamily` table, 194 `ShapeFamily::` references, documented in `MASTER_GUIDE.md` section 12.7 as the "Universal Noun Path" with a 4-tier fallback ending in "any remaining noun gets `ShapeFamily::Box` at confidence 0.10" | pinned by a test literally named `every_noun_classifies_into_a_buildable_family` (25-noun sweep) |
| 3 | Named `PrimitiveKind`s | compiled nouns, described in the 2026-08-15 plan as "a floor, not the ceiling" | the ceiling was never built, so the floor became the product |

Surface 2 is the one to watch. It is not a shortcut somebody left in — it is
**documented as a feature**, with a passing test whose name asserts that every
noun resolves. A test named `every_noun_classifies_into_a_buildable_family` is a
test that the dictionary is complete. Under the directive, completeness of a
dictionary is not a goal; the dictionary is the defect.

Honest note on process: this inventory was assembled after the phase design
below was written, and it widens the fence from one function to three surfaces.
The phases do not change. The fence does.

## Critical Measured Constraint

`score_mesh_render(png, expected: &MeshEditExpectedMetrics)` scores a render
against metrics **derived from the plan**, not against a text brief.

That means the existing scorer answers *"did the executor do what the program
said?"* It is a consistency signal. It is exactly right for Phase 0 and Phase 1
and it is useless for supervising language. Any plan that assumes the current
scorer can grade brief-to-shape correspondence is wrong.

## Phases

Each phase must pass before the next is authorized. No phase may be skipped
because a later one looks more like the product.

### Phase 0 — Operation semantics (forward model)

**Question:** given a program, what geometry results?

Chronos2 samples valid programs from the operation space, executes them, and
records program, resulting mesh metrics, render, silhouette, and view score.
Primus trains a model to predict the geometry metrics from the program alone.

- Data contains **no object class, no name, no brief, no label**. There is
  nowhere to put a noun.
- Holdouts are by **program structure** — sequence length, operation mix,
  nesting depth — never by object class, because object classes are nouns.
- Declared baselines, fixed before training: predict the training mean; predict
  from operation count alone; nearest-neighbour over programs.
- **Pass:** beats every declared baseline on structurally held-out programs.
- **Fail:** does not beat them. Then the action space or the metric set is wrong,
  and that is the finding — do not proceed to Phase 1 on a failed forward model.

This is the honest version of what the synthetic generator pretended to be. The
ground truth is a real renderer executing real Blender operations, not
closed-form arithmetic somebody wrote.

### Phase 1 — Program induction (inverse model)

**Question:** given a shape, what program produces it?

Trained on the Phase 0 corpus, reversed. Evaluated by **re-executing** the
predicted program and scoring the result against the target with the existing
scorer — the repo can already do this.

This is where geometry understanding actually lives. The model has to learn that
a taper narrows a top, that a subtract makes a cavity no intersection of
silhouettes can reach, that a bevel eats an edge. Those are facts about
operations, learned from the operations.

- Still no language, still no nouns.
- **Pass:** re-executed predictions beat nearest-neighbour-program retrieval on
  structurally held-out targets.
- **Fail:** the silhouette scorer is too weak a signal to distinguish programs.
  That is a real possible outcome and it is measurable early — see Risks.

### Phase 2 — Search, then distillation

Use the Phase 0 forward model to evaluate candidate programs **without Blender**,
making search cheap. Search finds programs for targets the inverse model misses.
Distil the search results back into the policy.

Still no language. Still no nouns.

### Phase 3 — Language, attached last, attached to shape

Only after 0–2 work. Language maps into the learned shape space; it never maps
to programs directly, because that mapping is a dictionary by construction.

The test that this has not become a recipe:

- A novel compound brief must produce a program not present in training.
- Deleting one word from a brief must change the output **continuously**, not
  switch branches. Branch-switching on a keyword is the signature of a lookup.
- Two unrelated novel briefs must not produce identical programs. On
  2026-08-29, `think_from_brief` failed exactly this: "a gnarled tree root", "a
  bicycle chainring", and "a differential gearbox housing" returned byte-identical
  plans.

If Phase 3 cannot be done without a dictionary, **it does not ship**. Per the
operator directive: learn or not exist.

## Anti-Recipe Safeguards, Enforceable

Prose rules did not hold. These are checks.

1. The sampler samples the **operation space**. It is never seeded from a list of
   objects. A test asserts the corpus schema has no class, name, label, or brief
   field.
2. Holdouts are by program structure. A test asserts no object-class key exists
   in any split definition.
3. A repo test scans the planning and training path for noun-list literals — an
   array of three or more common object nouns — and fails if one appears. This is
   the check that would have caught `is_structure_brief`.
4. All three recipe surfaces above are **fenced**: no new keywords, no new
   branches, no new seeds, no new noun-to-family entries, no new hardcoded
   profiles. They stay only because the product calls them today and removing
   them breaks it. Each is deleted when a learned policy replaces it. Adding a
   noun to any of them is a law violation, not a bug fix.
5. Any phase reporting a result must state which baselines it beat, on which
   structural holdout, or it is not a result.

## Repo Split — Why Tandem

| Repo | Role | Owns |
|---|---|---|
| `C:\chronos2` | **the world** | operation space, executor, renderer, scorer, acceptance gate, Codex sealing, program sampler, corpus emission |
| `C:\Primus` | **the learner** | frozen hash-pinned inputs, candidate lifecycle, declared baselines, structural holdouts, promotion governance, rejection discipline |

This is not an arbitrary division. It is where each repo is already strong.
Chronos2 has a working sealed executor and a calibrated scorer. Primus has the
only genuinely non-recipe result in either repo — the BridgeData work — and the
governance that produced it: hash-pinned frozen inputs, predeclared acceptance
rules, split-separated metrics, error bars, and two candidates rejected from
promotion despite passing.

That governance is the asset. Point it at geometry.

**Interface:** a hash-pinned corpus manifest, exactly the discipline of the
BridgeData intake — SHA-256 over data, splits, and schema, verified before
training, during training, and at evaluation.

## Risks, Named Before Starting

1. **The scorer may be too weak.** `silhouette_v0.1` is silhouette + bbox IoU,
   and the worst known-good sample scores 0.1837 against a 0.15 threshold. That is
   a thin margin. If two visibly different programs score the same, Phase 1 has no
   gradient. **Measure this first** — score a set of deliberately different
   programs and check the scores separate. If they do not, the scorer is the first
   thing to build, not the model.
2. **Blender round-trip cost bounds the corpus.** Every sample is a real render.
   Measure throughput before promising a corpus size.
3. **glTF triangulation loses topology.** Found 2026-08-28: assets round-trip
   through glTF, which stores triangles only, so quad face identity is gone by the
   time an operation selects a face. This may distort operation semantics and
   needs a decision — keep `.blend` in the loop, or accept triangulated semantics.
4. **The action space may be too small.** Ten operations may not span the shapes
   the product needs. That is discoverable in Phase 1 and is a finding, not a
   failure.

## What This Plan Does Not Authorize

No implementation. No corpus generation. No training. No deletion of
`think_from_brief` or the synthetic generator. No product or installer change. No
claim about learned behaviour until Phase 0 beats its declared baselines.

## First Executable Step

Not a model. A measurement: **does the existing scorer separate visibly different
programs?** Everything downstream depends on the answer, it is cheap, and it can
be run against machinery that already works.

## Next-Agent Pickup

Read the Chronos2 copy of this plan before touching either repo. If you are about
to add a keyword, a noun list, a per-shape default, or a stored sample keyed by a
name, stop — that is the failure this plan exists to prevent, and repo law rule 9
(Primus) / non-negotiable 8 (chronos2) forbids it.
