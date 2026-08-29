# Handoff - Codex R2 Lane C Primus Verification

**Date:** 2026-08-29
**Repo:** `C:\Primus`
**Branch:** `main`
**Start commit:** `31ab5e74f7f54d00402954e79a1f92ed0ca106b8`
**Lane:** Codex / verification

## What Changed

- Added `CCF_Sovereign\audit_geometry_corpus.py`, a fail-closed audit tool for
  geometry program corpus artifacts.
- Extended `CCF_Sovereign\test_no_recipe_guard.py` with v2 fixture coverage for
  the audit path.
- Recorded this work plan in
  `plan_2026-08-29_1006_codex-primus-verification.md`.

The audit verifies:

- manifest-bound corpus SHA-256
- schema-version SHA-256
- split-definition SHA-256 when a split file is supplied
- `geometry_program_corpus_v1` and `geometry_program_corpus_v2` record shape
- forbidden key absence at any depth
- duplicate `sample_id` rejection
- `sample_id` derivation from canonical `program` JSON
- `program_structure` derivation from `program`, not hand-written metadata
- structural split disjointness for the declared split-definition contract

## Files Touched

- `CCF_Sovereign\audit_geometry_corpus.py`
- `CCF_Sovereign\test_no_recipe_guard.py`
- `plan_2026-08-29_1006_codex-primus-verification.md`
- `handoff_codex_2026-08-29_r2-lane-c-primus-verification.md`

## Commands Run

```pwsh
git status --short --branch
git diff --stat
git ls-files --deleted
git log -8 --oneline --decorate
python test_no_recipe_guard.py
python -m compileall -q audit_geometry_corpus.py test_no_recipe_guard.py
python test_geometry_corpus.py
```

Real result:

- `python test_no_recipe_guard.py`: 5 tests passed.
- `python -m compileall -q audit_geometry_corpus.py test_no_recipe_guard.py`:
  exit 0.
- `python test_geometry_corpus.py`: 6 tests passed.

## What Was Not Run

- No real corpus audit was run because no Lane A real
  `geometry_program_corpus_v2` corpus and manifest were present in Primus.
- No Blender, BlenderMCP, renderer, sampler, or Chronos2 metric-separation
  harness was invoked.
- No model training or promotion was run.

## Boundaries

This is fixture-backed audit tooling, not evidence of a learned geometry model
and not a replacement for the Chronos2 output-space novelty ratchet. The source
guard remains a secondary detector; output-space saturation is still the primary
anti-recipe signal.

## Dirty Or Untracked State

At handoff creation time, only this lane's owned files were dirty or untracked.
Final repo cleanliness and push parity are to be verified after commit/push.

## Next Step

When Lane A emits a real corpus and manifest, run:

```pwsh
cd C:\Primus\CCF_Sovereign
python audit_geometry_corpus.py --corpus <corpus.jsonl> --manifest <manifest.json> --splits <splits.json>
```

If the real emitted manifest includes a split path, `--splits` may be omitted.
