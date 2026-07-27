# Handoff: Codex - 2026-07-27 - git governance seed

## What Changed

- Initialized `C:\Primus` as a git repository on `main`.
- Set `origin` to `https://github.com/90DegreeRobotics/Primus.git`.
- Added Chronos-style governance and truth surfaces:
  - `AGENTS.md`
  - `.agents/AGENTS.md`
  - `.gitignore`
  - `.gitattributes`
  - `README.md`
  - `STATUS.md`
  - `plan_2026-07-27_0946_establish-git-rules.md`

## Commands Run

- `git ls-remote https://github.com/90DegreeRobotics/Primus.git`
  - Returned no refs before setup, so the remote appeared empty.
- `git init -b main`
  - Initialized the repo at `C:\Primus\.git`.
- `git remote add origin https://github.com/90DegreeRobotics/Primus.git`
  - Wired the GitHub remote.
- `git diff --check --cached`
  - Passed with no output.
- `git commit -m "chore(repo): establish Primus git governance"`
  - Created root commit `7eb51c0a2a6d864c22c97be1fb72581207e21af5`.
- `git push -u origin main`
  - Pushed `main` and set upstream tracking.
- `git rev-parse HEAD` and `git rev-parse origin/main`
  - Both returned `7eb51c0a2a6d864c22c97be1fb72581207e21af5`.

## What Was Not Run

- No source/runtime tests were run for `CCF_Sovereign` during this governance seed.
- No training or inference claims were certified.
- No source import was performed.

## Dirty Or Untracked Boundary

The following local surfaces remain untracked by design:

- `CCF_Sovereign/`
- `Fascia and Mycelia Network Comparison.md`
- `Organic Wetware AI Architecture.md`
- `SBIR_plan.md`
- `Sovereign Textual Mind Paradigm.md`
- `council_ideas.md`

`SBIR_plan.md` appeared after git initialization and was not created by this
handoff. Treat it as builder/operator work until proven otherwise.

Ignored local surfaces include virtual environments, checkpoints/model weights,
raw conversation exports, generated root maps, logs, and caches.

## Next Step

When the active builder is done, run a path-by-path import audit. Do not
`git add -A`. Stage only the verified source/docs that should become
git-canonical, and keep corpus exports, checkpoints, venvs, logs, generated maps,
and scratch output out of history.
