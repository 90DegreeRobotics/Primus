# CCF World-Core Day-One Evidence Summary — 2026-08-26

**Classification:** Non-confidential aggregate engineering evidence
**Training code commit:** `eb560c0fb7f64522e0bbc8bb4b1ca7504bea4bfe`
**Device:** NVIDIA GeForce RTX 3060, 12.884 GB reported CUDA memory
**Promotion:** Not performed

## Scope

This record reports the first isolated Primus scaling ladder, the typed
world-schema implementation, and the chunked selective-scan benchmark. It is a
hardware and substrate report. It is **not** evidence that Primus has learned
world dynamics, produces useful language, improves over the parent, or is ready
for product deployment.

## Frozen inputs and isolation

The ladder used a frozen 845-turn corpus containing 1,012,661 tokens after the
local 2,048-token byte-level BPE. Each rung used sequence length 256, batch size
1, one epoch, tied embedding/output weights, equal model/backbone width, and seed
base 20260826. Candidate output remained under ignored per-run directories. The
live parent SHA-256 remained
`5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.

## Scaling ladder

| Rung | Actual parameters | Completed steps | Tokens/s | Peak reserved VRAM | Mean harness loss | Outcome |
|---|---:|---:|---:|---:|---:|---|
| 5M | 5,342,720 | 3,940 | 1,194.65 | 2.28 GB | 7.58 | Completed |
| 15M | 16,214,400 | 3,940 | 623.40 | 4.09 GB | 6.92 | Completed |
| 50M | 53,932,160 | 3,940 | 308.84 | 8.73 GB | 6.84 | Completed |
| 150M | 155,347,584 | 1 | Not recoverable | Not recoverable | 783.02 | CUDA OOM |

The 155.35M rung successfully initialized and completed one logged training
step. CUDA then reported out-of-memory asynchronously as a generic
`RuntimeError`. The original process exited before writing its result row or
marking its candidate manifest failed. Both ignored artifacts were atomically
reconciled from hashed stdout/stderr evidence. Exact 150M throughput and peak
memory are intentionally reported as unavailable rather than estimated. The
harness now classifies both typed and asynchronous RuntimeError CUDA OOM forms.

Loss is included only as a training-path sanity signal. The corpus-to-parameter
ratios and single-epoch design do not support a capability, quality, or scaling-law
claim.

## Chunked selective scan

The former production scan materialized full-sequence FP32 `(B,L,D,N)` state
through every Hillis–Steele stage. The new production path processes bounded
chunks and carries only the boundary state between chunks. The old path remains
available only as a differential oracle.

| Shape and workload | Full-state reserved | Chunked reserved | Full-state tokens/s | Chunked tokens/s |
|---|---:|---:|---:|---:|
| B1, L256, D256, N16, forward | 0.044 GB | 0.017 GB | 89,513.62 | 28,494.31 |
| B1, L1024, D512, N16, forward/backward | 0.950 GB | 0.552 GB | 13,291.53 | 5,467.12 |
| B2, L1024, D512, N16, forward | 0.560 GB | 0.090 GB | 64,107.08 | 62,975.18 |
| B4, L2048, D1024, N16, forward | 4.364 GB | 0.388 GB | 29,669.94 | 55,640.80 |
| B4, L2048, D1024, N16, forward/backward | 16.234 GB | 8.498 GB | 1,121.88 | 9,507.04 |

At the largest stress shape, chunking reduced reported forward/backward reserved
allocator demand by 1.91x and increased throughput by 8.47x. The full-state path
reported allocator demand above the card's dedicated memory, consistent with a
severe oversubscription/spill regime. Chunking is not a universal speedup: the
small shapes are slower because Python chunk and kernel-launch overhead dominates.

Seven focused scan tests passed. They cover recurrent output, final boundary
state, nonzero initial state, complete backward gradients, a 513-token long
sequence, invalid input rejection, preserved full-state differential results,
and complete Mamba-block input/parameter gradients across multiple batch,
sequence, `d_state`, and `d_conv` configurations.

## Typed world schema

The typed schema represents persistent entities, relations, quantized transforms,
explicit camera poses and intrinsics, materials, compiler-owned geometry and
narrative actions, evidence, uncertainty, capability status, and time-ordered
frames. It uses object classes as data and holdout labels rather than selecting
object-specific model recipes.

The 4,096-token codec emits learnable typed semantic markers plus a canonical
byte payload for exact decoding. Structural program signatures remove concrete
entity names and object-class labels while retaining operation order, relation
topology, macro families, parameters, and frame structure. Dataset partitions
support whole-object-class, whole-operation-family, and held-out-composition
splits; random-example holdout is not part of the contract.

Eight focused schema tests passed. They cover deterministic canonical JSON,
lossless bounded token encoding, exact schema-to-S3V-to-schema recovery, explicit
camera/evidence preservation, object-name-independent structural signatures,
operation-order sensitivity, dangling-reference rejection, and explicit
capability status. A generated fixture was independently parsed and validated by
ChronoSophia's real Rust `chronos_s3v` v1 crate as three entities, four actions,
and one frame.

## Stage 2 trajectory infrastructure

A deterministic synthetic trajectory generator now emits canonical JSONL and a
SHA-256-bound manifest for validated three-frame `WorldProgram` records. It
reserves whole object-class, operation-family, and composition holdouts, records
structural-program coverage, and retains generated-versus-inferred evidence,
uncertainty, cameras, and capability status. Seven fail-hard generator tests cover
byte-identical regeneration, holdout isolation, schema/codec/S³V round trips,
canonical records, file hashes, coverage, and refusal to overwrite an existing
destination.

The first ignored smoke dataset contained 21 programs and 21 unique structural
signatures. This is dataset infrastructure, not learned or visually verified
world grounding. The fixtures have not been compiled and rendered as a dataset,
used to train a candidate, or evaluated as predictions.

## Reproduction surfaces

```pwsh
cd C:\Primus\CCF_Sovereign
python test_scaling_ladder.py
python test_world_schema.py
python test_world_trajectory_generator.py
python test_chunked_scan.py
python test_candidate_training.py
python test_mvp.py
```

The raw ladder summary, candidate manifests, checkpoints, scan benchmark JSON,
and stdout/stderr logs remain in ignored local evidence paths. They are not
committed because they include runtime artifacts or checkpoint-bearing paths.

## Remaining gates

A useful world-core claim still requires compiler-executed and render-witnessed
trajectories, model ingestion, held-out prediction evaluation, parent/candidate
quality comparison, retention/forgetting measurement, and an explicit promotion
decision. Deterministic synthetic trajectories, structural-program coverage,
whole-family partitions, and retained uncertainty/provenance now exist as tested
data infrastructure; they do not establish learned world dynamics or visual
correctness. None of those capability claims is implied by this substrate evidence.
