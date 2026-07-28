# Candidate 001 Generation Blocker - 2026-07-27

## Decision

- [x] Candidate-generation path audited.
- [x] Parent checkpoint treated as frozen evidence.
- [x] Local training data inspected by metadata only.
- [x] Candidate 001 was not created.
- [x] Parent checkpoint was not intentionally mutated.

Candidate 001 is a no-go for this pass. The existing trainer is not safe to run
as a shadow/candidate generator because it writes to the canonical parent
checkpoint path.

## Read-Only Evidence Checked

| Item | Evidence |
| --- | --- |
| Parent checkpoint | `CCF_Sovereign/checkpoints/primus_council_trained.pt` |
| Parent checkpoint size | `1784989658` bytes |
| Parent checkpoint SHA-256 | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |
| Training data | `CCF_Sovereign/training/training_data/council_turns.jsonl` |
| Training data size | `3399338` bytes |
| Training data lines | `845` |
| Training data SHA-256 | `8e07223c24ab9234a4b823905d73352eebcb681c04663a592ee7067b0309c556` |
| Training manifest | `CCF_Sovereign/training/training_data/council_turns.manifest.json` |
| Training manifest summary | parser `3.0`, `845` turns, `36` source files |
| Ignored data/checkpoint check | `.gitignore` excludes training JSONL, training manifest JSON, checkpoints, and `docs/defense_evidence/local_runs/` |

No raw prompts, responses, private conversation exports, checkpoints, or
candidate artifacts were staged.

## Blocker Findings

- [x] `CCF_Sovereign/train.py` has no CLI parser and no output-path override.
- [x] The training input path is hardcoded to
  `CCF_Sovereign/training/training_data/council_turns.jsonl`.
- [x] The trainer initializes a fresh `CCFSubstrate(config)` and does not load
  the frozen parent checkpoint as a parent state.
- [x] Every checkpoint save targets
  `CCF_Sovereign/checkpoints/primus_council_trained.pt`.
- [x] The trainer saves at epoch 5, epoch 10, and epoch 15 on CUDA, overwriting
  the same canonical path each time.
- [x] No candidate ID, candidate output directory, parent hash precondition,
  post-run parent hash check, subprocess observer, or candidate manifest is
  implemented in the current trainer.

## Not Run

```pwsh
python CCF_Sovereign\train.py
```

This command was intentionally not run because the audited code path would write
to the frozen parent checkpoint filename.

## Minimum Repair Before Candidate 001

- [ ] Add a candidate-generation entry point that requires an explicit candidate
  ID and explicit output path.
- [ ] Reject any output path that resolves to the parent checkpoint.
- [ ] Record parent checkpoint hash before training and verify it after training.
- [ ] Bind training input hash, parent hash, candidate output hash, environment,
  command, and benchmark manifest into a candidate manifest.
- [ ] Keep raw training data and checkpoint artifacts ignored/local.
- [ ] Run candidate evaluation against the same frozen benchmark manifest as the
  parent baseline.
- [ ] Run the parent/candidate comparison gate before any improvement claim.
