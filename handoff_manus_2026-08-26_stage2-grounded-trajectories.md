# Handoff — Stage 2 governed world trajectories

**Date:** 2026-08-26
**Prepared by:** Manus AI
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\Primus`
**Branch:** `main`
**Factual change commit:** `8cf4e695297b8f76cd6d6de4784581463d6fcf86`
**Promotion status:** No candidate was promoted or authorized for promotion

## Governing files

Read these before substantive follow-on work:

1. `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
2. `C:\Primus\AGENTS.md`
3. `C:\Primus\README.md`
4. `C:\Primus\STATUS.md`
5. `C:\Primus\plan_2026-08-26_2024_stage2-grounded-trajectories.md`
6. `C:\Primus\CCF_Sovereign\README.md`
7. `C:\Primus\CCF_Sovereign\docs\WORLD_SCHEMA_V1.md`
8. `C:\Primus\docs\research\PRIMUS_THESIS_VALUE_AND_NOVELTY_2026-08-26.md`

> Repository state, executable gates, and hash evidence outrank prose if any surface becomes stale. A generated dataset is not a trained model, and a process or manifest is not evidence of capability or promotion.

## What changed

The factual commit adds the first bounded Stage 2 world-trajectory data lane. `CCF_Sovereign/src/world_schema/trajectory_generator.py` now emits deterministic three-frame `WorldProgram` records with persistent entities, relations, geometry and state-transition operations, cameras, generated and inferred evidence, quantified uncertainty, capability status, and explicit dataset partitions.

The generator reserves a whole object class, a whole operation family, and a composition of otherwise-seen families. It does not expose a random-example split. It validates every program, 4K token encoding, S³V round trip, identity set, and holdout contract before returning a dataset. The writer refuses an existing destination, stages output in a temporary sibling directory, verifies bytes, and publishes canonical JSONL plus a deterministic manifest.

The commit also adds `CCF_Sovereign/generate_world_trajectories.py`, seven fail-hard generator tests, package exports, and coordinated updates to the root and CCF truth surfaces. No Chronos2 source, training code, model checkpoint, candidate manifest, promotion surface, or raw corpus was changed.

## Factual commit contents

| Path | Purpose |
|---|---|
| `CCF_Sovereign/src/world_schema/trajectory_generator.py` | Deterministic generation, holdout validation, manifests, and atomic publication |
| `CCF_Sovereign/generate_world_trajectories.py` | Explicit-destination command-line entry point |
| `CCF_Sovereign/test_world_trajectory_generator.py` | Seven fail-hard Stage 2 tests |
| `CCF_Sovereign/src/world_schema/__init__.py` | Public package exports |
| `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md` | Authoritative generator contract and proof boundary |
| `CCF_Sovereign/README.md` | Developer command and non-claims |
| `README.md` | Root orientation and capability boundary |
| `STATUS.md` | Verified smoke evidence and remaining gaps |
| `docs/defense_evidence/benchmarks/ccf_world_core_day_one_2026-08-26.md` | Updated world-core evidence and remaining gates |

## Verification performed

The final matrix ran from `C:\Primus\CCF_Sovereign` after the last source change. Every command exited `0`.

| Gate | Result | Measured duration |
|---|---:|---:|
| `python -m compileall -q src\world_schema generate_world_trajectories.py test_world_schema.py test_world_trajectory_generator.py` | Pass | 0.153 s |
| `python test_world_schema.py` | 8 tests passed | 0.249 s command time |
| `python test_world_trajectory_generator.py` | 7 tests passed | 2.632 s command time |
| `python test_candidate_training.py` | 4 tests passed | 12.675 s command time |
| `python test_mvp.py` | 6 tests passed | 8.326 s command time |

The required Markdown auditor passed five Stage 2 truth surfaces after unresolved-marker detection was narrowed to word boundaries. An initial audit failure was a false positive on the existing, truthful phrase “business/team placeholders” in `STATUS.md`; no unrelated SBIR text was changed. The cached Git whitespace gate also initially caught Markdown hard-break spaces in the plan. Those spaces were removed before staging.

## Smoke dataset evidence

The first ignored local smoke artifact remains at:

