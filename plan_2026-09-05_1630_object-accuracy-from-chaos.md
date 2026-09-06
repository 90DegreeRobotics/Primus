# Plan — Raising Object Accuracy From Chaos Prompts

**Date:** 2026-09-05 1630 CDT
**Status:** COMPLETE
**Scope:** Increase how often an arbitrary, unrehearsed Object prompt produces a
recognisable built body on the live compiler path. Theory → measurement →
experiment → implementation → signed build.

## Governing constraints

- `main` only. No branch, worktree, or clone.
- No noun recipes, no named-object generators, no hardcoded parameter profiles.
  Every intervention here is a *measurement or feedback loop*, not a table.
- The operator installs. Agents build, hash, and deliver to Downloads.
- Render witnesses must be shown in chat before any candidate is called good.

## The path under study

Buyer Object mode now routes to `chronos first-light` (no `--geometry-forge`),
which is:

```
prompt
  → SceneSketchConductor::generate      crates/chronos_dreamer/src/conductor.rs
      one Ollama call, qwen2.5:7b-instruct, temperature 0.2, format=json
      up to 3 attempts — but ONLY on JSON/schema/sandbox failure
  → shape_lexicon::enforce               forces kind=custom + geometry_program
                                         for anything not in the base alphabet
  → geometry_sandbox::check_geometry_program   STATIC STRING SCAN ONLY
  → SketchBlenderCompiler::compile_with_textures_and_seed
  → Blender: exec(source) inside _chronos_run_geometry_program
```

## Theory — five reasons accuracy is low

**T1. The geometry program is never executed before the render.**
`check_geometry_program` (`crates/chronos_dreamer/src/geometry_sandbox.rs`) is a
lowercased substring scan. It proves the source has no `import os` and mentions
`bpy.data.objects.new`. It does not prove the Python parses, runs, or builds
anything. The first execution is inside the final render script at
`compiler.rs:1623` — `exec(source, g, g)` with **no exception handling**. A
model that emits one bad face index kills the whole render, and the buyer waits
several minutes for nothing. This is the mechanism behind "PRODUCE NOTHING".

**T2. The sandbox bans the mesh-authoring library.**
`bmesh` is on `forbidden_imports()`. `bmesh` performs no I/O, no network, no
filesystem access — it is pure in-memory geometry. Banning it removes extrude,
bevel, subdivide, spin/lathe, solidify, inset and boolean: exactly the
operations that turn a box into a recognisable object. What is left is
hand-written `from_pydata` vertex soup. A 7B model writing raw coordinate lists
has a low ceiling no amount of prompting will lift.

**T3. One sample, temperature 0.2, no selection.**
There is no candidate diversity and nothing to choose between. The retry loop
fires on malformed JSON only, so a program that parses cleanly and builds a flat
four-vertex plane is accepted in silence.

**T4. No decomposition.** "a mountain range" arrives as one object the model
must nail in one program.

**T5. Nothing scores the result.** `chronos_vision` scores silhouettes against a
reference (carve only). `create_readiness` catches blank frames. Neither knows
whether the mesh resembles the words. With no metric there is no gradient, and
no way to tell whether any change helped.

## Interventions to test

| ID | Intervention | Predicted effect |
|----|--------------|------------------|
| I1 | Execute each program in headless Blender before the render; on failure feed the traceback back to the model for repair | Turns render death into a repaired mesh |
| I2 | Allow `bmesh` (pure geometry, no I/O) and teach the prompt to use it | Higher structural richness per program |
| I3 | Best-of-N sampling scored by a mesh-health critic | Raises median, removes degenerates |
| I4 | Part-decomposition turn before geometry | Multi-part bodies |
| I5 | Larger local model (`qwen2.5:14b-instruct`, already cached) | Better code, more VRAM |

## Measurement

`scripts/geometry_accuracy_probe.py` — a developer harness (not a product
surface). For a corpus of chaos prompts it calls the live Ollama with the real
conductor prompt, extracts every `geometry_program`, and executes each one in
headless Blender 4.5 under a replica of the compiler's restricted-exec
environment. Per program it records: raised//did not raise, vertex and face
counts, loose parts, bounding-box dimensions.

Reported metrics:

- **`build_rate`** — programs that execute and leave a mesh with vertices.
  This is the dominant term; a program that raises is worth zero.
- **`solid_rate`** — of those, the fraction that are non-degenerate
  (>= 4 faces and a bounding box that is not effectively flat).
- **`rich_rate`** — fraction with >= 24 faces, i.e. beyond a box.
- **median verts / faces / parts** — structural richness.
- **`distinct_bodies`** — unique mesh fingerprints across distinct prompts,
  to catch saturation the way the novelty ratchet does for the planner.

Corpus: `scripts/chaos_prompts.json` — unrehearsed briefs including the two the
operator watched fail (`a wine glass`, `a mountain range`).

## Measured results

All figures from `out/geometry_accuracy/`, 24 chaos briefs, one sample each,
`qwen2.5:7b-instruct` at temperature 0.2.

### Baseline — the shipped behaviour on 2026-09-05

| Metric | Value |
|---|---|
| geometry programs emitted | 23 |
| **programs that executed and built a body** | **11 of 23 (`build_rate` 0.478)** |
| prompts that ended with any authored body | 7 of 24 (0.292) |
| median verts / faces | 64 / 34 |
| median call time | 28.8 s |

