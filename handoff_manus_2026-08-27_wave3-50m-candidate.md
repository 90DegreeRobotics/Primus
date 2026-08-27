# Handoff — Wave 3 50M candidate diagnostic

**Date:** 2026-08-27 CDT
**Prepared by:** Manus
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\Primus` / `main`
**Code commit bound at candidate creation:** `a18f4d690163132b062a8021949d9826b115dbb9`
**Candidate ID:** `wave3-50m-20260827-0641-50m`
**Candidate lifecycle:** `completed`
**Promotion status:** not eligible; no promotion command run

## Executive status

Wave 1–2’s three local commits were independently re-tested and pushed to `origin/main` before the candidate preflight. The governed Wave 3 run then completed exactly one 50M-class, 100-step CUDA diagnostic in an isolated candidate directory. It demonstrated allocation, execution, memory feasibility for the bounded workload, measured throughput, checkpoint writing, checkpoint restoration, and finite inference output.

It is **not a world-model** run and did **not** demonstrate a learned world model, world-data ingestion into training, next-state prediction, held-out world generalization, render correctness, visual grounding, promotion eligibility, or a product-capability result. The run used the existing Council conversation corpus through the scaling-ladder harness. The 100-step final observed loss remained above the exact uniform 2,048-token reference, so even optimization beyond that reference is not established. This 100-step diagnostic does not supersede the August 26 full 50M ladder result that ran the same rung for 3,940 steps.

## What changed

| Item | Result |
|---|---|
| Wave 1–2 integration | Pushed `a6d901ec`, `4d8929da`, and `18e17b7` after a reproduced 77-test gate across ten suites |
| Wave 3 preparation plan | Committed and pushed as `a18f4d690163132b062a8021949d9826b115dbb9` |
| Candidate isolation | Created only `CCF_Sovereign/checkpoints/candidates/wave3-50m-20260827-0641-50m/` |
| Runtime evidence | Created ignored `docs/defense_evidence/local_runs/wave3-50m-20260827-0641/` and `CCF_Sovereign/tmp/` logs/helpers |
| Parent/frozen checkpoint | Not modified; SHA-256 remained `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |
| Training source | Existing Council corpus only; it is not the manifest-bound Stage 2 world-data path |
| Promotion | No automatic or explicit promotion; non-mutating policy decision is ineligible |

## Candidate configuration and measured result

| Signal | Observed value |
|---|---:|
| 50M rung actual parameter count | 53,932,160 |
| Architecture | `D=640`, `L=20`, `d_state=16`, `d_conv=4`, `expand=2`, tied embedding head |
| Device | NVIDIA GeForce RTX 3060 / CUDA |
| CUDA capacity | 12.8843776 GB |
| CUDA preflight allocation | 4,194,304 bytes, successful |
| Sequence length / batch size | 256 / 1 |
| Bounded steps / epoch | 100 / 1 |
| Prediction tokens | 25,600 |
| Wall time | 109.8648043 seconds |
| Throughput | 233.0136586 tokens/s |
| Peak allocated / reserved VRAM | 7.200100864 / 7.233077248 GB |
| Inference probe | batch sizes 1, 2, and 4 passed; maximum probe reservation 1.440743424 GB |
| Candidate checkpoint SHA-256 | `4842588e50731b6c0ba2cc883f160c624c72a86bf0dca55b2a8f84be47f0919c` |
| Candidate manifest SHA-256 at policy evaluation | `8c0478dcdabb78689727d375479d782336b84dbd78eadccaff26a71de8de6636` |

The observed loss checkpoints are 574.5605 at step 1, 26.3873 at step 50, and 17.1370 at step 100. The computed uniform loss reference is `ln(2048) = 7.624618986159`. The decline is real but the final value remains 9.512381013841 above the reference. It would be false to call this optimization success, generalization, or capability.

The loss and throughput must be read with step count beside them:

| Run | Matching configuration | Steps | Loss / throughput |
|---|---|---:|---|
| August 26 full 50M ladder | 53,932,160 params, `D=640`, `L=20`, same Council corpus hash, same tokenizer, batch 1, sequence 256 | 3,940 | mean loss 6.84; 308.84 tokens/s |
| Wave 3 50M diagnostic | 53,932,160 params, `D=640`, `L=20`, same Council corpus hash, same tokenizer, batch 1, sequence 256 | 100 | step-100 loss 17.1370; 233.0136586 tokens/s |

Wave 3 is therefore an earlier bounded point on the same harness shape, not evidence that the established 50M rung regressed, failed to beat random at full duration, or ceased to be the practical starting size. The lower throughput is likewise not a proven regression because startup and fixed overhead are amortized over only 100 steps rather than 3,940.

## Inputs, integrity, and artifacts

