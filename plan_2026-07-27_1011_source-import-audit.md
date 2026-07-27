# Plan: source import audit - 2026-07-27 10:11

## Status
COMPLETE

## Goal
Audit the remaining untracked Primus surfaces and import only defensible source/docs to `main`, while keeping private corpus exports, virtual environments, checkpoints, generated maps, caches, and scratch out of git. The SBIR plan needs verified build/test/training evidence; this pass establishes what the local CCF/Primus prototype can honestly support.

## Context
- Relevant areas:
  - root research documents
  - `CCF_Sovereign`
  - repo truth surfaces
  - SBIR evidence trail
- Files read before this plan:
  - `AGENTS.md`
  - `README.md`
  - `STATUS.md`
  - `handoff_codex_2026-07-27_sbir-plan-completion.md`
  - `plan_2026-07-27_1002_complete-sbir-plan.md`
  - `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
  - `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`
- Files/directories expected to inspect:
  - `CCF_Sovereign\README.md`
  - `CCF_Sovereign\MVP_STATUS.md`
  - `CCF_Sovereign\requirements.txt`
  - `CCF_Sovereign\src\**\*.py`
  - `CCF_Sovereign\training\*.py`
  - `CCF_Sovereign\test_mvp.py`
  - `CCF_Sovereign\test_inference.py`
  - root research Markdown files
- Files likely to edit/create:
  - `STATUS.md`
  - `docs/sbir/README.md`
  - `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md`
  - this plan
  - final handoff

## Audit Checklist

- [x] Inventory untracked and ignored surfaces without bulk staging.
- [x] Classify root Markdown documents as importable, sensitive, generated, or out of scope.
- [x] Classify `CCF_Sovereign` source/docs/tests versus ignored local payloads.
- [x] Search first-party source/docs for wrapper residue, false-success language, stubs, mocks, placeholders, and generated artifacts.
- [x] Run Python compile gate for first-party CCF source/tests/training scripts.
- [x] Run `CCF_Sovereign\test_mvp.py` and record whether it proves real behavior or only a weak smoke test.
- [x] Run `CCF_Sovereign\test_inference.py` if checkpoint is present, and record output quality without overclaiming.
- [x] Create a repo audit artifact summarizing import decisions and evidence.
- [x] Update `STATUS.md` with the verified CCF/source-import state.
- [x] Update SBIR source register with the technical evidence pointer.
- [x] Write root handoff for this import/audit unit.
- [x] Stage only explicit import/audit paths.
- [x] Run `git diff --check --cached`.
- [x] Commit and push to `origin main`.
- [x] Verify `HEAD == origin/main`.

## Exclusion Rules

Do not stage:

- `.venv/`
- `CCF_Sovereign/venv/`
- `CCF_Sovereign/checkpoints/`
- `CCF_Sovereign/training/training_data/`
- `NeuroCognica_Primus/convos/`
- `primus-map.txt`
- `primus-tree.txt`
- `__pycache__/`
- logs, caches, generated maps, raw exports, or large model weights

## Test Gate
```pwsh
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\training CCF_Sovereign\train.py CCF_Sovereign\test_mvp.py CCF_Sovereign\test_inference.py
python CCF_Sovereign\test_mvp.py
python CCF_Sovereign\test_inference.py
git diff --check --cached
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

If `test_inference.py` cannot run or output is incoherent, record that plainly. A loaded checkpoint is not proof of learned agency by itself.

## Rollback
Do not delete. If an imported path proves wrong, add a follow-up commit that moves it to an archive/exclusion path or corrects the status language with explicit operator approval where needed.

## Next-Agent Pickup
If Status is `INTERRUPTED`, resume at the first unchecked box. Do not stage broad pathsets. Preserve unrelated untracked local surfaces.