Twelve programs raised. In production each one propagates out of
`exec(source, g, g)` and kills the entire render script, so the buyer waits and
receives no picture at all. The failures were not exotic:

| Cause | Count |
|---|---|
| `rotation_euler=` passed as a `bpy.ops.mesh.primitive_*_add` keyword | 6 |
| operators that do not exist (`primitive_teapot_add`, `primitive_rocking_chair_add`, `primitive_knight_mesh_create`) | 3 |
| `bpy.ops.transform.scale` unavailable in background context | 1 |
| `SyntaxError: '(' was never closed` | 1 |
| `TypeError: couldn't access the py sequence` | 1 |

Nine of twelve are the same two mechanical mistakes about the Blender API.

### Latency — a separate defect found while measuring

`conductor.rs` never set `num_ctx`. Ollama therefore sized the window from its
own default: on the 12 GB card `qwen2.5:7b-instruct` loaded at **32768 tokens,
8.7 GB, 62%/38% CPU/GPU**, and a single sketch took **138–150 s**. Pinned to
8192 the same model loads at **5.3 GB, 100% GPU** and answers in **25–35 s**.
Nothing is truncated: system prompt plus response is far under 8192 tokens.

### bmesh alone — a real trade, in both directions

| Metric | baseline | bmesh + API truth |
|---|---|---|
| programs emitted | 23 | 35 |
| `build_rate` | **0.478** | **0.229** |
| median verts | 64 | **273** |
| median faces | 34 | **267** |

Given real modelling operations the model attempts far more, decomposes more
briefs into parts (a crab became five objects, a violin four), and produces
bodies roughly eight times richer — but it gets more of the mechanics wrong:
`ensure_lookup_table` (8), `rotation_euler` again (9), `bmesh.free()` instead of
`bm.free()`, `random` which it is not given.

**Conclusion: bmesh raises the ceiling and lowers the floor.** It must not ship
without something that catches mechanical errors. That is the repair loop.

Note also that the API-truth paragraph in the prompt did *not* stop
`rotation_euler`: it recurred 9 times with the correction present. Telling the
model is not enough. Showing it the traceback is the intervention that can work.

### The repair loop — the decisive result

`shipped+repair` is the new prompt, `bmesh` permitted, and two rounds of
execute-and-repair driven by the real traceback.

| Metric | baseline | prompt+bmesh only | **+ repair** |
|---|---|---|---|
| `build_rate` | 0.478 | 0.280 | **0.480** |
| prompts ending with a body | 0.292 | 0.208 | **0.375** |
| median faces | 34 | 576 | **512** |
| distinct bodies | 9 | 5 | **10** |

Repair pays for bmesh's lost reliability exactly, and keeps the richness: same
build rate as the shipped baseline, **15× the geometry**, **28% more briefs
served**, and no loss of output diversity.

Two smaller fixes measured on the way, worth 0.16 → 0.28 on their own:
`context` is what Blender's own script runner exposes and the model writes it
from habit (4 NameErrors); and a JSON-decoded program can carry real U+0008
bytes, which Python refuses outright (3 SyntaxErrors).

### Defects found by running the thing end to end

Measurement on programs is not the same as running the product. Rendering five
briefs through the shipped binary exposed three failures the harness could not
see:

1. **An empty focal object crashed the render.** `_add_showroom` computed
   `min(v.z for v in ws_verts)` over an empty sequence, so a brief whose
   geometry could not be built still produced no picture — the original
   complaint, one layer down. Framing now tolerates a bodiless carrier.
2. **A failed program left debris that was rendered as the answer.** A repaired
   rocking-chair program added a UV sphere and *then* died assigning the
   read-only `view_layer.active_object`. The sphere survived in the scene and
   was rendered: a white ball presented as a rocking chair, which is precisely
   the silent substitution the compiler documents as impossible. It also made
   the probe and the render disagree, which would have made the probe
   worthless. A failing program now has everything it created removed before
   the exception propagates.
3. **The new prompt pulled work away from better geometry.** Pushing the model
   toward authored programs made it emit `custom` + a program for "a wine
   glass" where the baseline correctly chose `vessel` and got the compiler's
   measured lathe. A kind-precedence rule now states plainly that a listed kind
   beats a program the model would write.

## Verification standard

An intervention ships only if it beats baseline on `build_rate` and does not
regress `distinct_bodies`, and only if real renders through the shipped
`chronos first-light` path are shown to the operator as PNG witnesses.

## Visual first-light witnesses (2026-09-05, `out/witness_d/`)

Pictures exist. Recognition does not. That is the honest result, and it is
why the signed build is for the operator to judge, not a storefront claim.

- `a wine glass` — three dark cylinders on the pedestal. The model ignored
  `vessel` and authored a program (`kind: cube` + three primitives).
- `a mountain range` — empty stage. The program raised; the empty-carrier
  path framed the room instead of crashing. That is the original "produce
  nothing" defect, one layer down, now a picture of absence.
- `a rocking chair` — a tan block. Built, not carved-refused.

## Work items

- [x] Write the probe harness and the chaos corpus
- [x] Measure baseline
- [x] Test interventions against baseline
- [x] Implement what wins; focused Rust + Python gates
- [x] End-to-end render witnesses through the real binary
- [x] Truth surfaces, commit, push, signed build to Downloads
