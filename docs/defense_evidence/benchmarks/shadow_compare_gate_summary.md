# Shadow Compare Gate Summary - 2026-07-27

## Scope

This is a non-confidential summary of the parent/candidate comparison gate added
after the first live parent baseline. It is a referee layer only. It does not
generate a candidate, train a model, inspect raw private responses, or promote
an artifact.

## Implemented Surface

| Surface | Value |
| --- | --- |
| Module | `CCF_Sovereign/src/evaluation/shadow_compare.py` |
| Test | `CCF_Sovereign/test_shadow_compare.py` |
| Runner label | `shadow_parent_candidate_compare` |
| Input shape | Parent result JSON + candidate result JSON |
| Output shape | Comparison JSON without raw response text |

## Gate Behavior

- Rejects manifest SHA-256 mismatch.
- Rejects cycle ID mismatch.
- Rejects parent/candidate case-set mismatch.
- Computes pass/fail delta.
- Detects recovered failures.
- Detects protected-task regressions.
- Detects new candidate errors.
- Computes per-case latency deltas and mean case-latency delta.
- Emits a promotion-safe verdict.

## Verdicts

| Verdict | Meaning |
| --- | --- |
| `CANDIDATE_IMPROVES` | Candidate has positive pass delta with no protected regressions or new errors. |
| `NO_PROMOTION_NO_IMPROVEMENT` | Candidate does not regress, but does not improve enough to pass the gate. |
| `REJECT_PROTECTED_REGRESSION` | Candidate failed a protected case the parent passed. |
| `REJECT_NEW_ERRORS` | Candidate introduced execution errors absent from the parent run. |

## Boundary

This gate was tested with fixture JSON only. No live candidate result exists yet.
The first real candidate must produce a manifest-bound result artifact and pass
this gate against the frozen parent baseline before any improvement claim is
allowed.
