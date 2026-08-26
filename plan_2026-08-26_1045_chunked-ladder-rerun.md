# Plan — re-run the scaling ladder on the chunked scan

**Created:** 2026-08-26 10:45
**Status:** COMPLETE (stopped deliberately at step 85/300, 2026-08-26 17:45).

**Answered, but narrower than first reported:** 155,347,584 params ran 6.39
hours at ~12.08 GB at the exact config that OOMed after one step under the old
full-state scan. The memory ceiling is gone. **Memory-viable, not
training-viable** - see the stability finding below.

**Measured via py-spy on the live process (operator-approved install):**
completed_steps 85 of 300 - 0.95 tok/s - 271 s per step - 22.6 h projected,
16.2 h remaining when stopped.

**THE 150M CONFIGURATION DOES NOT TRAIN.** Mean loss 112.93 against a random
baseline of ln(2048) = 7.62 - about 15x worse than guessing, flat across steps
2-85 (~105 average). Compare 5m 7.58, 15m 6.92, 50m 6.84, all at or below
random. NOT the chunked scan: day one 150m under the OLD scan logged 783.02 on
its single step. Both implementations show it, so this is an
optimization/initialization defect at depth 30 - lr 3e-4 with no warmup through
30 layers is the leading suspect.

**Consequence:** fixing dispatch overhead alone will not make 155M usable, and
53.93M is now BETTER supported as the starting size - it is the largest rung
that trained stably.

**Answered:** 155,347,584 params have trained 4.5+ hours at ~12.08 GB at the
exact configuration that OOMed after one step under the old full-state scan.
The 12 GB memory ceiling is gone.

**Still executing:** the run has no progress signal (prints only at step 1 and
every 50 steps, ~210 bytes total, far below Python block-buffer size, so the
log stays empty until exit). Average is under 4.7 tok/s. Remaining time cannot
be estimated from available signals; py-spy is not installed and installing it
needs per-act operator approval.

**Diagnosed:** dispatch-bound on a single CPU core. GPU at 100% utilization but
53 W of 170 W and 44 C. The card is starved, not saturated - an efficiency
problem in software, not a hardware limit.

**Discard:** the earlier ladder-chunked-20260826b run (batch 2, seq 512) was
confounded - it changed scan AND shape together - and was force-killed. Its 5m
figure (869.5 tok/s / 5.93 GB) and stale 15m manifest are not evidence.

**Next agent:** if this was killed rather than completed, the manifest will sit
stale at status=training; a SIGKILL cannot run the OOM reconciliation. Record
the bounded result rather than leaving the stale status to be misread.
**Operator instruction:** "Proceed with the next run."
**Authority:** `handoff_manus_2026-08-26_world-core-day-one.md`, `AGENTS.md`,
and the Charter. Continues
`C:\chronos2\plan_2026-08-26_0531_primus-world-core.md`.

## Goal

Produce the **one measurement day one did not**: real end-to-end model
throughput on the chunked selective scan, and a direct answer to whether the
155.35M rung now fits inside 12 GB.

Two open questions:

1. **Does 150m still OOM?** It died at batch 1 / seq 256 under the old
   full-state scan. The chunked path reduced stress-shape reserved demand
   16.23 GB → 8.50 GB. If 150m now completes, the ceiling is gone in practice,
   not just in a micro-benchmark.
2. **What is real model throughput?** The 9,507 tok/s figure is the *scan
   operation*, not a model. Across ~11–30 layers plus the rest of each block,
   end-to-end will be far lower. The plan's schedule still rests on an estimate
   that has already been proven wrong once.

## Why this is not a capability run

Same corpus (845 turns, 1,012,661 tokens), same non-claim: at 0.019 tokens per
parameter for the 50m rung, nothing here supports a capability, quality, or
scaling-law claim. **This measures the harness and the hardware.** The loss
column must not be read as a knee — the apparent 15m→50m flattening on day one
is data starvation, not a scaling law.

## Configuration and why

| Setting | Value | Reason |
|---|---|---|
| `--batch-size` | 2 | Day one ran batch 1, which starves the GPU. Modest step up; the card must also hold 150m. |
| `--sequence-length` | 512 | 1,024 tokens/step vs day one's 256 — 4x better utilisation without a memory cliff. |
| `--max-steps` | 300 | ~307k tokens/rung. Enough for stable tok/s; avoids a multi-hour epoch. |
| `--rungs` | 5m,15m,50m,150m | All four, so the comparison against day one is like-for-like on everything but shape and scan. |
| `--run-prefix` | `ladder-chunked-20260826` | Unique; `mkdir(exist_ok=False)` rejects collisions with day-one dirs. |

Vocab, tied head, equal-width backbone and seed are left at their committed
defaults so only shape and scan differ.

## Safety

- Candidate isolation (`2113851`) is on `origin/main`; training cannot write the
  parent. Verified again immediately before launch.
- Parent SHA-256 must remain
  `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`
  before and after. Frozen archive at `checkpoints/frozen/` is never written.
- **No promotion.** `promote_candidate.py` is not invoked by this plan.
- Candidate output lands under ignored per-run paths; nothing large is committed.
- If Manus resumes work mid-run, stop and surface rather than racing it — two
  agents driving one GPU is how results get corrupted.

## Ordered steps

1. Confirm clean tree, `main == origin/main`, parent hash matches.
2. `--describe` on CPU: confirm parameter counts before spending GPU time.
3. Launch the ladder in background with the configuration above.
4. Watch peak VRAM per rung; specifically whether 150m completes or OOMs.
5. Re-verify parent hash and tree state after.
6. Report measured tok/s per rung, peak VRAM, and the 150m outcome, **against
   the day-one numbers**.
7. Do not commit results unless the operator asks — raw artifacts are ignored
   paths by design, and the day-one evidence doc is already the record.

## Test gate

Not a code change, so no code gate applies. The integrity gate is the parent
hash before and after, plus a clean tree. If the harness itself is touched for
any reason, the five suites must be re-run first.

## Rollback path

Nothing is rewritten or deleted. Candidate output is additive under ignored
paths. Aborting is safe at any point: kill the process; the reconciliation Manus
added marks an interrupted run `failed` rather than leaving a stale
`training` status.

## Next-agent pickup notes

- Day one landed at `b2b138f`; implementation commit `e2378fe`.
- Day-one ladder: 5m 1,194.65 tok/s / 2.28 GB · 15m 623.40 / 4.09 · 50m 308.84 /
  8.73 · **150m CUDA OOM** — all at batch 1, seq 256, old full-state scan.
- The purpose here is a like-for-like delta, so do not change vocab, seed, tying,
  or width. Only shape and scan differ.
- If 150m completes, the next real question is the Stage 2 data generator, not a
  bigger model. Size should be re-derived from a ladder on **grounded
  trajectories**, never from this text corpus.
