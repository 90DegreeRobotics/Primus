# Plan - Codex Primus Verification

**Date:** 2026-08-29 1006 CDT
**Status:** COMPLETE
**Lane:** Codex / Lane C, Primus-owned files only

## Goal

Complete the Primus-side portion of the current Codex verification work order:
add the missing geometry corpus audit tool and extend the existing no-recipe
guard so v2 corpus records are covered.

## Files Read

- `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `plan_2026-08-29_0838_round2-multi-lane-phase0-corpus.md`
- `task_2026-08-29_forward-model-sprint.md`
- `handoff_codex_2026-08-29_lane-c-enforcement-and-debt.md`
- `CCF_Sovereign\test_no_recipe_guard.py`
- `CCF_Sovereign\src\geometry_corpus\intake.py`
- `CCF_Sovereign\test_geometry_corpus.py`

## Files To Edit

- `CCF_Sovereign\audit_geometry_corpus.py`
- `CCF_Sovereign\test_no_recipe_guard.py`
- `handoff_codex_2026-08-29_r2-lane-c-primus-verification.md`

## Ordered Steps

1. Add `audit_geometry_corpus.py` with fail-closed corpus, manifest, split, hash,
   schema, forbidden-key, duplicate, and derived-structure checks.
2. Extend `test_no_recipe_guard.py` to exercise v2 audit acceptance and reject
   hand-written `program_structure`.
3. Run focused Python gates.
4. Pull with rebase, stage explicit pathspecs, commit, push, and verify
   `HEAD == origin/main`.

## Test Gate

```pwsh
cd C:\Primus\CCF_Sovereign
python test_no_recipe_guard.py
python -m compileall -q audit_geometry_corpus.py test_no_recipe_guard.py
```

## Rollback Path

If a focused gate fails and cannot be fixed inside owned files, stop, write a
blocked handoff, and leave unowned files untouched.

## Next-Agent Pickup

This audit is a learner-side corpus verifier. It does not replace the Chronos2
output-space novelty ratchet and does not prove a learned geometry model.

## Completion Notes

Focused Primus gates passed on 2026-08-29:

```pwsh
python test_no_recipe_guard.py
python -m compileall -q audit_geometry_corpus.py test_no_recipe_guard.py
python test_geometry_corpus.py
```

No real Lane A corpus was present in Primus during this pass, so the audit was
proved against a v2 fixture only.
