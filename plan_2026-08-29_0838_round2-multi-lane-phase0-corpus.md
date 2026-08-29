# Plan — Round 2 Multi-Lane: Phase 0 Corpus (Claude / Codex / Manus)

**Date:** 2026-08-29 0838 CDT
**Status:** ACTIVE — three lanes may start immediately
**Repos:** tandem. Identical copy in `C:\chronos2` at the same filename.
**Operator:** may be away. Every lane must finish or park without asking.

Parent architecture: `plan_2026-08-29_0552_no-recipe-geometry-understanding.md`.
Round 1 split: `plan_2026-08-29_0603_multi-lane-no-recipe-build.md`.
Read both before starting.

---

## 0. What Round 1 Established

| Lane | Result |
|---|---|
| A (Claude) | **A1 FAILED.** `silhouette_v0.1` separation is **−0.1721**: a render scores better against a *wrong* plan than its own. Only 2 distinct reference masks across 8 distinct plans. A2 correctly not started. |
| B (Manus) | Frozen `geometry_program_corpus_v1` intake, structural holdouts, 3 declared baselines. 6 tests. Built against a fixture; no real corpus exists. |
| C (Codex) | No-recipe guards in both repos; capability map honest, `check_reachability` exits 0. Guard later widened to whole-file scan; 4 confessed surfaces. |

Round 1's dependency split worked: A failed and B and C still completed.

---

## 1. The Decision This Plan Encodes

**The render is the wrong observation for Phase 0.**

`score_mesh_render` compares a silhouette to a centred rectangle parameterised by
one scalar. It cannot see a cavity, a bevel, a taper, or a hole. Phase 0 is
supposed to predict **geometry**, and geometry is measurable directly from the
executed mesh — vertex and face counts, bounding box, volume, surface area,
component count. Those separate every pair that defeated the view score.

So Phase 0 becomes: **program → mesh metrics.** The render is retained as
evidence a human can look at, and `view_score` stays in the record as metadata,
but **neither is a learning target or a gate.**

> **Assumption, stated because it was not explicitly confirmed.** If the operator
> prefers to fix the scorer and keep a pixel signal instead, this plan changes in
> exactly one place — Lane A builds a scorer rather than a metrics extractor —
> and Lanes B and C are unaffected. Say so and it is a one-lane edit, not a
> replan.

---

## 2. Corpus Contract v2 — amended, not silently edited

Round 1 §5 froze `geometry_program_corpus_v1`. Lane A's finding requires a richer
`mesh_metrics`. Per the Round 1 rule, a contract change is declared, so this is
**`geometry_program_corpus_v2`**. v1 records remain readable; v2 adds fields and
demotes `view_score`.

```json
{
  "schema_version": "geometry_program_corpus_v2",
  "sample_id": "sha256 of canonical program JSON",
  "program": { "...MeshEditPlan JSON..." },
  "program_structure": {
    "step_count": 4,
    "op_mix": {"CreateCube": 1, "PullFace": 2, "BevelEdges": 1},
    "op_signature": "BevelEdges|CreateCube|PullFace"
  },
  "executed": true,
  "mesh_metrics": {
    "vert_count": 28,
    "edge_count": 44,
    "face_count": 18,
    "tri_count": 32,
    "loose_part_count": 1,
    "bbox_min_mm": [-0.5, -0.5, -0.5],
    "bbox_max_mm": [1.156, 0.5, 0.5],
    "bbox_extent_mm": [1.656, 1.0, 1.0],
    "volume_mm3": 1656.0,
    "surface_area_mm2": 912.0,
    "is_closed": true
  },
  "render": {"path": "...", "sha256": "...", "width": 960, "height": 540},
  "view_score": {
    "score": 0.41, "scorer_version": "silhouette_v0.1",
    "note": "metadata only; not a learning target or gate (Lane A1, 2026-08-29)"
  }
}
```

**Forbidden keys, at any depth, unchanged:** `class`, `object_class`, `label`,
`name`, `brief`, `prompt`, `category`, `family`, `noun`, `kind_name`.

