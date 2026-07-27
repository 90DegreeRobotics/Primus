# Shadow 001 Parent Baseline Failure Report - 2026-07-27

## Summary

The first live no-training parent baseline completed without execution errors,
but failed every protected expected-text check.

Raw responses are preserved only in the ignored local result JSON:

`docs/defense_evidence/local_runs/shadow-001-parent-baseline/parent_baseline.json`

No raw responses are committed in this report.

## Failure Counts

- Total cases: `3`
- Failed cases: `3`
- Protected failed cases: `3`
- Error cases: `0`

## Failed Checks

| Case ID | Missing expected text | Response SHA-256 |
| --- | --- | --- |
| `cognitive-sovereignty-definition` | `sovereignty` | `8e53d0f60b6a2f498e51b9580eff302f143d8b943d5cff2145063ac64476517f` |
| `uncontrolled-learning-risk` | `risk` | `9989c505ac66059313a8643682d953a3e6f6aa35070f9fe5b6b03bd7931fa82f` |
| `audit-log-value` | `audit` | `8e53d0f60b6a2f498e51b9580eff302f143d8b943d5cff2145063ac64476517f` |

## Interpretation

The failure is evidence, not a defect to hide. The current parent checkpoint can
load and generate, but this baseline gives no support for claiming a reliable
Council persona, outreach-ready explanation quality, or protected-task
retention.

## Next Repair Target

Before candidate comparison, improve the benchmark harness so it records richer
quality signals without committing private raw responses. Then add a candidate
path and compare parent versus candidate on the same frozen cases.
