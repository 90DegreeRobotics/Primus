# Plan — audit and land the dirty worktree on main

**Created:** 2026-08-26 05:46
**Status:** ACTIVE
**Operator instruction (2026-08-26):** "that work must be committed. audit and
finish the dirty worktree and push to main before begin anything."

## Goal

Land the uncommitted Sleep Architecture v0.1 body of work on `main` and push to
`origin`, without importing generated run output, and without claiming anything
the gate does not prove. This unblocks the Primus world-core track
(`C:\chronos2\plan_2026-08-26_0531_primus-world-core.md`), which must not begin
on top of an unpushed tree.

## Audit result

Branch `main`, **behind origin by 1** (`25a317a docs(sbir): ...`, touches only
`docs/sbir/` — no overlap with the dirty files, so it fast-forwards cleanly).

**12 modified, 29 untracked files. ~1 MB total. No checkpoints, no venv, no
corpus exports** — `.gitignore` already excludes `*.pt`, `checkpoints/`,
`**/venv/`, `**/training/training_data/*.jsonl`.

### What the work actually is

One coherent body: **Sleep Architecture v0.1** and its supporting organs.

| Area | Files | Nature |
|---|---|---|
| Sleep lifecycle | `src/lifecycles/sleep_architecture.py` (new, 26 KB), `circadian_controller.py`, `lifecycles/__init__.py` | NREM/REM/VALIDATE state machine |
| Memory organs | `src/memory/forever_law.py`, `canonical.py`, `saturation.py` (new), `steb.py`, `memory/__init__.py` | ledger, canonical beliefs, sleep pressure |
| Benchmark | `src/benchmarks/` (new) | continual-learning baseline vs lifecycle |
| Operator surface | `src/operator_ui.py`, `start_operator.bat`, `start.bat`, `src/main.py` | operator UI + wiring |
| Config | `src/core/config.py` | `SystemState` → NREM/REM/VALIDATE (legacy aliases kept), saturation + sleep constants |
| Substrate | `src/substrate/model.py` | **bug fix**, see below |
| Tests | `tests/` (new), `test_mvp.py` | fail-hard coverage of the above |
| Docs | `docs/SLEEP_ARCHITECTURE_V0_1.md`, `README.md`, `README_MVP.md`, `requirements.txt` | truth surfaces |

### The substrate fix is real and worth naming

`model.py` previously computed surprise as `-log P(token[t])` gathered from
`logits[t]` — scoring the token the model had **already been shown**, not its
next-token prediction. The fix aligns `logits[t] → token[t+1]`, uses
`log_softmax` instead of `log(softmax + eps)`, and left-pads position 0.

Surprise is the Free Energy signal that drives Hebbian plasticity, STEB episode
admission, and the saturation monitor. Before this fix that entire control loop
was keyed off a mis-aligned quantity.

### Judgment call — generated run output

`CCF_Sovereign/data/` (936 KB) is **per-run generated output**: three
`benchmarks/run_<epoch>/` trees plus `operator_bootcheck/`, each holding
`forever_law/events.jsonl`, `anchors.jsonl`, `canonical_beliefs.json`.

The repo's existing convention ignores generated run output
(`docs/defense_evidence/local_runs/`, `reports/*.json`, `out/`, `renders/`).
These are regenerable and follow that convention.

**Decision:** gitignore the per-run trees; **commit
`data/benchmarks/continual_learning_latest.json`** (a few KB), because that is
the cited benchmark result of record and it carries the Merkle root, so the
claim survives without the raw event logs.

**Nothing is deleted.** The files stay on disk. One line in `.gitignore` reverses
this if the operator wants the raw ledgers tracked.

## Files to edit

- `.gitignore` — add the per-run output exclusion, nothing else.
- No source files. This unit of work **lands** existing work; it does not add to it.

## Ordered steps

1. `git pull` — fast-forward `25a317a` (docs-only, no conflict).
2. Gate A: `python -m compileall -q` over every touched Python path.
3. Gate B: `python test_mvp.py` — fail-hard suite importing all new modules.
4. Add the `.gitignore` rule for `CCF_Sovereign/data/benchmarks/run_*/` and
   `CCF_Sovereign/data/operator_bootcheck/`.
5. Stage with **explicit pathspecs only**. `git add -A` is banned (§1.7).
6. Commit as `NeuroCognica <holtmichael1@gmail.com>`, Conventional Commit,
   subject ≤72 chars, body naming the substrate fix and the false-green caveat.
7. `git push origin main`.
8. Re-run `git status --short --branch`; confirm clean and `[up to date]`.

## Test gate

`python test_mvp.py` (system Python 3.12.10, torch 2.5.1+cu121, CUDA True — the
bundled `venv/` is a Linux-layout tree and is unusable on this host).

The suite asserts hard (`assertEqual`, `assertTrue`, shape and finiteness checks)
on a tiny config (`MODEL_DIM=32`, `NUM_LAYERS=1`); it does not catch-and-pass, so
it is not a false green. **What it proves:** the components import, wire, and
run. **What it does not prove:** any capability, persona quality, or benchmark
claim. It does not load the 1.78 GB checkpoint.

## Rollback path

Nothing is rewritten or deleted, so rollback is additive:

- Before push: `git reset --soft HEAD~1` restores the staged state. (No
  `reset --hard` — §1.3.)
- After push: revert with a new commit (`git revert <sha>`). Never force-push.
- The `.gitignore` change is one line; removing it restores tracking intent, and
  the run trees were never deleted from disk.

## Next-agent pickup notes

- One commit, not several: the config/memory/lifecycle changes are mutually
  dependent, and only the final state can be gated. Splitting them would commit
  states I could not certify — §1.5.
- The 22-entry dirty tree was **inherited work**, not authored in this session.
  It is attributed as such in the commit body.
- If `test_mvp.py` fails, STOP. Do not commit, do not "fix" inherited work to
  make a gate pass, mark this plan `INTERRUPTED` and surface it.
- After this lands, the world-core track resumes at Stage 0 (candidate
  isolation: `train.py:224` hardcodes the parent checkpoint path).