| Artifact | SHA-256 | Status |
|---|---|---|
| Live parent checkpoint | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` | Verified before launch, after checkpoint write, and after restore smoke |
| Frozen parent checkpoint | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` | Same immutable content as live parent |
| Council JSONL | `8e07223c24ab9234a4b823905d73352eebcb681c04663a592ee7067b0309c556` | Frozen by candidate manifest |
| Council manifest | `8bfe4837c1c65e801396a21ddf133d8eddcd424b71a6feadfb5419b0712874fa` | Frozen by candidate manifest |
| Candidate checkpoint | `4842588e50731b6c0ba2cc883f160c624c72a86bf0dca55b2a8f84be47f0919c` | Isolated, retained as local evidence |
| Prelaunch repository snapshot | `a5e912c093ea6deaba80e0823160342ba80c5fa254d8caa028d124bcf61d40e1` | `C:\Users\m\AppData\Local\Temp\manus_wave3_evidence\wave3_launch_preflight_20260827_0641.json` |

The run verified `torch.cuda.is_available() == true`, one CUDA device, and a real allocation on the RTX 3060. `nvidia-smi` failed with `Failed to initialize NVML: Unknown Error`; that is a telemetry limitation only, not evidence that the CUDA run failed.

## Commands run and real results

| Command or gate | Result |
|---|---|
| Full Wave 1–2 integration suite | 77 tests across ten suites passed: schema 8, generator 7, compiler 13, ingestion 11, metrics 8, candidate safety 4, promotion 8, budget parity 6, shadow compare 6, MVP 6 |
| `python -m src.benchmarks.scaling_ladder ... --describe` | Constructed the 50M rung and measured 53,932,160 parameters |
| 50M budget-policy preflight | Allowed with operator authorization basis, armed gate, and `promotion_permitted_by_default=false` |
| PyTorch CUDA allocation preflight | Passed on RTX 3060; 1 device visible |
| `python -m src.benchmarks.scaling_ladder ... --rungs 50m --max-steps 100` | Completed; candidate checkpoint and evidence summary created |
| Candidate checkpoint restore smoke | Passed on CUDA; strict state restore; finite `[1, 256, 2048]` logits |
| Non-mutating promotion policy | Ineligible; `performs_mutation=false`; `automatic_promotion=false` |

## Promotion decision and non-claims

The non-mutating policy rejected promotion for the right reasons: there is no behavioral comparison/evaluation manifest, the comparison gate did not pass, the verdict is not `CANDIDATE_IMPROVES`, the comparison pass delta is not positive, and no separate promotion authorization was presented. Its only generated `required_command` is conditional guidance and was **not** executed.

No parent checkpoint was replaced, no frozen archive was changed, no candidate was copied to a parent path, no render was attempted, no S3V fixture was relabelled, and no truth surface was edited directly. Two historic candidates remain marked `training` while no matching live candidate process was identified:

- `ladder-ab-150m-20260826-150m` - 150M, batch 1, sequence 256.
- `ladder-chunked-20260826b-15m` - 15M, batch 2, sequence 512; the known confounded chunked-ladder run.

Both were preserved untouched as stale lifecycle artifacts and did not affect this run.

## TRUTH-SURFACE REQUEST

**Target file:** `STATUS.md` (director-only)
**Evidence basis:** this handoff; the isolated candidate manifest; `scaling_ladder.json`; the runtime log; and the prelaunch snapshot listed above.

**Proposed wording:**

> **Wave 3 completed as a bounded hardware and harness diagnostic, not a learned-world result.** A 53,932,160-parameter 50M-class candidate completed 100 CUDA training steps on the frozen Council corpus at 233.0137 tokens/s, with 7.2331 GB peak reserved VRAM, an isolated checkpoint, and unchanged live/frozen parent hashes. The candidate checkpoint restored and produced finite logits. The final observed loss declined but remained above the uniform 2,048-token reference after the 100-step diagnostic; because the prior identical 50M ladder ran 3,940 steps and reached mean loss 6.84, this 100-step result does not supersede the August 26 full-ladder finding. The Stage 2 world-data loader is not wired into this run, no world-transition or held-out behavior was evaluated, no render was run, and the non-mutating promotion policy is ineligible. No candidate was promoted.

## Working-tree and remote status before documentation closure

At the end of execution the tracked repository was clean at `a18f4d690163132b062a8021949d9826b115dbb9`, equal to `origin/main`, before this handoff and the execution-plan update were written. All candidate, evidence, runtime-log, and temporary helper artifacts are ignored by policy and must remain out of Git.

## Next step

Audit and commit only this handoff plus `plan_2026-08-27_0641_wave3-50m-candidate.md` as a documentation-only closure unit, then push `main` and verify synchronization. Future research should not schedule an A–F ablation yet: first wire the manifest-bound Stage 2 dataset into a training path, obtain actual model predictions, and evaluate separate protected object, operation, and composition holds. A 50M run on the Council corpus does not answer the world-learning thesis.
