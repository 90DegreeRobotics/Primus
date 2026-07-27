# Handoff: Shadow Compare Gate

**Date:** 2026-07-27
**Agent:** Codex
**Branch:** `main`
**Scope:** Parent/candidate comparison referee for manifest-bound shadow
baseline result artifacts.

## What Changed

- Added `CCF_Sovereign/src/evaluation/shadow_compare.py`.
- Exported comparison helpers from `CCF_Sovereign/src/evaluation/__init__.py`.
- Added `CCF_Sovereign/test_shadow_compare.py`.
- Added
  `docs/defense_evidence/benchmarks/shadow_compare_gate_summary.md`.
- Updated `docs/defense_evidence/README.md`,
  `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`,
  `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`, `SBIR_plan.md`,
  `STATUS.md`, and `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md`.
- Created and maintained
  `plan_2026-07-27_1824_shadow-compare-gate.md`.

## Evidence Summary

- The comparison gate consumes parent result JSON and candidate result JSON.
- It rejects manifest SHA-256 mismatch, cycle ID mismatch, and case-set
  mismatch before judging a candidate.
- It computes pass delta, recovered failures, protected-task regressions, new
  errors, per-case latency deltas, and mean case-latency delta.
- It emits one of:
  - `CANDIDATE_IMPROVES`
  - `NO_PROMOTION_NO_IMPROVEMENT`
  - `REJECT_PROTECTED_REGRESSION`
  - `REJECT_NEW_ERRORS`
- It writes comparison JSON without raw response text. Response hashes remain
  allowed.

## Commands Run

- `git status --short --branch`; branch was `main...origin/main`.
- `git diff --stat`; no tracked diff at start.
- `git ls-files --deleted`; no deleted tracked files.
- `Select-String` memory lookup for adjacent NeuroCognica anti-stub doctrine.
- `Get-Content` for repo law, truth surfaces, Charter, Annex, latest
  plan/handoff, CCF docs/source/tests, and SBIR/evidence docs.
- First `python test_shadow_compare.py`; failed because the test incorrectly
  rejected the word `response` in `response_sha256` key names. The assertion was
  corrected to reject raw fixture response text instead.
- `python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_mvp.py CCF_Sovereign\test_shadow_manifest.py CCF_Sovereign\test_shadow_baseline.py CCF_Sovereign\test_live_parent_baseline.py CCF_Sovereign\test_shadow_compare.py`;
  exit 0.
- `python test_shadow_manifest.py`; 4 tests, exit 0.
- `python test_shadow_baseline.py`; 4 tests, exit 0.
- `python test_live_parent_baseline.py`; 4 tests, exit 0.
- `python test_shadow_compare.py`; 6 tests, exit 0.
- `python test_mvp.py`; 6 tests, exit 0.
- `rg` stale-language and non-ASCII checks against the new comparison surfaces.
- `git diff --check --cached`; exit 0.
- `git commit --author "NeuroCognica <holtmichael1@gmail.com>" -m "feat(ccf): add shadow comparison gate"`;
  created `bcc49aa6c58015127b15ef5059e774c1df175614`.
- `git push origin main`; pushed `69c83b3..bcc49aa`.
- `git rev-parse HEAD`; `bcc49aa6c58015127b15ef5059e774c1df175614`.
- `git rev-parse origin/main`; `bcc49aa6c58015127b15ef5059e774c1df175614`.

## What Was Not Run

- No live checkpoint run.
- No training run.
- No candidate generation.
- No live parent/candidate benchmark comparison.
- No raw response publication.
- No Forever Law event-chain sealing.
- No atomic promotion.

## Remaining Blockers

- There is still no real candidate result artifact.
- Richer quality scoring remains future work.
- Candidate generation must produce a result artifact from the same frozen
  manifest and pass this comparison gate before any improvement claim.

## Dirty / Untracked State At Handoff Write

Expected paths staged and committed in the substantive comparison-gate commit:

- `CCF_Sovereign/src/evaluation/__init__.py`
- `CCF_Sovereign/src/evaluation/shadow_compare.py`
- `CCF_Sovereign/test_shadow_compare.py`
- `docs/defense_evidence/README.md`
- `docs/defense_evidence/benchmarks/shadow_compare_gate_summary.md`
- `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- `SBIR_plan.md`
- `STATUS.md`
- `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md`
- `plan_2026-07-27_1824_shadow-compare-gate.md`
- `handoff_codex_2026-07-27_shadow-compare-gate.md`

Ignored local artifacts remain intentionally unstaged, especially checkpoints
and `docs/defense_evidence/local_runs/`.

## Next Step

Generate a first candidate result artifact from the same frozen manifest and
run it through the comparison gate.
