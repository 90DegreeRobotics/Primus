# Plan: Candidate Generation Audit - 2026-07-27 22:11

## Status
COMPLETE - CANDIDATE 001 BLOCKED / NOT CREATED

## Goal
Audit the CCF training/candidate-generation path and create Candidate 001 only
if the path can run without mutating the frozen parent checkpoint or staging
private/raw artifacts.

## Files Read

- [x] `AGENTS.md`
- [x] `README.md`
- [x] `STATUS.md`
- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`
- [x] `plan_2026-07-27_1429_live-parent-baseline.md`
- [x] `handoff_codex_2026-07-27_live-parent-baseline.md`
- [x] `CCF_Sovereign\README.md`
- [x] `CCF_Sovereign\MVP_STATUS.md`
- [x] `CCF_Sovereign\requirements.txt`
- [x] `CCF_Sovereign\train.py`
- [x] `CCF_Sovereign\training\analyze_data.py`
- [x] `CCF_Sovereign\training\parse_council_corpus.py`
- [x] `CCF_Sovereign\training\execution_trace_logger.py`
- [x] `CCF_Sovereign\src\evaluation\live_parent_baseline.py`
- [x] `CCF_Sovereign\src\evaluation\shadow_compare.py`
- [x] `.gitignore`
- [x] local ignored training/checkpoint paths

## Files To Edit/Create

Candidate code only if the audit proves a safe path; docs/handoff if the audit
blocks Candidate 001:

- [ ] candidate-generation code or wrapper if needed - not edited this pass
  because the audited path was no-go
- [ ] candidate-generation tests if code changes are needed - not edited this
  pass because no Python candidate fix was attempted
- [x] non-confidential candidate audit/evidence summary
- [x] `STATUS.md`
- [x] `docs\ccf\CCF_SOURCE_AUDIT_2026-07-27.md`
- [x] `docs\defense_evidence\README.md`
- [x] `docs\sbir\CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- [x] `SBIR_plan.md`
- [x] `handoff_codex_2026-07-27_candidate-generation-audit.md`
- [x] this plan

## Checklist

- [x] Recheck dirty tree and repo rules.
- [x] Load Charter, Annex, CCF truth surfaces, and current baseline/comparison
  context.
- [x] Inspect current training entry points and output paths.
- [x] Inspect local training data presence, size, and privacy boundary without
  staging raw data.
- [x] Decide whether existing training can generate Candidate 001 without
  mutating the parent checkpoint.
- [x] If unsafe or unreal, record blocker and do not fake Candidate 001.
- [ ] If safe, run isolated Candidate 001 generation to an ignored local path -
  not safe this pass.
- [ ] Hash Candidate 001 and run candidate baseline/comparison if generated -
  no candidate exists.
- [x] Update docs with exact result or exact blocker.
- [x] Write fresh handoff.
- [x] Stage explicit paths only.
- [x] Run relevant compile/test/check gates.
- [x] Run `git diff --check --cached`.
- [ ] Commit and push to `origin main`.
- [ ] Verify `HEAD == origin/main`.

## Test Gate

Minimum if docs-only blocker:

```pwsh
git diff --check --cached
git status --short --branch --ignored
git rev-parse HEAD
git rev-parse origin/main
```

If Python code changes:

```pwsh
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\train.py CCF_Sovereign\training CCF_Sovereign\test_mvp.py CCF_Sovereign\test_shadow_manifest.py CCF_Sovereign\test_shadow_baseline.py CCF_Sovereign\test_live_parent_baseline.py CCF_Sovereign\test_shadow_compare.py
python test_shadow_manifest.py
python test_shadow_baseline.py
python test_live_parent_baseline.py
python test_shadow_compare.py
python test_mvp.py
git diff --check --cached
```

If a real candidate is generated, also run the candidate baseline and comparison
commands and record exact hashes.

## Rollback
Do not delete local artifacts. If candidate generation starts to target the
parent checkpoint, stop before running it. If a run fails after writing an
ignored artifact, preserve the failure summary and hash any produced files.

## Next-Agent Pickup
If interrupted, resume at the first unchecked item. Do not claim Candidate 001
exists unless a real artifact is present, hashed, and isolated from the parent.