**Splits unchanged:** `train`, `held_out_length` (by `step_count` band),
`held_out_op_combo` (by withheld operation pair in `op_signature`). Never by
object class.

`volume_mm3` and `surface_area_mm2` are the two fields that make a hollow shell
distinguishable from a solid cube. `loose_part_count` and `is_closed` catch
booleans that shatter or open a body. If any of these cannot be computed
reliably in Blender, that is a Lane A blocker handoff, not a silent omission.

---

## 2b. The Decision On How This Stays Out Of Recipe Territory

Two mechanisms, in priority order. The second is the one that actually wins.

### Defence 1 — measure the output space (the gate that cannot be evaded)

Source scans catch the lazy version. They do not catch a table that moves into
data, a seed file, a prompt template, or magic-number profiles. What defines a
recipe book is that **distinct outputs are bounded by a maintained table**, and
that is measurable directly.

`crates/chronos_geometry_plan/tests/novelty_ratchet.rs` feeds compositionally
generated briefs — never a curated noun list — through the live path and counts
distinct programs out.

**Measured 2026-08-29: 200 briefs produced 7 distinct programs, 4 operation
signatures, novelty ratio 0.035.** All 7 came from the modifier words. The
subject of the brief contributed nothing: for any subject outside the dictionary
the system has exactly seven answers.

A ratchet, not a red test. Raise the floor as the system improves; lowering it is
a law violation. This number is the headline metric for the whole programme — if
it is not climbing, nothing else that is being built matters.

### Defence 2 — remove the pressure that creates recipes

Recipes do not appear because agents are careless. They appear because the
dictionary **works today** and the learned path does not, and something has to
answer a brief before the model exists. Every guard in the world loses to that.

So the fix is to make a non-recipe path work *early*: **search over the operation
space, scored by mesh metrics.** The program sampler in A4 plus the metric
evaluator in A1 already compose into one — sample candidates, score against a
target, keep the best, iterate. Nothing about it is a table.

This is also what the project thesis already said:

> The LLM is used not to generate the final plan, but to act as an intelligent
> heuristic or "idea generator" that guides a more rigorous, underlying symbolic
> planner.

Read against the gate above: **the LLM must emit targets in metric space — tall,
hollow, roughly 2:1, closed — never a program and never a noun lookup.** Search
supplies the rigour. The LLM is allowed to be fuzzy precisely because it is not
the thing choosing operations.

An LLM mapping words to metric targets is not a recipe book: the target space is
continuous, it generalises to subjects nobody enumerated, and there is no table
in the repo to maintain. That is the difference between a model that generalises
and a dictionary somebody keeps up to date.

**Consequence for sequencing:** the learned Phase 0/1 models replace search for
*speed*, not for *capability*. Search is what retires `think_from_brief`, and it
can exist long before a model does. Round 2's sampler is therefore not only
corpus infrastructure — it is the first non-recipe answer path.

## 3. Lane Assignment And Ownership

| Lane | Agent | Focus |
|---|---|---|
| **A — Metrics and Sampler** | Claude | make the executor report real geometry, then sample the operation space |
| **B — Phase 0 Learner** | Manus | v2 intake, richer baselines, training harness ready for a real corpus |
| **C — Independent Verification** | Codex | re-derive Lane A's separation number, guard the corpus, audit the emitted data |

### Lane A owns (chronos2)
```
crates/chronos_dreamer/src/mesh_metrics.rs                 (new)
crates/chronos_dreamer/src/lib.rs                          (module decl + re-export ONLY)
crates/chronos_geometry_plan/src/program_sampler.rs        (new)
crates/chronos_geometry_plan/src/lib.rs                    (module decl + re-export ONLY)
crates/chronos_vision/examples/scorer_separation.rs        (existing; may extend)
crates/chronos_vision/examples/metric_separation.rs        (new)
out/**                                                     (ignored evidence)
handoff_claude_2026-08-29_r2-lane-a-*.md
```

