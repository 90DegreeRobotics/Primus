# Defense Evidence Package

This folder is the non-confidential evidence package for future MDA, DoD prime,
DIU, DARPA, SBIR/STTR, or other defense-facing conversations.

It is not a proposal upload folder. Do not store private company identifiers,
SAM/UEI screenshots, tax records, banking data, export-controlled technical
detail, controlled unclassified information, raw private conversations,
checkpoints, model weights, or training corpora here.

## Current Status

- [x] Evidence package folder created.
- [x] Manifest code scaffold exists at
  `CCF_Sovereign/src/evaluation/shadow_manifest.py`.
- [x] Manifest tests exist at `CCF_Sovereign/test_shadow_manifest.py`.
- [x] No-training parent baseline result writer exists at
  `CCF_Sovereign/src/evaluation/shadow_baseline.py`.
- [x] No-training parent baseline tests exist at
  `CCF_Sovereign/test_shadow_baseline.py`.
- [x] First real shadow-cycle manifest generated from live artifacts.
- [x] First live parent baseline run against a real parent artifact.
- [x] Parent/candidate comparison gate exists with fixture tests.
- [x] Candidate-generation path audited for parent mutation risk.
- [ ] Candidate 001 generated as an isolated artifact.
- [ ] First parent/candidate benchmark run.
- [x] First raw failure record preserved locally and summarized without raw
  responses.
- [ ] First retention/forgetting measurement.
- [x] First latency measurement from a live parent baseline.
- [ ] First resource measurement beyond `device=cuda`.
- [ ] First non-confidential capability statement reviewed for IP safety.

## Intended Subfolders

Create these only when there is real content to preserve:

- `capability/` - non-confidential one-pagers and outreach-safe summaries.
- `manifests/` - shadow-cycle manifests generated from real artifacts.
- `benchmarks/` - benchmark schemas, reproduction notes, and aggregate results.
- `failures/` - failure reports preserved without cosmetic rewriting.
- `measurements/` - latency, retention, forgetting, resource, and cost data.
- `hardware_translation/` - neuromorphic translation notes and assumptions.
- `outreach/` - date/target/material/response logs without private screenshots.

## Evidence Rules

- [x] Every manifest must name parent artifact, training inputs, benchmark cases,
  and hashes where files exist.
- [x] Every benchmark result must include the command, environment, manifest
  hash, raw output location, and pass/fail criteria.
- [x] Every failure report must preserve what failed before any repair.
- [x] Every metric must name the measurement source or say `not instrumented`.
- [x] Every parent/candidate comparison must reject manifest, cycle, or case-set
  mismatch before judging improvement.
- [ ] Every outreach artifact must be non-confidential unless IP review says
  otherwise.

## First Build Target

The next technical target is a hardened candidate-generation entry point that
cannot overwrite the parent checkpoint, requires an explicit candidate ID/output
path, records input/output hashes, and writes a result artifact against the same
frozen manifest as the parent baseline. That candidate result must pass the
comparison gate before any improvement claim is allowed.
