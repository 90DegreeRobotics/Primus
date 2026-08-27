# Plan — all-lanes integration and governed Wave 3 50M candidate

**Created:** 2026-08-27 06:41 CDT
**Owner:** Manus, acting under Michael Holt’s explicit directive to finish integration and Wave 3
**Repository:** `C:\Primus`
**Branch:** `main`
**Code commit:** `a18f4d690163132b062a8021949d9826b115dbb9`
**Status:** EXECUTION COMPLETE — documentation closure remains before final delivery

## Goal

Push the already-committed verified Wave 1–2 units ahead of `origin/main`, then execute exactly one bounded 50M-class candidate experiment only after clean-repository, candidate-isolation, policy, hardware, and protected-checkpoint checks. Preserve the actual result, including its evaluation limits and default non-promotion outcome.

## Governing sources and working inputs read

- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `AGENTS.md`
- [x] `vision_deep_dive.md` as orientation only
- [x] `plan_2026-08-26_2144_multi-lane-build-charter.md`
- [x] `CCF_Sovereign/src/benchmarks/scaling_ladder.py`
- [x] `CCF_Sovereign/src/promotion/gate.py`
- [x] `CCF_Sovereign/training/candidate_run.py`
- [x] `handoff_claude_2026-08-26_lane-a-compiler-witness.md`
- [x] Current all-lanes log, commit history, active process state, candidate/checkpoint inventory, corpus inputs, comparison gate, and training-budget contract

`vision_deep_dive.md` supports orientation only. It does not support a provenance, priority, legal, or capability claim in this plan.

## Files and artifacts created

- [x] `plan_2026-08-27_0641_wave3-50m-candidate.md` — this governed execution record
- [x] `CCF_Sovereign/checkpoints/candidates/wave3-50m-20260827-0641-50m/` — unique isolated candidate destination
- [x] `CCF_Sovereign/tmp/manus_wave3_50m_20260827_0641.log` — ignored runtime log
- [x] `docs/defense_evidence/local_runs/wave3-50m-20260827-0641/` — ignored hardware/throughput evidence
- [ ] `handoff_manus_2026-08-27_wave3-50m-candidate.md` — final exact evidence handoff

No parent or frozen checkpoint, training corpus, sibling repository, foreign builder file, or director-only truth surface was edited by this plan.

## Completed ordered work

