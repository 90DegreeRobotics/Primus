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
- [ ] First real shadow-cycle manifest generated from live artifacts.
- [ ] First live parent baseline run against a real parent artifact.
- [ ] First parent/candidate benchmark run.
- [ ] First raw failure report.
- [ ] First retention/forgetting measurement.
- [ ] First latency/resource measurement.
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

- [ ] Every manifest must name parent artifact, training inputs, benchmark cases,
  and hashes where files exist.
- [ ] Every benchmark result must include the command, environment, manifest
  hash, raw output location, and pass/fail criteria.
- [ ] Every failure report must preserve what failed before any repair.
- [ ] Every metric must name the measurement source or say `not instrumented`.
- [ ] Every outreach artifact must be non-confidential unless IP review says
  otherwise.

## First Build Target

The next technical target is a live shadow manifest using a real local parent
artifact and outreach-safe benchmark cases, followed by a no-training parent
baseline against that same parent artifact. That still will not prove
autonomous learning. It will prove that the evidence pipeline can start
recording the right facts against real artifacts instead of only unit-test
fixtures.
