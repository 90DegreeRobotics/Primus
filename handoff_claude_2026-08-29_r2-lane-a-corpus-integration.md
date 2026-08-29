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