`C:\Primus\CCF_Sovereign\tmp\stage2_smoke_20260826_2024\`

| Signal | Result |
|---|---:|
| Seed | `20260826` |
| Programs | 21 |
| Train | 12 |
| Held-out object class | 3 |
| Held-out operation family | 3 |
| Held-out composition | 3 |
| Frames per program | 3 |
| Structural signatures | 21 unique, 0 duplicate |
| Token sequence length | minimum 7,391; mean 7,436.762; maximum 7,494 |
| JSONL SHA-256 | `3a0b5e79bd592dffb2731131f83ce1d1db93a583dd7aed0bdbe6718e4beb3a28` |
| Manifest SHA-256 | `6af0b09145aa680e527db98e33b6bf10bcd5752bef7e523e1180301b00d7f607` |
| Program-hash-set SHA-256 | `9a90253d7da94fb267a6bb7836d6e62a54004cf70a114e1c70d21251a07fd2fe` |

The smoke manifest explicitly records `model_training_started: false`, `checkpoint_modified: false`, `candidate_promoted: false`, `learned_world_dynamics_proven: false`, and `visual_correctness_proven: false`.

## Protected parent and process state

The protected parent remained byte-identical before and after Stage 2 work:

```text
CCF_Sovereign/checkpoints/primus_council_trained.pt
Bytes: 1,784,989,658
SHA-256: 5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b
```

No Primus scaling-ladder process was active during the baseline. No training command, candidate creation command, evaluation promotion command, or checkpoint-writing command was run. Candidate promotion remains **none**.

## Chronos2 concurrency boundary

`C:\chronos2` was inspected read-only and intentionally not modified. At the time of the baseline it was on `main` at `78bed56ac1bf6857260c44e37a437ae7bbe9ab6c` with no upstream configured for local `main`. Its visible tree was dirty with tracked edits to `AGENTS.md`, `crates/chronos_cli/src/governed_artifact.rs`, `crates/chronos_dreamer/src/hull_showcase.rs`, `desktop/test_tabs_runtime.py`, and `scripts/chronos_windows_paths.ps1`, plus untracked review and extraction residue. Multiple Claude/Codex processes were present. Do not sweep, stage, reset, or attribute those paths without a fresh ownership audit.

## What remains unproven

This unit generates deterministic synthetic typed trajectories. It does not establish that those trajectories are physically valid, visually correct, compiler-executable as a dataset, representative of customer worlds, or sufficient for model learning. The evidence bindings are `generated` and `inferred`; they are not presented as `observed` or `measured`.

The learner still consumes transcript-style text. The Stage 2 JSONL has not been ingested, segmented, batched, or used in a candidate run. No action-conditioned next-state accuracy, held-out prediction accuracy, compiler acceptance rate for the full dataset, render-witness score, forgetting result, or parent/candidate delta exists. The observed 7.4K-token program length also means later throughput work must use this trajectory shape rather than the older 256-token transcript benchmark.

## Next technical sequence

First, add a governed compiler-execution and render-witness lane for these fixtures when the Chronos2 ownership boundary is clean. Preserve per-program compiler receipts, S³V hashes, render hashes, failure classes, and evidence-kind distinctions. Do not relabel synthetic state as observation merely because a renderer accepts it.

Second, design model ingestion around action-conditioned transitions and protected whole-family splits. The data loader must bind the generator manifest hash, reject train/evaluation overlap, define program segmentation for 7.4K-token records, and report state, relation, operation, evidence, uncertainty, and compiler-validity metrics separately.

Third, run a small 50M-class candidate experiment before any 150M attempt. Keep equal resource budgets across the A–F ablation sequence, retain the existing no-promotion default, and stop early if optimization does not cross the appropriate baseline. Depth-30 instability and dispatch overhead remain separate investigations.

## Verification commands for the next instance

```powershell
cd C:\Primus
git status --short --branch
git log -4 --oneline
git rev-parse HEAD
git rev-parse origin/main
Get-FileHash CCF_Sovereign\checkpoints\primus_council_trained.pt -Algorithm SHA256

cd C:\Primus\CCF_Sovereign
python test_world_schema.py
python test_world_trajectory_generator.py
python test_candidate_training.py
python test_mvp.py
```

Do not say that Stage 2 is complete as a learned-world experiment. The accurate claim is narrower: **Primus now has deterministic, hash-bound, partitioned temporal `WorldProgram` dataset infrastructure with fail-hard evidence gates. Compiler/render grounding, model ingestion, held-out learning, and promotion remain open.**
