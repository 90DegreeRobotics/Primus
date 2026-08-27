# Handoff - Codex promotion governance lane

**Date:** 2026-08-26
**Prepared by:** Codex
**Repository:** `C:\Primus`
**Branch:** `main`
**Lane:** C - Governance

## What changed

Lane C added a pure promotion-governance policy module under
`CCF_Sovereign/src/promotion/`. The policy evaluates completed candidate
manifests and parent/candidate comparison artifacts before an operator may run
the existing explicit `promote_candidate.py` command.

The new code does not train, score live model quality, copy checkpoint bytes,
replace the parent checkpoint, call `promote_candidate.py`, or start candidate
runs. It returns an allow/refuse decision with reasons and an explicit command
string only when evidence and operator authorization are present.

## Files touched

- `plan_2026-08-26_2155_codex-promotion-governance.md`
- `CCF_Sovereign/src/promotion/__init__.py`
- `CCF_Sovereign/src/promotion/gate.py`
- `CCF_Sovereign/test_promotion_gate.py`
- `CCF_Sovereign/test_budget_parity.py`
- `docs/governance/promotion_gate_2026-08-26.md`
- `handoff_codex_2026-08-26_promotion-governance.md`

## Verification run

From `C:\Primus\CCF_Sovereign`:

```powershell
python -m compileall -q src\promotion test_promotion_gate.py test_budget_parity.py
python test_promotion_gate.py
python test_budget_parity.py
python test_candidate_training.py
python test_shadow_compare.py
```

Results:

- Compile gate exited 0.
- `test_promotion_gate.py`: 8 tests passed.
- `test_budget_parity.py`: 6 tests passed.
- `test_candidate_training.py`: 4 tests passed.
- `test_shadow_compare.py`: 6 tests passed.

## What is now covered

- Candidate checkpoint hash must match the operator-supplied expected hash.
- Candidate manifest must be completed.
- Promotion cannot be recorded or permitted as a training side effect.
- Live parent hash before and after evaluation must match the expected parent.
- Candidate manifest parent and frozen-parent hashes must match the expected
  parent.
- Comparison artifact must match the expected evaluation manifest hash.
- Protected regressions, new candidate errors, non-positive pass delta, and
  non-improving verdicts refuse promotion eligibility.
- Operator authorization remains required even when evidence is green.
- First serialized candidate budget is constrained to the `50m` rung.
- Ablation arms must keep equal resource budgets.
- Promotion remains disabled by default for candidate and ablation budgets.

## What was not run

- No candidate training.
- No GPU run.
- No checkpoint promotion.
- No root truth-surface edit.
- No sibling repository access beyond reading local Primus files.

## TRUTH-SURFACE REQUEST

If the director updates `STATUS.md`, the accurate wording is:

```text
Lane C now has a pure promotion-governance policy and focused tests for
hash-gated promotion eligibility, parent immutability, manifest parity,
protected-regression rejection, new-error rejection, 50M first-run budget
constraints, ablation budget parity, and no automatic promotion. This is
governance infrastructure only; no candidate was trained, promoted, or quality
certified.
```

## Next step

Lane B can build ingestion and transition metrics while Lane C keeps the
promotion gate ready. Phase 4 still requires real Phase 2/3 evidence, operator
authorization, and a serialized GPU token before any 50M candidate run.
