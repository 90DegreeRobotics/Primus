# Plan — Five-Boundary Truth Surface Audit

## Goal

Audit the five completed Primus local-capability boundaries against committed
truth surfaces and local ignored evidence, then correct only documentation drift
found during verification.

## Files To Read

- `AGENTS.md`
- `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `README.md`
- `STATUS.md`
- `handoff_manus_2026-08-28_bridgedata-context-robustness.md`
- `handoff_manus_2026-08-28_primus-chronos-transition-contract.md`
- `handoff_manus_2026-08-28_transition-diagnostic-visual.md`
- `handoff_manus_2026-08-28_offline-artifact-safety.md`
- `handoff_manus_2026-08-28_buyer-evidence-demo-gate.md`
- The local ignored JSON/PNG/HTML receipts named by those handoffs

## Files To Edit

- `STATUS.md`
- `handoff_manus_2026-08-28_transition-diagnostic-visual.md`
- this plan

## Ordered Steps

1. [x] Verify `main == origin/main` at the reported completion commit.
2. [x] Check local evidence file existence, byte size, SHA-256, and payload
   fields for the five boundaries.
3. [x] Inspect the accepted diagnostic PNG visually.
4. [x] Correct discovered documentation drift without altering evidence.
5. [x] Run the docs gate.
6. [x] Commit and push the bounded correction to `origin/main`.

## Test Gate

```pwsh
git diff --check --cached
git status --short --branch
```

## Rollback Path

Revert only this docs correction commit if a later audit proves the wording or
hash correction wrong. Do not alter ignored evidence artifacts, candidates,
checkpoints, or receipts.

## Next-Agent Pickup Notes

The five requested boundaries exist as committed code/docs plus ignored local
evidence, but the diagnostic visual handoff had a stale receipt payload hash and
`STATUS.md` retained a stale feasibility-only sentence after later completed
evaluation paragraphs.
