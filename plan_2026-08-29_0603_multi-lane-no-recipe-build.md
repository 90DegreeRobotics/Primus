# Plan — Multi-Lane No-Recipe Build (Claude / Codex / Manus)

**Date:** 2026-08-29 0603 CDT
**Status:** ACTIVE — three lanes may start immediately
**Repos:** tandem. Identical copy in `C:\chronos2` at the same filename.
**Operator:** away during execution. Every lane must be able to finish or park
without asking a question.

Parent architecture: `plan_2026-08-29_0552_no-recipe-geometry-understanding.md`
(both repos). Read it before starting. This document is the work split only.

---

## 0. The Rule That Matters Most While Michael Is Away

**No lane improvises past a blocker.** If a lane hits a stop condition, it writes
`handoff_<agent>_2026-08-29_<lane>-BLOCKED.md`, commits it, pushes, and stops
that lane. It does not switch to another lane's files, does not invent a
substitute input, and does not relax a gate to make something pass.

A parked lane with an honest blocker is a good outcome. A lane that improvised is
worse than a lane that stopped.

---

## 1. Lane Assignment

Assigned from demonstrated strength in the 2026-08-26..28 handoff record, not
from preference. Michael may reassign freely.

| Lane | Agent | Why | Repo |
|---|---|---|---|
| **A — Measure and Sample** | Claude | Drove the cross-repo Rust/Blender debugging on 2026-08-28 and has the executor loaded | `C:\chronos2` |
| **B — Learner Intake** | Manus | Built the BridgeData transition gate, rollout harnesses, and candidate lifecycles; this is the same shape of work | `C:\Primus` |
| **C — Enforcement and Debt** | Codex | Built the feasibility scans, evidence corrections, and compliance registers; this lane is verification | both |

---

## 2. Hard File Ownership

Three agents on one `main` in two repos. **Ownership is the collision
prevention.** A lane may create and edit only the paths listed for it.

### Lane A owns (chronos2)
```
crates/chronos_geometry_plan/src/program_sampler.rs      (new)
crates/chronos_geometry_plan/src/lib.rs                  (module decl + re-export ONLY)
crates/chronos_vision/examples/scorer_separation.rs      (new)
out/**                                                   (ignored evidence)
handoff_claude_2026-08-29_lane-a-*.md
```

**Amended 2026-08-29 by Lane A.** The example was assigned to
`chronos_geometry_plan`, which cannot work: `chronos_dreamer` (the compiler) and
`chronos_vision` (the scorer) both depend on `chronos_geometry_plan`, so it
cannot depend on them. It lives in `chronos_vision`, which sees all three.
Declared here rather than silently exceeding the list.

### Lane B owns (Primus)
```
CCF_Sovereign/src/geometry_corpus/**                     (new package)
CCF_Sovereign/test_geometry_corpus*.py                   (new)
CCF_Sovereign/tmp/**                                     (ignored evidence)
handoff_manus_2026-08-29_lane-b-*.md
```

### Lane C owns (both)
```
C:\chronos2\crates\chronos_geometry_plan\tests\no_recipe_guard.rs   (new)
C:\chronos2\docs\CAPABILITY_MAP.md
C:\Primus\CCF_Sovereign\test_no_recipe_guard.py                     (new)
handoff_codex_2026-08-29_lane-c-*.md
```

### Owned by nobody — do not touch this session
`AGENTS.md`, `README.md`, `MASTER_GUIDE.md`, `ARCHITECTURE.md`, both `STATUS.md`,
`think_from_brief`, `classify_prompt`, any `PrimitiveKind`, the installer, the
desktop UI, `src/real_data`, and the synthetic trajectory generator.

**`STATUS.md` is deliberately unowned.** Each lane reports in its own handoff.
Truth surfaces get one consolidation pass afterwards, by one agent, so three
agents never append to the same file tail.

---

## 3. Shared Push Protocol

All three lanes push to `main` in shared repos. Non-optional:

```pwsh
git pull --rebase origin main
# ... work ...
git diff --check
git add -- <explicit owned paths only>
git diff --check --cached
git pull --rebase origin main
git push origin main
```

- **Never `git add -A`.**
- If a rebase conflicts in a file **you do not own**, stop. Do not resolve it.
  Write the blocked handoff and park.
- Commit small and push often. A lane holding six hours of unpushed work is a
  merge problem waiting to happen.

---

## 4. Exclusive Resource: Blender

**BlenderMCP on `tcp://127.0.0.1:9876` is a single shared process. Lane A owns it
exclusively.**

Lanes B and C must not start Blender, must not run `dreamer run-s3v`, and must
not execute anything against port 9876. Two lanes driving one Blender session
silently corrupts both sets of results — the scene is global mutable state.

