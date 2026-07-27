# Primus

Primus is the local-first NeuroCognica textual-mind workspace. This repository
is being brought under git governance from an existing local tree rather than a
fresh scaffold.

## Current Truth

- Canonical branch: `main`.
- Remote: `https://github.com/90DegreeRobotics/Primus.git`.
- Repo-law surface: `AGENTS.md`.
- Current status ledger: `STATUS.md`.

The local tree contains research documents, `CCF_Sovereign`, and
`NeuroCognica_Primus` material. Those surfaces must be imported intentionally
after audit. Do not bulk-stage the whole tree.

## Operator Rules

Read `AGENTS.md` before changing anything. The short version:

- work on `main`
- no worktrees
- no force-push or history rewrite
- no deletion without explicit per-item approval
- no stubs or random-output demos reported as real
- stage by explicit pathspec
- run the gate before claiming done
- push verified units to `origin/main`

## Verification

For this initial governance seed, the relevant gate is:

```pwsh
git diff --check --cached
git status --short --branch
```

Future Python/code work must run the relevant command named in `AGENTS.md`.
