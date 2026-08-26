# Plan: Primus world-core day-one execution

**Status:** IN PROGRESS
**Branch:** `main`
**Authority:** `handoff_manus_2026-08-26_world-core-day-one.md`, `AGENTS.md`, and the Charter of Cognitive Sovereignty.

## Guardrails

- [x] Verify live parent checkpoint SHA-256 equals `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.
- [x] Verify frozen archive exists and has the same hash.
- [x] Verify starting tree is clean and `main == origin/main`.
- [x] Never run training until Workstream A is committed and pushed.
- [x] Never overwrite or promote the parent as a training side effect.
- [x] Use explicit pathspec staging only.

## Workstream A — candidate isolation

- [x] Add isolated per-candidate output paths.
- [x] Refuse to start when the live parent hash differs from the frozen expected hash.
- [x] Emit a manifest containing config, data hash, seed, code commit, metrics, and output path.
- [x] Make promotion a separate explicit atomic command.
- [x] Add a regression test proving training cannot write the parent path.
- [x] Run compile gate, `python test_mvp.py`, and the new regression test.
- [x] Commit and push before any training.

## Workstream D — scaling ladder

- [x] Add or verify 5M/15M/50M/150M configurations using a small vocabulary and tied head.
- [x] Record tokens/sec, peak VRAM, OOM status, loss only as a sanity measurement, exact config, seed, and commit.
- [x] Launch only after Workstream A is on `origin/main`.
- [x] Preserve results under ignored local-run paths; publish the non-confidential summary in the final evidence commit.

## Workstream B — typed world schema

- [x] Define domain-general world entities, relations, observations, actions, constraints, and uncertainty.
- [x] Ground it in ChronoSophia S3V and the existing compiler.
- [x] Implement lossless schema → S3V → schema round trip.
- [x] Add category- and operation-family holdout fields to prevent generator inversion.
- [x] Run focused tests and documentation gates.

## Workstream C — chunked selective scan

- [x] Replace the full float32 Hillis–Steele materialization with a chunked scan.
- [x] Preserve recurrent equivalence and hidden-state semantics.
- [x] Add forward differential, backward gradient, and boundary-state tests.
- [x] Benchmark memory and throughput against the existing scan.
- [ ] Commit only if numerical and gradient gates pass.

## Measured day-one results

- 5.34M, 16.21M, and 53.93M completed 3,940-step passes on the RTX 3060 at 1,194.65, 623.40, and 308.84 tokens/s with 2.28, 4.09, and 8.73 GB peak reserved VRAM.
- 155.35M completed one step and then failed honestly with CUDA OOM; no checkpoint was promoted.
- The chunked scan passed seven differential/gradient tests. At batch 4, sequence 2,048, width 1,024, state 16, forward/backward peak reserved memory fell from 16.23 GB reported allocator demand to 8.50 GB, while throughput rose from 1,121.88 to 9,507.04 tokens/s.
- The typed world schema passed eight focused tests and a bridge fixture was accepted by ChronoSophia's real Rust S3V v1 parser.

## Final gates and handoff

- [ ] Run all touched-surface tests and repository diff checks.
- [ ] Update truth/status documents in the same commit as capability changes.
- [ ] Push verified commits to `origin/main`.
- [ ] Report what ran, real measurements, failures, remaining blockers, and exact git state.