If Lane A finishes and releases it, that is recorded in Lane A's handoff.

---

## 5. The Corpus Contract — frozen now so lanes can work in parallel

Lane B must not wait for Lane A's code. **Both build against this written
schema.** If Lane A needs to change it, that is a blocker handoff, not a silent
edit.

`geometry_program_corpus_v1`, one JSON object per line:

```json
{
  "schema_version": "geometry_program_corpus_v1",
  "sample_id": "sha256 of canonical program JSON",
  "program": { "...MeshEditPlan JSON..." },
  "program_structure": {
    "step_count": 4,
    "op_mix": {"CreateCube": 1, "PullFace": 2, "BevelEdges": 1},
    "op_signature": "BevelEdges|CreateCube|PullFace"
  },
  "executed": true,
  "mesh_metrics": {
    "vert_count": 28, "face_count": 18,
    "bbox_min_mm": [-0.5, -0.5, -0.5], "bbox_max_mm": [1.156, 0.5, 0.5]
  },
  "render": {"path": "...", "sha256": "...", "width": 960, "height": 540},
  "view_score": {
    "score": 0.41, "silhouette_overlap": 0.44, "bbox_iou": 0.35,
    "scorer_version": "silhouette_v0.1"
  }
}
```

**Forbidden keys, at any nesting depth:** `class`, `object_class`, `label`,
`name`, `brief`, `prompt`, `category`, `family`, `noun`, `kind_name`. Lane C's
guard test enforces this. This is the anti-recipe rule made structural: the
corpus has nowhere to put a noun.

A manifest accompanies the corpus with SHA-256 over the JSONL, the split
definition, and the schema version — the BridgeData intake discipline, unchanged.

**Splits are by program structure only:**

| Split | Rule |
|---|---|
| `train` | default |
| `held_out_length` | all programs with `step_count` in a withheld band |
| `held_out_op_combo` | all programs whose `op_signature` contains a withheld operation pair |

Never by object class. Object classes are nouns.

---

## 6. Lane A — Measure and Sample (Claude, chronos2)

### A1. Scorer separation measurement — BLOCKING, do this first

Everything downstream assumes `silhouette_v0.1` can tell different programs
apart. Nobody has checked.

1. Hand-build 6–8 deliberately distinct valid `MeshEditPlan`s: tall column, wide
   slab, tapered spike, shelled vessel, cube with a subtraction, deep-bevelled
   block, an L via two extrudes, a lone cube as control.
2. Execute each through the sealed BlenderMCP path.
3. Score **every render against every plan's expected metrics** — the full N×N
   matrix.
4. Report: diagonal mean, off-diagonal mean, separation margin, and the worst
   confusable pair.

**Pass:** the diagonal dominates with a margin that survives the 0.15 threshold.
**Fail:** it does not. Then **the scorer is the deliverable**, not the sampler,
and Lane A stops and reports rather than proceeding to A2.

The probe plans are a measurement instrument **only**. They must not be retained
as a seed library, a curriculum, or a plan source. Delete them or fence them in
the example file once the matrix is recorded — a kept set of named example shapes
is how a recipe book starts.

### A2. Program sampler — only if A1 passes

`program_sampler.rs`: sample valid programs from the operation space under
`MeshEditPlan::validate`. Seeded, deterministic, reproducible from the seed alone.

- Samples the **operation space**. Never a list of objects, never a target shape.
- Rejection-samples against `validate()`; records the rejection rate as evidence
  of how much of the space is legal.
- Emits `geometry_program_corpus_v1` records for executed samples.
- Unit tests: determinism from seed; every emitted program passes `validate`; no
  forbidden key appears in the record.

Measure and report Blender round-trip throughput — samples per minute bounds the
corpus size, and nobody should promise a corpus size before it is measured.

### Lane A stop conditions
Scorer fails to separate; BlenderMCP unreachable; the action space cannot produce
valid programs at a usable rate; a corpus schema change is needed.

---

## 7. Lane B — Learner Intake (Manus, Primus)

Build the consumer side against the §5 contract. **No model training this
session.**

### B1. Frozen intake
`CCF_Sovereign/src/geometry_corpus/` — load and hash-verify a
`geometry_program_corpus_v1` JSONL and manifest, using the same discipline as the
BridgeData intake: SHA-256 over data, splits, and schema, verified at load and
re-verified at evaluation. Refuse on any mismatch.

### B2. Structural splits
Implement `held_out_length` and `held_out_op_combo`. Prove by test that:
- no program appears in two splits,
- no `op_signature` in `held_out_op_combo` appears in `train`,
- split membership is derivable from `program_structure` alone.

