# Handoff: Live Parent Baseline

**Date:** 2026-07-27
**Agent:** Codex
**Branch:** `main`
**Scope:** First live no-training parent baseline against the ignored local CCF
checkpoint.

## What Changed

- Added `CCF_Sovereign/src/evaluation/live_parent_baseline.py`.
- Added `CCF_Sovereign/test_live_parent_baseline.py`.
- Updated `CCF_Sovereign/src/substrate/tokenizer.py` so GPT-2 tokenizer loading
  is local-files-only by default, with byte fallback preserved.
- Reverted a temporary live-runner package export before commit to avoid
  `runpy` import side effects; `CCF_Sovereign/src/evaluation/__init__.py` has
  no final diff in this pass.
- Added `.gitignore` coverage for
  `docs/defense_evidence/local_runs/`.
- Added committed non-confidential evidence summaries:
  - `docs/defense_evidence/benchmarks/shadow_001_parent_baseline_summary.md`
  - `docs/defense_evidence/failures/shadow_001_parent_baseline_failures.md`
- Updated `docs/defense_evidence/README.md`,
  `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`,
  `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`, `SBIR_plan.md`,
  `STATUS.md`, and `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md`.
- Created and maintained
  `plan_2026-07-27_1429_live-parent-baseline.md`.

## Evidence Summary

- Checkpoint path:
  `CCF_Sovereign/checkpoints/primus_council_trained.pt`.
- Checkpoint bytes: `1784989658`.
- Checkpoint SHA-256:
  `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.
- Final live baseline command:
  `python -m src.evaluation.live_parent_baseline --max-new-tokens 64 --device auto`.
- Final live command exited 0.
- Device: `cuda`.
- Torch: `2.5.1+cu121`.
- Checkpoint load mode: `weights_only`.
- Tokenizer backend: `gpt2`, `local_files_only=true`.
- Checkpoint metadata: `training_turns=845`, `epochs=15`.
- Manifest SHA-256:
  `6aff06c9c16574b43f547d91984f517d27d0ed4a6eb8414f71cb8dee7a447ea4`.
- Result SHA-256:
  `fba068afb8ae583cc04088461cbc99b88584937c9f47a509071b0adad2040608`.
- Aggregate: `0/3` protected cases passed, `3/3` failed, `0` execution errors,
  mean latency `2255.469` ms.

Raw local artifacts are intentionally ignored:

- `docs/defense_evidence/local_runs/shadow-001-parent-baseline/manifest.json`
- `docs/defense_evidence/local_runs/shadow-001-parent-baseline/parent_baseline.json`
- `docs/defense_evidence/local_runs/shadow-001-parent-baseline/run_metadata.json`

No raw model responses were committed.

## Commands Run

- `git status --short --branch`; branch was `main...origin/main`.
- `git diff --stat`; no tracked diff at start.
- `git ls-files --deleted`; no deleted tracked files.
- `Get-Content` for repo law, truth surfaces, Charter, Annex, CCF docs/source,
  previous plan/handoff, inference script, and evidence docs.
- `Get-Item CCF_Sovereign\checkpoints\primus_council_trained.pt`; checkpoint
  existed, `1784989658` bytes.
- `Get-FileHash -Algorithm SHA256 CCF_Sovereign\checkpoints\primus_council_trained.pt`;
  hash listed above.
- First `python -m src.evaluation.live_parent_baseline --max-new-tokens 64 --device auto`;
  failed before checkpoint execution because existing `core.*` imports were not
  resolvable under `python -m src...`.
- `python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_live_parent_baseline.py`;
  exit 0 after import-path fix.
- `python test_live_parent_baseline.py`; 4 tests, exit 0 after import-path fix.
- Final live baseline command; exit 0 with aggregate listed above.
- `python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_mvp.py CCF_Sovereign\test_shadow_manifest.py CCF_Sovereign\test_shadow_baseline.py CCF_Sovereign\test_live_parent_baseline.py`;
  exit 0.
- `python test_shadow_manifest.py`; 4 tests, exit 0.
- `python test_shadow_baseline.py`; 4 tests, exit 0.
- `python test_live_parent_baseline.py`; 4 tests, exit 0.
- `python test_mvp.py`; 6 tests, exit 0.

## What Was Not Run

- `python test_inference.py`; the new live baseline supersedes it for this
  evidence pass because it writes manifest-bound JSON instead of print-only
  stochastic output.
- No training run.
- No candidate generation.
- No parent/candidate comparison.
- No Forever Law event-chain sealing.
- No atomic promotion.
- No neuromorphic hardware or RF waveform work.
- No raw responses were reviewed for outreach publication.

## Remaining Blockers

- Parent baseline failed all three protected expected-string checks. This is
  not outreach-ready capability evidence.
- Need richer scoring that can preserve quality evidence without committing raw
  private responses.
- Need candidate generation and parent/candidate comparison on the same frozen
  cases.
- Need retention/forgetting, resource/cost, and power measurements.

## Dirty / Untracked State At Handoff Write

Expected changed/untracked paths before staging:

- `.gitignore`
- `CCF_Sovereign/src/evaluation/live_parent_baseline.py`
- `CCF_Sovereign/src/substrate/tokenizer.py`
- `CCF_Sovereign/test_live_parent_baseline.py`
- `docs/defense_evidence/README.md`
- `docs/defense_evidence/benchmarks/shadow_001_parent_baseline_summary.md`
- `docs/defense_evidence/failures/shadow_001_parent_baseline_failures.md`
- `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`
- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`
- `SBIR_plan.md`
- `STATUS.md`
- `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md`
- `plan_2026-07-27_1429_live-parent-baseline.md`
- `handoff_codex_2026-07-27_live-parent-baseline.md`

Ignored local artifacts remain intentionally unstaged, especially checkpoints
and `docs/defense_evidence/local_runs/`.

## Next Step

Build the parent/candidate comparison skeleton and a richer scoring layer that
can judge quality from raw local outputs without publishing private responses.
