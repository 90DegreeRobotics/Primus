# Handoff: Candidate Generation Audit - 2026-07-27

## Current Verdict

Candidate 001 does not exist. Do not claim it exists.

The existing CCF training path is not safe to run as a shadow/candidate
generator because `CCF_Sovereign/train.py` writes checkpoint saves to the frozen
parent path `CCF_Sovereign/checkpoints/primus_council_trained.pt`.

## Evidence Checked

- `git status --short --branch` started clean except the required audit plan
  after it was created.
- Local parent checkpoint:
  - path: `CCF_Sovereign/checkpoints/primus_council_trained.pt`
  - size: `1784989658` bytes
  - SHA-256: `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`
- Local training data:
  - path: `CCF_Sovereign/training/training_data/council_turns.jsonl`
  - size: `3399338` bytes
  - lines: `845`
  - SHA-256: `8e07223c24ab9234a4b823905d73352eebcb681c04663a592ee7067b0309c556`
- Local training manifest metadata:
  - parser version: `3.0`
  - total turns: `845`
  - source files: `36`
- `.gitignore` excludes training JSONL, training manifest JSON, checkpoints,
  and `docs/defense_evidence/local_runs/`.

## Why Candidate 001 Was Not Run

- `train.py` has no `argparse`/CLI output override.
- `train.py` hardcodes training input to
  `CCF_Sovereign/training/training_data/council_turns.jsonl`.
- `train.py` initializes a fresh `CCFSubstrate(config)` and does not load the
  parent checkpoint as a frozen base.
- `train.py` saves every checkpoint to
  `CCF_Sovereign/checkpoints/primus_council_trained.pt`.
- There is no candidate ID, candidate output directory, parent hash guard,
  post-run parent hash check, training subprocess observer, or candidate
  manifest.

## Next Real Build Step

Implement a hardened candidate-generation entry point before any training run:

- [ ] Require explicit `--candidate-id candidate-001`.
- [ ] Require explicit ignored output path outside the parent checkpoint.
- [ ] Refuse output paths that resolve to
  `CCF_Sovereign/checkpoints/primus_council_trained.pt`.
- [ ] Hash parent checkpoint before and after training.
- [ ] Hash training input and candidate output.
- [ ] Write non-confidential run metadata without raw prompts/responses.
- [ ] Run candidate baseline against the same frozen manifest as the parent.
- [ ] Run `shadow_compare.py` before any improvement claim.

Keep all raw artifacts ignored. Stage only docs, source, and tests with explicit
paths.
