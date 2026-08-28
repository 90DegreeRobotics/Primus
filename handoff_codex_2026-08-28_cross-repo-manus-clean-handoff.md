# Handoff - Cross-Repo Manus Clean Handoff

## Purpose

Michael flagged the coordination issue: Manus is parked in `C:\Primus`, while
the next witness plan had been written in `C:\chronos2`. This handoff makes the
two-repo boundary visible from Primus.

## What Changed

Added:

- `plan_2026-08-28_1736_cross-repo-manus-clean-handoff.md`
- `handoff_codex_2026-08-28_cross-repo-manus-clean-handoff.md`

The new plan instructs Manus to treat Primus and Chronos2 as separate but linked
handoff surfaces. Any repo touched during the next phase must end clean, with
all worked files audited, committed, and pushed to `origin/main`.

## Current Verified State Before Commit

Primus:

- `C:\Primus`
- `main`
- `HEAD == origin/main`
- Starting commit:
  `d8752ffc2524c31d99f7d75b5f0486504423db33`

Chronos2:

- `C:\chronos2`
- Latest clean-handoff plan:
  `plan_2026-08-28_1734_manus-native-witness-clean-handoff.md`
- Latest known clean-handoff commit:
  `d1081db00a986858d67b9ea90b96d3e4e581c091`

## Verification

Docs-only gate for this handoff:

- `git diff --check`
- explicit staging only
- `git diff --check --cached`
- push `origin main`
- verify clean `git status --short --branch`
- verify `HEAD == origin/main`

## Boundary

This is coordination documentation only. It does not run Primus tests, Chronos2
tests, BlenderMCP, a native render witness, robot/control actions, model
training, candidate promotion, or product release work.