### B3. Declared baselines, no model
Implement and test the three Phase 0 baselines, declared before any model exists:
predict the training mean; predict from `step_count` alone; nearest-neighbour
over `op_mix`. They must run on a corpus and emit split-separated metrics.

### B4. Synthetic fixture, clearly labelled
Lane A's corpus will not exist yet. Build a **hand-written fixture** conforming
to the schema so B1–B3 are testable. It must be named `*_fixture_*`, and every
test using it must assert it is a fixture. It is never evidence, never a result,
and never cited outside its own test.

### Lane B stop conditions
The §5 schema is insufficient; the BridgeData intake pattern does not transfer;
splits cannot be made disjoint from structure alone.

**Lane B must not:** train a model, create a candidate, touch `src/real_data`,
touch the frozen BridgeData intake, extend the synthetic trajectory generator, or
run Blender.

---

## 8. Lane C — Enforcement and Debt (Codex, both repos)

Prose rules did not hold last time. This lane makes them executable.

### C1. The no-recipe guard — the highest-value item in this plan

A test in each repo that **fails** when a noun dictionary appears.

Detection, at minimum:
- an array or match arm listing **three or more** common object nouns,
- a `match`/`if` chain keyed on string literals that returns a plan, family,
  primitive, or parameter set,
- a corpus or fixture record containing any §5 forbidden key at any depth.

Practical requirement: it must **fail today** against
`chronos_priors::classify_prompt` and `shape_thinking::is_structure_brief`, then
be given an explicit, dated, individually-listed allowlist for exactly those
known-fenced surfaces — so a *new* dictionary trips it while the fenced ones stay
visible as named debt.

An allowlist entry is a confession, not an exemption. Each entry names the
surface, the date, and the plan that retires it.

If a broad detector proves impossible, ship the narrow version that catches the
forbidden-key case and report honestly what it cannot catch. A guard that catches
one real class is worth more than a design for one that catches all of them.

### C2. Capability map debt
`check_reachability.ps1` reports **4 rows falsely claiming LIVE**: Shape guard,
Evolution Proof, Measuring engine, Windows signing. Verified 2026-08-29 as
pre-existing — the same 4 fail against committed `HEAD`.

For each row: determine whether it is genuinely live, and either fix the cited
test reference or relabel the row honestly. Do not relabel without investigating;
that is how the map started lying.

The gate's own note says it resolves Rust `fn` under `crates/**` only, so rows
citing Python tests cannot pass it. Determine whether that is the whole
explanation for each of the 4, and say so per row.

### Lane C stop conditions
A row's true status cannot be determined without running the installed GUI (that
is Michael's, never an agent's); the guard cannot be written without
false-positives across the whole tree.

**Lane C must not:** run the installer, run Blender, or edit any surface it does
not own.

---

## 9. Definition of Done, Per Lane

A lane is done when **all** hold:

1. Its owned files are committed and pushed to `origin/main`.
2. `git status --short --branch` is empty but for the branch header.
3. `git rev-parse HEAD` equals `git rev-parse origin/main`.
4. Its gate ran and its real result is recorded — pass or fail.
5. A handoff exists naming: files touched, commands run, actual output, what was
   **not** run, what remains blocked, and the exact start/final commits.
6. No file outside its ownership list was modified.

"If you did not run it, you do not get to say it works" applies unchanged.

---

## 10. Order and Dependencies

```
Lane A1 (scorer measurement) ──► A2 (sampler) ──► corpus exists
Lane B1..B4 ─────────────────────────────────────► ready to consume it
Lane C1..C2 ─────────────────────────────────────► independent throughout
```

- **A1 blocks A2 only.** B and C never wait.
- B is decoupled from A by the §5 written schema, not by A's code.
- C is independent of both.

If A1 fails, B and C still complete. That is the point of the split.

---

## 11. What No Lane May Do

No installer execution. No deletion of any recipe surface (they are fenced, not
removed — removal breaks the product today). No model training. No promotion. No
product or UI behaviour change. No claim of a learned result. No editing another
lane's files. No `git add -A`. No force push. No relaxing a gate to make
something pass.

---

## 12. Consolidation, After The Lanes

One agent, one pass, once Michael is back or all three lanes have parked:
fold the three handoffs into both `STATUS.md` files and reconcile
`CAPABILITY_MAP.md`. Deliberately not parallel — that file tail is the one place
three agents would reliably collide.

---

## 13. Next-Agent Pickup

Read `plan_2026-08-29_0552_no-recipe-geometry-understanding.md` in both repos
first. Then find your lane above, confirm nobody else has pushed to your owned
files, and start at your lane's first numbered item.

If you are about to add a keyword, a noun list, a per-shape default, or a stored
sample keyed by a name: **stop.** That is the failure this whole plan exists to
prevent. Primus rule 9 / chronos2 non-negotiable 8.