- [x] Reproduced the 77 regression tests across ten suites and confirmed both protected parent copies were unchanged.
- [x] Pushed three already-committed Wave 1–2 units: `a6d901ec`, `4d8929da`, and `18e17b7`; afterward `HEAD == origin/main`.
- [x] Committed and pushed the standalone governed preparation plan as `a18f4d690163132b062a8021949d9826b115dbb9` so candidate creation saw a clean repository.
- [x] Recorded a fresh external launch snapshot at `C:\Users\m\AppData\Local\Temp\manus_wave3_evidence\wave3_launch_preflight_20260827_0641.json`, SHA-256 `a5e912c093ea6deaba80e0823160342ba80c5fa254d8caa028d124bcf61d40e1`.
- [x] Confirmed the exact policy decision allows a `50m`, 100-step, batch-1, 256-token, one-epoch budget only under the recorded operator authorization and armed-gate basis. Promotion remains false by default.
- [x] Confirmed PyTorch CUDA availability with one real allocation on `NVIDIA GeForce RTX 3060` (12,884,377,600 bytes). NVML remained unavailable, so `nvidia-smi` cannot supply telemetry in this environment.
- [x] Measured the selected ladder model at 53,932,160 parameters, `D=640`, `L=20`; the 50M rung is 7.86432% above its nominal target and within the policy’s 50M-class restriction.
- [x] Launched exactly one isolated 100-step candidate run: `wave3-50m-20260827-0641-50m`.
- [x] Verified zero active Wave 3 processes after exit; candidate lifecycle is `completed`; checkpoint, manifest, evidence summary, and runtime log exist.
- [x] Rehashed the live parent and frozen parent after checkpoint creation and post-run restore; both remain `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.
- [x] Restored the candidate checkpoint on CUDA and completed one finite forward pass with output shape `[1, 256, 2048]`.
- [x] Applied the non-mutating promotion policy against actual candidate artifacts. It returned `eligibility=false`, `performs_mutation=false`, and `automatic_promotion=false` because no behavioral comparison/evaluation manifest exists, the comparison gate did not pass, pass delta was not positive, and no separate promotion authorization exists.
- [ ] Write, audit, commit, and push the exact final handoff and plan closure as a separate documentation unit; do not modify ignored candidate artifacts.

## Actual candidate configuration and measured result

| Parameter | Actual value |
|---|---:|
| Candidate ID | `wave3-50m-20260827-0641-50m` |
| Rung | `50m` |
| Model parameters | 53,932,160 |
| Model shape | `D=640`, `L=20`, `d_state=16`, `d_conv=4`, `expand=2` |
| Device | NVIDIA GeForce RTX 3060 / CUDA |
| VRAM capacity | 12.8843776 GB |
| Sequence length | 256 |
| Batch size | 1 |
| Steps | 100 |
| Predicted tokens | 25,600 |
| Elapsed time | 109.8648043 seconds |
| Throughput | 233.0136586 tokens/s |
| Peak allocated / reserved | 7.200100864 / 7.233077248 GB |
| Inference batch probes | batch sizes 1, 2, and 4 all completed; highest observed reserved memory 1.440743424 GB |
| Candidate checkpoint SHA-256 | `4842588e50731b6c0ba2cc883f160c624c72a86bf0dca55b2a8f84be47f0919c` |
| Candidate manifest SHA-256 at policy evaluation | `8c0478dcdabb78689727d375479d782336b84dbd78eadccaff26a71de8de6636` |

The recorded step losses were 574.5605 at step 1, 26.3873 at step 50, and 17.1370 at step 100. The exact uniform 2,048-token cross-entropy reference is `ln(2048) = 7.624618986159`. Loss therefore declined sharply but remained above that simple baseline after the 100-step diagnostic. This run demonstrates allocation, execution, 100-step memory feasibility, observed throughput, checkpoint writing, restoration, and partial optimization trajectory only. It does not demonstrate optimization beyond the uniform reference, learned-world behavior, held-out generalization, renderer correctness, visual grounding, or capability.

## Candidate and promotion boundaries

The frozen Council corpus was used exactly as the existing scaling-ladder harness defines it: 845 turns, 1,012,661 tokens, 3,940 blocks, JSONL SHA-256 `8e07223c24ab9234a4b823905d73352eebcb681c04663a592ee7067b0309c556`, corpus manifest SHA-256 `8bfe4837c1c65e801396a21ddf133d8eddcd424b71a6feadfb5419b0712874fa`. The Stage 2 world-data loader is not integrated into `train.py` or `scaling_ladder.py`. Accordingly, the run is not world-model training and it cannot furnish Phase 3 held-out world-transition scores.

A prior local candidate, `ladder-ab-150m-20260826-150m`, remains labelled `training` in its historic manifest while no matching live process exists. It was preserved untouched as evidence of a stale lifecycle record and did not enter this candidate’s path, inputs, or result.

No promotion command was run. The candidate remains isolated. There is no automatic promotion path in the run or in the applied policy decision.

## Final documentation gate

```powershell
cd C:\Primus
python tmp\manus_audit_markdown.py plan_2026-08-27_0641_wave3-50m-candidate.md handoff_manus_2026-08-27_wave3-50m-candidate.md --require-regex "not a world-model|not world-model|not.*world-model" --require-regex "No promotion|no promotion|non-promotion" --forbid-regex "\bTODO\b|\bPLACEHOLDER\b"
git diff --check --cached
```

The final documentation commit must use exact pathspecs for this plan and handoff only, after a fresh clean-tree audit. It must not include candidates, checkpoints, logs, local run outputs, temporary helpers, unrelated plans, or any other work.

## Rollback path

Never reset, clean, force-push, amend a pushed commit, delete a checkpoint, reuse a candidate ID, or copy a candidate over the parent. The completed candidate, manifest, runtime log, and local evidence remain preserved. Promotion remains a separate explicit operator-run transaction and is not authorized by the candidate execution, checkpoint restore, loss decline, or this documentation plan.

## Next-agent pickup notes

The first unfinished action is the documentation-only handoff closure. It should preserve all hashes above, report the `nvidia-smi` NVML telemetry limitation separately from the successful CUDA allocation and training evidence, and state that the 100-step loss did not reach the uniform 2,048-token reference. Any future learned-world claim requires a separate training integration using manifest-bound Stage 2 input, actual model predictions, held-out object/operation/composition evaluation, and a new evidence protocol. Any future promotion needs a completed behavioral comparison artifact, a passed policy decision, clean repository state, expected hashes, and a separate explicit operator authorization.
