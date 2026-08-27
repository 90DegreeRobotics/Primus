# Plan - Codex promotion governance lane

**Created:** 2026-08-26 21:55 -05:00
**Author:** Codex
**Status:** COMPLETE

## Goal

Execute Lane C from the multi-lane build charter: add fail-closed promotion
governance and budget/parity test coverage without wiring any automatic
promotion path, starting from the synced `main` baseline.

## Files to read

- `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `vision_deep_dive.md`
- `plan_2026-08-26_2144_multi-lane-build-charter.md`
- `handoff_manus_2026-08-26_stage2-grounded-trajectories.md`
- `CCF_Sovereign\README.md`
- `CCF_Sovereign\MVP_STATUS.md`
- `CCF_Sovereign\requirements.txt`
- `CCF_Sovereign\promote_candidate.py`
- `CCF_Sovereign\training\candidate_run.py`
- `CCF_Sovereign\src\evaluation\shadow_compare.py`
- `CCF_Sovereign\src\benchmarks\scaling_ladder.py`
- Existing tests for candidate training, shadow comparison, and scaling ladder.

## Files to edit

- `CCF_Sovereign\src\promotion\__init__.py` (new)
- `CCF_Sovereign\src\promotion\gate.py` (new)
- `CCF_Sovereign\test_promotion_gate.py` (new)
- `CCF_Sovereign\test_budget_parity.py` (new)
- `docs\governance\promotion_gate_2026-08-26.md` (new)
- `handoff_codex_2026-08-26_promotion-governance.md` (new)
- This plan file.

No root truth surface, checkpoint, training data, sibling repo, or Lane A/B path
will be edited.

## Ordered steps

1. Finish reading existing candidate, promotion, comparison, and ladder code. DONE
2. Add a pure promotion-policy module that evaluates existing evidence records
   and returns an explicit allow/refuse decision.
   DONE
3. Add fail-hard tests for hash-gated promotion, protected-task regression
   rejection, new-error rejection, manifest parity, parent immutability, and
   refusal to auto-promote.
   DONE
4. Add budget/parity tests for 50M-only first-run authorization and equal
   budget constraints across ablation arms.
   DONE
5. Add a governance note documenting the policy boundary and non-automation.
   DONE
6. Run the focused compile/test gates. DONE
7. Update this plan and write the handoff. DONE
8. Report exact dirty state and whether commit/push was performed. DONE

## Outcome

Lane C added a pure promotion governance evaluator plus budget/parity checks.
The evaluator returns an explicit allow/refuse decision and the command an
operator may run, but it performs no mutation and cannot auto-promote.

## Test gate

From `C:\Primus\CCF_Sovereign`:

```pwsh
python -m compileall -q src\promotion test_promotion_gate.py test_budget_parity.py
python test_promotion_gate.py
python test_budget_parity.py
python test_candidate_training.py
python test_shadow_compare.py
```

Executed from `C:\Primus\CCF_Sovereign` on 2026-08-26:

- `python -m compileall -q src\promotion test_promotion_gate.py test_budget_parity.py` - exit 0
- `python test_promotion_gate.py` - 8 tests passed
- `python test_budget_parity.py` - 6 tests passed
- `python test_candidate_training.py` - 4 tests passed
- `python test_shadow_compare.py` - 6 tests passed

From `C:\Primus`:

```pwsh
git status --short --branch
git diff --stat
git ls-files --deleted
```

## Rollback path

Because the lane uses only new files plus this plan and a new handoff, rollback
is explicit per-file deletion on operator instruction. No existing code or
checkpoint is mutated.

## Next-agent pickup notes

This lane must remain a policy/test layer. It may authorize a promotion request
as data, but it must not copy checkpoint bytes, replace the parent, call
`promote_candidate.py`, or start candidate training.
