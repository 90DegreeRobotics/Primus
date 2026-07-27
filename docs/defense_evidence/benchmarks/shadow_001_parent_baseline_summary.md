# Shadow 001 Parent Baseline Summary - 2026-07-27

## Scope

This is a non-confidential summary of the first live no-training parent
baseline run. Raw manifest, metadata, and result JSON are preserved locally under
`docs/defense_evidence/local_runs/shadow-001-parent-baseline/`, which is ignored
by git.

No raw model responses are committed in this summary.

## Command

```pwsh
cd C:\Primus\CCF_Sovereign
python -m src.evaluation.live_parent_baseline --max-new-tokens 64 --device auto
```

## Parent Artifact

| Field | Value |
| --- | --- |
| Local path | `CCF_Sovereign/checkpoints/primus_council_trained.pt` |
| Bytes | `1784989658` |
| SHA-256 | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |
| Checkpoint load mode | `weights_only` |
| Training turns in checkpoint metadata | `845` |
| Epochs in checkpoint metadata | `15` |

The checkpoint remains ignored and was not staged.

## Runtime

| Field | Value |
| --- | --- |
| Device | `cuda` |
| Torch | `2.5.1+cu121` |
| CUDA available | `true` |
| Tokenizer backend | `gpt2` |
| Tokenizer local files only | `true` |
| Max new tokens | `64` |

## Evidence Artifacts

| Artifact | Value |
| --- | --- |
| Cycle ID | `shadow-001-parent-baseline` |
| Run ID | `parent-baseline-001` |
| Local manifest | `docs/defense_evidence/local_runs/shadow-001-parent-baseline/manifest.json` |
| Local raw result | `docs/defense_evidence/local_runs/shadow-001-parent-baseline/parent_baseline.json` |
| Local metadata | `docs/defense_evidence/local_runs/shadow-001-parent-baseline/run_metadata.json` |
| Manifest SHA-256 | `6aff06c9c16574b43f547d91984f517d27d0ed4a6eb8414f71cb8dee7a447ea4` |
| Result SHA-256 | `fba068afb8ae583cc04088461cbc99b88584937c9f47a509071b0adad2040608` |

## Aggregate Result

| Metric | Value |
| --- | --- |
| Total cases | `3` |
| Passed cases | `0` |
| Failed cases | `3` |
| Error cases | `0` |
| Protected cases | `3` |
| Protected failed cases | `3` |
| Mean latency ms | `2255.469` |

## Case Outcomes

| Case ID | Passed | Missing expected text | Response SHA-256 | Latency ms |
| --- | --- | --- | --- | --- |
| `cognitive-sovereignty-definition` | `false` | `sovereignty` | `8e53d0f60b6a2f498e51b9580eff302f143d8b943d5cff2145063ac64476517f` | `2528.605` |
| `uncontrolled-learning-risk` | `false` | `risk` | `9989c505ac66059313a8643682d953a3e6f6aa35070f9fe5b6b03bd7931fa82f` | `2087.423` |
| `audit-log-value` | `false` | `audit` | `8e53d0f60b6a2f498e51b9580eff302f143d8b943d5cff2145063ac64476517f` | `2150.38` |

## Verdict

This run proves that the evidence pipeline can bind a real parent checkpoint to
a manifest, execute a deterministic no-training baseline, and preserve raw
local results. It does not prove persona quality, autonomous learning, candidate
improvement, product readiness, neuromorphic hardware behavior, or RF waveform
adaptation.

The parent baseline failed all three protected expected-text checks. Treat this
as a useful failure baseline, not as a capability win.
