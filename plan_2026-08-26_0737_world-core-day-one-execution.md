# Plan: Primus world-core day-one execution

**Status:** IN PROGRESS
**Branch:** `main`
**Authority:** `handoff_manus_2026-08-26_world-core-day-one.md`, `AGENTS.md`, and the Charter of Cognitive Sovereignty.

## Guardrails

- [x] Verify live parent checkpoint SHA-256 equals `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.
- [x] Verify frozen archive exists and has the same hash.
- [x] Verify starting tree is clean and `main == origin/main`.
- [ ] Never run training until Workstream A is committed and pushed.
- [ ] Never overwrite or promote the parent as a training side effect.
- [ ] Use explicit pathspec staging only.

## Workstream A — candidate isolation

- [x] Add isolated per-candidate output paths.
- [x] Refuse to start when the live parent hash differs from the frozen expected hash.
- [x] Emit a manifest containing config, data hash, seed, code commit, metrics, and output path.
- [x] Make promotion a separate explicit atomic command.
- [x] Add a regression test proving training cannot write the parent path.
- [x] Run compile gate, `python test_mvp.py`, and the new regression test.
- [ ] Commit and push before any training.

## Workstream D — scaling ladder

- [ ] Add or verify 5M/15M/50M/150M configurations using a small vocabulary and tied head.
- [ ] Record tokens/sec, peak VRAM, OOM status, loss only as a sanity measurement, exact config, seed, and commit.
- [ ] Launch only after Workstream A is on `origin/main`.
- [ ] Preserve results under ignored local-run paths and publish a non-confidential summary.

## Workstream B — typed world schema

- [ ] Define domain-general world entities, relations, observations, actions, constraints, and uncertainty.
- [ ] Ground it in ChronoSophia S3V and the existing compiler.
- [ ] Implement lossless schema → S3V → schema round trip.
- [ ] Add category- and operation-family holdout fields to prevent generator inversion.
- [ ] Run focused tests and documentation gates.

## Workstream C — chunked selective scan

- [ ] Replace the full float32 Hillis–Steele materialization with a chunked scan.
- [ ] Preserve recurrent equivalence and hidden-state semantics.
- [ ] Add forward differential, backward gradient, and boundary-state tests.
- [ ] Benchmark memory and throughput against the existing scan.
- [ ] Commit only if numerical and gradient gates pass.

## Final gates and handoff

- [ ] Run all touched-surface tests and repository diff checks.
- [ ] Update truth/status documents in the same commit as capability changes.
- [ ] Push verified commits to `origin/main`.
- [ ] Report what ran, real measurements, failures, remaining blockers, and exact git state.
