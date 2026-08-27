# Promotion Gate Governance - 2026-08-26

## Scope

This note records the Lane C promotion-governance boundary. The new policy code
under `CCF_Sovereign/src/promotion/` evaluates evidence and returns an
allow/refuse decision. It does not train, evaluate live model quality, copy
checkpoint bytes, replace the parent checkpoint, or call `promote_candidate.py`.

## Required Evidence

A promotion request is eligible only when all of these are true:

- The candidate run manifest is `completed`.
- The candidate checkpoint SHA-256 matches the operator-supplied expected hash.
- The live parent hash before and after evaluation matches the expected parent
  hash.
- The candidate manifest parent and frozen-parent hashes match the expected
  parent hash.
- The parent/candidate comparison is bound to the expected evaluation manifest.
- The comparison gate passed with verdict `CANDIDATE_IMPROVES`.
- Protected-task regressions and new candidate errors are both zero.
- Promotion is not permitted as a training side effect.
- The operator explicitly authorizes promotion.

## Budget Boundary

The first serialized candidate experiment is constrained to the `50m` rung and
requires the promotion/comparison gate to be armed before launch. A `150m` retry
is refused at this governance layer because the current evidence already
records the RTX 3060 CUDA out-of-memory boundary.

Ablation arms must carry equal resource budgets. A lower loss curve is not a
promotion argument unless held-out behavior improves under the same budget.

## Non-Claim

This is governance infrastructure. It is not proof of candidate quality, learned
world dynamics, or a successful promotion event.
