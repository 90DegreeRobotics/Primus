# Plan — all-lanes integration and governed Wave 3 50M candidate

**Created:** 2026-08-27 06:41 CDT
**Owner:** Manus, acting under Michael Holt’s explicit directive to finish integration and Wave 3
**Repository:** `C:\Primus`
**Branch:** `main`
**Status:** ACTIVE — baseline reconciliation and integration first

## Goal

First push each already-committed, verified Wave 1–2 unit currently ahead of `origin/main`, without staging foreign or unverified content. Then execute exactly one bounded 50M-class candidate experiment only after the repository is clean and synchronized, the candidate-isolation and comparison gates are armed, the GPU is observed idle and usable, and the parent/checkpoint invariants are recorded. Preserve success, failure, and non-claims in an evidence handoff. No automatic promotion is permitted.

## Governing sources read

- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `AGENTS.md`
- [x] `vision_deep_dive.md` as orientation only
- [x] `plan_2026-08-26_2144_multi-lane-build-charter.md`
- [x] `CCF_Sovereign/src/benchmarks/scaling_ladder.py`
- [x] `CCF_Sovereign/src/promotion/gate.py`
- [x] `CCF_Sovereign/training/candidate_run.py`
- [x] `handoff_claude_2026-08-26_lane-a-compiler-witness.md`
- [ ] Current all-lanes log, commit history, active process state, and candidate/checkpoint inventory
- [ ] Current comparison, shadow-evaluation, and training corpus contracts

`vision_deep_dive.md` does not support a provenance, priority, legal, or capability claim in this plan.

## Files expected to change

- [ ] This plan, then a final Manus handoff
- [ ] New isolated candidate directory only under `CCF_Sovereign/checkpoints/candidates/<unique-id>/`
- [ ] New ignored runtime logs only under `CCF_Sovereign/tmp/`
- [ ] New ignored run evidence only under `docs/defense_evidence/local_runs/<unique-id>/`

No parent or frozen checkpoint, training corpus, sibling repository, foreign builder file, or director truth surface is edited without a specific authorized unit and verification gate.

## Ordered work

- [ ] Identify every commit ahead of `origin/main`; verify its unit, author, paths, and tests from its handoff or direct gate before pushing.
- [ ] Push only existing verified commits, then verify `HEAD == origin/main`.
- [ ] Commit and push this plan as a standalone governed preparation unit so candidate creation sees a clean repository.
- [ ] Inspect all candidate, checkpoint, corpus, evaluation, and test inputs; select a unique unused candidate ID and explicit output paths.
- [ ] Validate 50M-only budget, operator authorization, and an armed comparison/promotion gate using the committed policy code.
- [ ] Verify GPU availability and exclusive idleness; record the specific GPU and do not launch if not usable.
- [ ] Record separate pre-launch parent/frozen/corpus/code/ledger hashes outside the repository and run the exact preflight tests.
- [ ] Launch one bounded 50M candidate run using the committed harness and isolated destination; capture stdout/stderr, PID, manifest transitions, checkpoint hashes, memory, throughput, and loss.
- [ ] Verify process exit, final candidate lifecycle state, checkpoint/manifest integrity, and parent/frozen hash equality.
- [ ] Run only available post-run comparison and promotion-policy gates. Preserve the default non-promotion decision unless all policy evidence and a separate explicit promotion instruction exist.
- [ ] Write a full handoff and truth-surface request. Commit/push only a verified, authorized documentation unit after a fresh shared-tree audit.

## Initial candidate budget

| Parameter | Required initial value |
|---|---:|
| Rung | `50m` only |
| Model shape | `D=640`, `L=20` |
| Sequence length | `256` |
| Batch size | `1` |
| Epochs | `1` |
| Diagnostic max steps | bounded and decided after corpus/block preflight; no unbounded run |
| Learning rate | `3e-4` |
| Vocabulary cap | `2048` |
| Promotion default | `false` |

This is a harness/memory/throughput/optimization diagnostic on the existing Council corpus, not a world-learning or generalization claim. The Stage 2 loader is not yet wired into `train.py` or the scaling ladder; no result from this run may be framed as evidence of learned world dynamics.

## Verification gate

```powershell
cd C:\Primus\CCF_Sovereign
python test_candidate_training.py
python test_promotion_gate.py
python test_budget_parity.py
python test_shadow_compare.py
python -m src.benchmarks.scaling_ladder --rungs 50m --vocab-size 2048 --describe
```

Before launch, `CandidateRun.create` must observe a clean repository. The promotion budget decision must allow the exact budget with `operator_authorized=True` and `gate_armed=True`. Parent and frozen parent SHA-256 values must equal `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` before launch, after candidate creation, after any checkpoint write, on failure, and after final evaluation.

## Rollback path

Never reset, clean, force-push, amend a pushed commit, delete a checkpoint, reuse a candidate ID, or copy a candidate over the parent. If the candidate fails, retain its isolated directory, manifest, logs, and checkpoint only as evidence. If integration or a documentation unit needs reversal after push, use a new explicit revert commit only after fresh authorization. Promotion remains a separate operator-run transaction and is out of scope for this plan.

## Next-agent pickup notes

At plan creation, `main` was three commits ahead of `origin/main`; no untracked path was listed by the abbreviated baseline output, but a full status and commit audit remains the first unfinished step. Active Claude processes exist and no process or source file owned by them will be altered. The earlier GPU probe reported an NVML initialization error, so CUDA must be independently verified through PyTorch and a minimal exact environment test before launch. If CUDA is unavailable or the run would write into an existing candidate/output destination, stop with a recorded failure rather than substitute CPU or overwrite an artifact.