### Lane B owns (Primus)
```
CCF_Sovereign/src/geometry_corpus/**                       (existing package)
CCF_Sovereign/test_geometry_corpus*.py                     (existing + new)
CCF_Sovereign/train_geometry_phase0.py                     (new)
CCF_Sovereign/test_train_geometry_phase0.py                (new)
CCF_Sovereign/tmp/**                                       (ignored evidence)
handoff_manus_2026-08-29_r2-lane-b-*.md
```

### Lane C owns (both)
```
C:\chronos2\crates\chronos_geometry_plan\tests\no_recipe_guard.rs
C:\chronos2\crates\chronos_vision\tests\metric_separation_audit.rs   (new)
C:\Primus\CCF_Sovereign\test_no_recipe_guard.py
C:\Primus\CCF_Sovereign\audit_geometry_corpus.py                     (new)
handoff_codex_2026-08-29_r2-lane-c-*.md
```

### Owned by nobody
`AGENTS.md`, both `README.md`, `MASTER_GUIDE.md`, `ARCHITECTURE.md`, both
`STATUS.md`, `CAPABILITY_MAP.md`, `think_from_brief`, `classify_prompt`, any
`PrimitiveKind`, the installer, the desktop UI, `src/real_data`, and the
synthetic trajectory generator.

Same rules as Round 1: `pull --rebase` before every push, explicit pathspecs
only, never `git add -A`, park rather than resolve a conflict in a file you do
not own, and **BlenderMCP on :9876 is exclusive to Lane A**.

---

## 4. Lane A — Metrics and Sampler (Claude, chronos2)

### A1. Mesh metrics extraction — BLOCKING

Make the executed mesh report the §2 `mesh_metrics` block. Blender computes all
of it: `len(mesh.vertices/edges/polygons)`, `loop_triangles`, bound box,
`bmesh.ops` for volume via `calc_volume(signed=False)`, area via summed
`polygon.area`, loose parts by walking linked geometry, closedness by checking
for boundary edges.

### A2. Metric separation — the gate A1 exists to pass

Rerun the Round 1 probe set against **metrics** instead of the view score. Same
8 plans, same N×N structure, distance in normalised metric space.

- **Pass:** every probe is nearest to itself; diagonal separation is positive and
  the worst confusable pair is still distinguishable.
- **Fail:** two visibly different bodies collide. Then report which metric is
  missing rather than proceeding — the same discipline that stopped A2 in
  Round 1.

Specifically it must separate the four that the view score could not:
`lone_cube`, `deep_bevelled_cube`, `pierced_cube`, `hollow_shell`.

### A3. Fix the blank-render defect

At 20 mm, four of eight probes rendered **completely blank** while Blender exited
0 and wrote a valid PNG. All were compact bodies; 20 mm is 0.02 Blender units.
The camera reframing does not handle small bounding boxes.

This must be fixed before corpus generation, or every small sample silently
carries a blank render. Not a learning-signal issue any more, but it is a real
defect and the render is the human-inspectable evidence.

### A4. Program sampler — only after A2 passes

Sample valid programs from the operation space under `MeshEditPlan::validate`.
Seeded, deterministic, reproducible from the seed alone. Samples **operations**,
never objects. Records the rejection rate as evidence of how much of the space is
legal. **The guard watches this file** — it will fail on object nouns in it.

### A5. Corpus emission

Emit `geometry_program_corpus_v2` JSONL plus a manifest with SHA-256 over data,
splits, and schema. Report Blender throughput in samples per minute; corpus size
follows from measurement, not from a promise.

### Lane A stop conditions
A2 fails; a §2 metric cannot be computed reliably; the sampler cannot produce
valid programs at a usable rate; BlenderMCP unreachable.

---

## 5. Lane B — Phase 0 Learner (Manus, Primus)

### B1. v2 intake
Extend the existing intake to `geometry_program_corpus_v2`. Keep v1 readable.
Assert `view_score` is **never** read as a target or a filter — a test should
fail if it is.

### B2. Baselines on the richer target set
Extend the three declared baselines to predict the full `mesh_metrics` vector,
reporting per-metric and split-separated error. Declared before any model.

