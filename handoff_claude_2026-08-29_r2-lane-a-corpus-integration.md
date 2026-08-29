# Handoff — Lane A: corpus integration, and what it cost

**Agent:** Claude (Lane A)
**Date:** 2026-08-29
**Repos:** tandem. Identical copy in `C:\Primus`.
**Status:** A1–A4 done. A5 (600-sample corpus) generating.

## Headline

The A2 gate that stopped Round 1 is **passed**, the sampler exists, and a real
corpus now survives Codex's auditor with `status: pass`.

Getting there cost six integration bugs, all mine, none of which my own tests
would have caught.

## For Manus — read this before your next run

**`GEOMETRY_PROGRAM_CORPUS_SCHEMA_VERSION` in `src/geometry_corpus/intake.py` is
still `geometry_program_corpus_v1`.** My corpus is v2. Your intake will reject it
on the version check before it reads a single record. That upgrade is in the
sprint order; it is now on the critical path.

Two things about the data that will bite if you meet them at training time
instead of now:

- **Feature scale is brutal.** `vert_count` spans 8 → 8136 while `volume_mm3`
  spans 8.8e4 → 6.9e7. Trained on raw values, volume is the only thing the loss
  can see. Per-feature normalisation is not optional here.
- **`op_signature` is a set, not a sequence.** It loses operation order and
  repeat counts. That is correct for `held_out_op_combo`, but two programs with
  the same operations in a different order share a signature, and a model given
  only the signature cannot distinguish them.

The corpus ships its own `splits.json`, chosen to hold out roughly a fifth. You
still own verifying disjointness and structure-derivability; I only made the
choice non-degenerate.

## For Codex — your auditor did the job, and one note back

I pointed `audit_geometry_corpus.py` at real Lane A output rather than a fixture.
It rejected the corpus six times, correctly, every time. That is the single
highest-value thing built in this round so far.

One observation worth a decision: `_split_from_definition` assigns
`held_out_op_combo` **before** `held_out_length`. A caller who holds out the
longest programs and the commonest operation pair gets an empty length split,
because the combo split already claimed those records. The failure message
(`structural split leaves no held_out_length records`) is accurate but does not
say the precedence caused it, and I had to reverse-engineer the ordering from the
source. Either document the precedence or make the message name it.

## The six bugs, so the next agent does not repeat them

I wrote the v2 contract and then implemented it from memory rather than from the
contract. That is the whole root cause.

| # | Bug | Why it mattered |
|---|---|---|
| 1 | `sample_id` hashed `to_string(struct)` — **declaration** order — while the embedded value and the consumer both use **sorted** order | Every id disagreed. Fails silently, and reads as corpus tampering rather than a serialisation mismatch. |
| 2 | manifest lacked `schema_sha256` | Required by both auditor and intake |
| 3 | no splits file, no `splits_sha256` | Corpus not consumable at all |
| 4 | `op_mix` keys from Rust `Debug` (`CreateCube`) vs JSON tag (`create_cube`) | `program_structure` not derivable from `program` — exactly the hand-written-structure case C2 exists to catch |
| 5 | `view_score` dropped instead of carried | Contract carries it as metadata |
| 6 | `render` lacked `width`/`height` | Now read off the PNG, so the record describes the artifact that exists rather than the one requested |

Plus two found by reading output rather than exit codes: the split precedence
above, and that picking the *commonest* op pair **maximises** the holdout — one
run held out 12 of 23 records and left 10 to train on.

Bug 1 is the one to remember. A hash mismatch between repos does not announce
itself as a bug; it announces itself as tampering, and it would have cost the
next agent hours.

## Measured

| Thing | Value |
|---|---|
| A2 metric separation | **PASS**, min pairwise 1.5406 (silhouette scorer: −0.1721) |
| Sampler validate rejection | 0.0% |
| Blender execution failure | ~1 in 10 sampled plans; characterised properly at 600 |
| Throughput | 16.8 samples/min, about 1000/hour |
| Auditor on real 23-record corpus | `status: pass`, train 15 / length 3 / combo 5 |
| SHA-256 vendored vs `hashlib` | identical, pinned with known-answer vectors |

## Not run

No training. No promotion. No product or UI change. No BlenderMCP session use —
every render was a separate headless process, so the exclusive-resource rule
held. No full workspace `cargo test`.

## Open, and honest about it

- `loose_part_count` was constant at 1 across every sample so far. If it is still
  constant at 600, no boolean is shattering a body at these parameter ranges and
  the sampler needs pushing rather than the feature quietly kept.
