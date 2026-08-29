# Task — Forward Model Sprint

**Date:** 2026-08-29
**Repos:** tandem. Identical copy in `C:\Primus`.
**Supersedes ceremony, not law.** Rules 8/9 (chronos2) and 9/10 (Primus) still
bind. This replaces the Round 2 lane document as the active work order.

## Why this is short

Three guards, two lane plans, and law in both repos exist. Zero lines of learning
code exist. The measurement scaffolding has outrun the thing being measured. This
order is one page because the next thing needed is building, not planning.

## The goal

**Train the forward model: program → mesh metrics.**

This is the piece with the least risk in the whole programme. The executor is
deterministic, so every sample is a perfect input-output pair with no label noise
and no ambiguity, and we can generate as many as we want. If this does not learn,
something is broken rather than hard.

It is also the first honest learning result on the geometry side, and it makes
the novelty number climb for a real reason instead of sitting at 0.035 while more
documents get written about it.

---

## Claude — corpus production (chronos2)

Building now, in this order:

1. `mesh_metrics.rs` — make the executed mesh report real geometry: vert/edge/
   face/tri counts, loose parts, bbox, volume, surface area, closedness.
2. Metric separation check — the eight Round 1 probes must be nearest to
   themselves. Specifically `lone_cube`, `deep_bevelled_cube`, `pierced_cube`,
   `hollow_shell`, which `silhouette_v0.1` could not tell apart at all.
3. `program_sampler.rs` — sample the operation space. Seeded, deterministic,
   never seeded from a list of objects.
4. Corpus emission — `geometry_program_corpus_v2` JSONL plus a hash-pinned
   manifest, with measured throughput.

Blender and port 9876 remain exclusive to this lane.

---

## Manus — the trainer (Primus)

**Not blocked. Start now.**

`CCF_Sovereign/train_geometry_phase0.py`: train a small model to predict the
`mesh_metrics` vector from `program` + `program_structure`.

- Build and test it against the v2 fixture so it is ready to run the hour the
  real corpus lands. Extend the fixture to v2 yourself.
- Same lifecycle discipline as the BridgeData work: frozen hash-pinned inputs,
  isolated candidate directory, atomic manifest, no promotion operation,
  rejection by default.
- Report per-metric error, split-separated, against the three baselines you
  already declared. A number without its baseline and its structural holdout is
  not a result.
- **A fixture run is never a result.** Training on the fixture proves the harness
  executes. That is all it proves, and the handoff must say so in those words.
- A test must fail if `view_score` is ever read as a target or a filter. It is
  metadata; its measured separation is −0.1721.

Owned: `CCF_Sovereign/src/geometry_corpus/**`, `train_geometry_phase0.py`,
`test_train_geometry_phase0.py`, `test_geometry_corpus*.py`,
`CCF_Sovereign/tmp/**`, `handoff_manus_2026-08-29_*`.

---

## Codex — verification (both repos)

**Not blocked. Start now.**

1. `CCF_Sovereign/audit_geometry_corpus.py` — given a corpus and manifest,
   verify hashes, schema conformance, forbidden keys at any depth, split
   disjointness, no duplicate `sample_id`, and that `program_structure` is
   actually derivable from `program` rather than hand-written. Build it against
   the fixture; run it on the real corpus when it lands.
2. Extend both guards to v2 records, and watch `program_sampler.rs` and
   `mesh_metrics.rs` for object nouns.
3. **Independently re-derive Claude's metric separation number.** Do not read the
   harness and agree with it — compute it separately from the emitted metrics. If
   the two answers disagree, that disagreement is the finding and the sprint
   parks until Michael arbitrates. One number gates whether any of this is worth
   training on.

Owned: `crates/chronos_geometry_plan/tests/no_recipe_guard.rs`,
`crates/chronos_geometry_plan/tests/novelty_ratchet.rs`,
`crates/chronos_vision/tests/metric_separation_audit.rs`,
`C:\Primus\CCF_Sovereign\test_no_recipe_guard.py`,
`C:\Primus\CCF_Sovereign\audit_geometry_corpus.py`,
`handoff_codex_2026-08-29_*`.

Do not lower a ratchet floor. Raising one when the system improves is the intent.

---

## Standing rules, unchanged

`pull --rebase` before every push. Explicit pathspecs, never `git add -A`. Park
rather than resolve a conflict in a file you do not own. Both repos end clean
with `HEAD == origin/main`. If you did not run it, you do not get to say it
works. If you are about to add a keyword, a noun list, or a per-shape default:
stop.