### B3. Phase 0 training harness
`train_geometry_phase0.py`: consume a frozen v2 corpus, train a small model to
predict `mesh_metrics` from `program` + `program_structure`, evaluate against the
declared baselines on both structural holdouts.

Same discipline as the BridgeData lane: frozen hash-pinned inputs, isolated
candidate directory, no promotion operation, atomic manifest, rejection by
default.

**Do not train on the fixture and report it as a result.** The fixture proves the
harness runs. A result requires Lane A's real corpus.

### B4. Fixture upgrade
Extend the labelled fixture to v2 so B1–B3 are testable before the corpus lands.
Still named `*_fixture_*`, still asserted as a fixture, still never evidence.

### Lane B stop conditions
The v2 contract is insufficient; splits cannot be made disjoint from structure
alone; the harness cannot run without a real corpus.

**Lane B must not:** run Blender, touch `src/real_data` or the frozen BridgeData
intake, extend the synthetic trajectory generator, or promote anything.

---

## 6. Lane C — Independent Verification (Codex, both repos)

Round 1 showed the value of an independent auditor. This round, verification
gates the science.

### C1. Independently re-derive Lane A's separation number
Do **not** read Lane A's harness and confirm it. Compute the metric-separation
result independently from the emitted metrics and say whether you get the same
answer. One number gates the entire round; two agents should reach it separately.

If Lane A reports pass and Lane C reports fail, **that is the finding**, and the
round parks until the operator arbitrates.

### C2. Corpus audit
`audit_geometry_corpus.py`: given an emitted corpus and manifest, verify hashes,
schema conformance, forbidden-key absence at any depth, split disjointness,
absence of duplicate `sample_id`, and that `program_structure` is actually
derivable from `program` — i.e. the structure fields were not written by hand.

### C3. Extend the guards
- Rust guard: watch `program_sampler.rs` and `mesh_metrics.rs` for object nouns.
- Python guard: extend forbidden-key checks to v2 records.
- Consider whether `is_cube_block_brief` and `is_cross_brief` — currently named
  but not allowlisted, because they branch on shape words rather than object
  nouns — deserve a separate shape-word detector, or should stay named-only. A
  reasoned decision either way, recorded.

### Lane C stop conditions
Lane A's corpus does not exist yet (C2/C3 can still proceed against the fixture);
an independent re-derivation cannot be built without duplicating Lane A's code.

---

## 7. Order And Dependencies

```
A1 metrics ──► A2 separation gate ──► A4 sampler ──► A5 corpus
                     │                                   │
                     └──► C1 independent re-derivation    └──► C2 corpus audit
B1..B4 ────────────────────────────────────────────────► ready to consume
C3 guards ──────────────────────────────────────────────► independent throughout
```

- **A2 is the gate for the round.** If it fails, no corpus, no training.
- B never waits: it builds against the §2 written contract.
- C1 waits only on A1's emitted metrics. C2/C3 never wait.
- A3 (blank renders) is independent of the gate and can be done any time.

---

## 8. Definition Of Done, Per Lane

1. Owned files committed and pushed to `origin/main`.
2. `git status --short --branch` empty but for the branch header.
3. `HEAD == origin/main`.
4. Gate ran, real result recorded, pass or fail.
5. Handoff naming files touched, commands run, actual output, what was **not**
   run, what is blocked, and exact start/final commits.
6. No file outside the ownership list modified.

---

## 9. What No Lane May Do

No installer. No deletion of a fenced recipe surface. No promotion. No product or
UI change. No training on a fixture reported as a result. No claim of a learned
result without a named baseline and a named structural holdout. No editing
another lane's files. No `git add -A`. No relaxing a gate to make something pass.

---

## 10. Next-Agent Pickup

Read the parent architecture plan and the Round 1 split first. Then find your
lane. If you are about to add a keyword, a noun list, a per-shape default, or a
stored sample keyed by a name: **stop.** Primus rule 9 / chronos2
non-negotiable 8, and the guard will catch you in the watched paths.

If you are about to report a number, name the baseline it beat and the structural
holdout it beat it on, or do not report it.