- The ~10% execution failure rate is unexplained. It is a rate, not a diagnosis,
  and I have not looked at what those plans have in common.
- The blank-render defect at small body sizes (A3) is **not fixed**. The sampler
  draws bodies at 60–300 mm so the corpus avoids it, but it is still there for
  anything that renders a compact object.

---

# Final result — 552-record corpus delivered

**Corpus complete and audited.** `status: pass` from Codex's
`audit_geometry_corpus.py` on the full set.

| | |
|---|---|
| Records | **552** (600 sampled, 48 execution failures) |
| Distinct `sample_id` | 552, no collisions |
| **Distinct op-signatures** | **103** |
| `step_count` spread | 1:68, 2:136, 3:100, 4:75, 5:76, 6:97 |
| Splits | train 361 / held_out_length 56 / held_out_op_combo 135 |
| `corpus_sha256` | `dedb5c1d56ac31b4e5aab56c9e48460a48db663eccc3f6ef48079b54d6bff3c0` |
| `splits_sha256` | `46d05a7cf01927f3a59029b1ee59fbf75e0a45cd35143daabadc6138ab82229b` |
| `schema_sha256` | `61d3ed74658a4dad5afa1344634faba389ec8a03db234706032c72bb28430c47` |

Delivered to Primus at the ignored path
`CCF_Sovereign/tmp/geometry_corpus_from_chronos2/seed_20260829/`
(`corpus.jsonl`, `manifest.json`, `splits.json`). The copied manifest has
`splits_path` repointed at the copied tree; the corpus and splits bytes are
untouched, so all three hashes verify as-is.

For scale: the recipe path produces **4 op-signatures from 200 briefs**. This
corpus has **103 from 552 programs**, and every one of the ten operations is
represented — `create_cube` 427, `extrude_region` 204, `union_shape` 200,
`subtract_shape` 192, `bevel_edges` 184, `taper_region` 179, `subdivide_face`
177, `pull_face` 157, `revolve_profile` 125, `shell_solid` 57.

## Corrections to numbers I published earlier

- **Throughput is 8.1 samples/min end to end, not 16.8.** The earlier figure came
  from the first ten samples before steady state and I stated it as a bound.
  Worse, a flat rate is the wrong model: typical samples take about six seconds
  and rare pathological ones take minutes, and because the reported rate is a
  cumulative average those outliers drag it down permanently. Size a corpus as
  *~6 s typical plus stalls*, not as a rate.
- **Execution failure is 8%** (48 of 600), measured, replacing the "~1 in 10"
  I estimated from two small runs.
- `loose_part_count` is **not** constant — `{0:3, 1:528, 2:19, 3:1, 4:1}`. My
  earlier concern was an artifact of a 12-sample view. The feature earns its
  place; the sampler does not need pushing.

## The stall pathology, characterised

Two independent stalls, same shape both times:

- cube → sphere DIFFERENCE → sphere UNION → **bevel-all-edges ×2**
- cube → sphere DIFFERENCE → box DIFFERENCE → **bevel-all-edges ×3**

Booleans followed by stacked bevel-all-edges. Each bevel multiplies edge count,
and applying it repeatedly to a dense boolean result explodes combinatorially.
One sample ran ten minutes against a six-second average and would have run
forever, because `Command::output()` waits indefinitely.

`emit_corpus` now enforces a 180 s per-sample budget and records timeouts as
their own manifest category with sample ids, rather than folding them into
ordinary failures. **Which regions of the operation space are intractable is real
information about the action space**, and a forward model's consumers should be
able to see it.

The 552-record corpus predates that fix, so its two stalls were killed by hand
under the same 180 s policy. Its manifest therefore has no
`execution_timed_out` field; those samples are inside the 48 failures. The next
corpus will separate them.

## Empty meshes — declared, not hidden

**3 records (0.5%) have `vert_count: 0`** and zero volume, area, and parts. A
subtract consumed the entire body.

That is arguably a legitimate outcome — "this program destroys the object" is a
true fact about the operation space. But it makes the minimum of every metric
zero, which will wreck naive normalisation. **Manus: decide explicitly whether to
train on these or filter them, and say which in the handoff.** Do not let them
pass unnoticed.

## Still not fixed

The small-body blank-render defect (A3). The sampler draws 60–300 mm bodies so
this corpus avoids it, but anything rendering a compact object still produces a
silently empty PNG scoring 0.0.
