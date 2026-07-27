# Plan: establish git rules - 2026-07-27 09:46

## Status
COMPLETED

## Goal
Bring `C:\Primus` under Chronos-style repo governance without importing an unaudited working tree while another builder is active. The immediate deliverable is a git-ready rule surface, ignore policy, line-ending policy, and honest root status docs.

## Context
- Relevant areas: repo root, git metadata, governance docs.
- Files read: `C:\chronos\AGENTS.md`, `C:\chronos\.gitignore`, `C:\chronos\.gitattributes`, `C:\Primus` directory listing.
- Files that will be edited or created: `AGENTS.md`, `.agents/AGENTS.md`, `.gitignore`, `.gitattributes`, `README.md`, `STATUS.md`, this plan.
- Preconditions: `C:\Primus` is not currently a git repo; `https://github.com/90DegreeRobotics/Primus.git` has no visible refs from `git ls-remote`.

## Steps

### Step 1 - Seed governance files
- [x] Action: Add Chronos-style repo rules adapted to Primus.
- Files touched: `AGENTS.md`, `.agents/AGENTS.md`.
- Expected outcome: Future agents have a clear root law surface before touching code or docs.

### Step 2 - Add git hygiene files
- [x] Action: Add ignore and attribute policies for Python caches, virtualenvs, checkpoints, model weights, local corpus exports, and generated maps.
- Files touched: `.gitignore`, `.gitattributes`.
- Expected outcome: Git will not accidentally ingest multi-GB or private/generated artifacts.

### Step 3 - Add truth surfaces
- [x] Action: Add minimal root `README.md` and `STATUS.md` that describe the current repository state without claiming the system is complete.
- Files touched: `README.md`, `STATUS.md`.
- Expected outcome: The repo has a current truth anchor and explicit source-import boundary.

### Step 4 - Initialize git and remote
- [x] Action: Initialize git on `main`, set `origin` to `https://github.com/90DegreeRobotics/Primus.git`, stage only governance/truth files, commit, and push if the gate is clean.
- Files touched: git metadata only.
- Expected outcome: The remote contains the repo-law seed commit without capturing the active builder's work.

## Test gate
- `git status --short --branch`
- `git diff --check --cached`
- `git remote -v`
- `git ls-remote origin`

## Rollback
Do not delete files. If a governance rule needs correction, add a follow-up commit on `main` that edits the specific file and explains why.

## Next-agent pickup
If Status is INTERRUPTED, the next agent should:
1. Read this document top-to-bottom.
2. Run `git status --short --branch`.
3. Check each Step and resume at the first unchecked box.
4. Preserve the active builder's uncommitted work; do not stage broad pathsets.
