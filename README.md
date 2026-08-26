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

## Verified CCF world-core substrate

`CCF_Sovereign` now has fail-closed candidate isolation, a domain-general typed
world schema, a lossless S3V v1 bridge, and a memory-bounded chunked selective
scan. These are **substrate and evidence capabilities**, not proof of a learned
world-builder. The August 26 RTX 3060 ladder completed full 5.34M, 16.21M, and
53.93M parameter passes; the 155.35M rung completed one step and then recorded a
CUDA out-of-memory limit. No candidate was promoted and the frozen parent
remained protected.

The schema contract is documented in
`CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`. Non-confidential measurements are
recorded in the status and CCF audit ledgers; raw run manifests, checkpoints,
and local benchmark JSON remain ignored.

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
For the current world-core surfaces, the focused gates are:

```pwsh
cd CCF_Sovereign
python test_world_schema.py
python test_chunked_scan.py
python test_candidate_training.py
python test_scaling_ladder.py
python test_mvp.py
```
