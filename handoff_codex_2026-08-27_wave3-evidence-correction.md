# Handoff - Wave 3 evidence correction

**Date:** 2026-08-27
**Prepared by:** Codex
**Repository:** `C:\Primus`
**Branch:** `main`

## What changed

Applied the audit correction to the Wave 3 documentation-only evidence record.
The Wave 3 50M diagnostic now states the 100-step result beside the August 26
3,940-step 50M ladder result so the step-100 loss cannot be misread as a
regression or replacement of the full-ladder finding.

The stale lifecycle-manifest wording now records two preserved stale manifests:

- `ladder-ab-150m-20260826-150m`
- `ladder-chunked-20260826b-15m`

## Files touched

- `plan_2026-08-27_0702_wave3-evidence-correction.md`
- `plan_2026-08-27_0641_wave3-50m-candidate.md`
- `handoff_manus_2026-08-27_wave3-50m-candidate.md`
- `handoff_codex_2026-08-27_wave3-evidence-correction.md`

## Evidence checked

- Wave 3 manifest: `status=completed`, `max_steps=100`, 53,932,160 parameters,
  `D=640`, `L=20`, batch 1, sequence 256.
- Wave 3 runtime log: losses 574.5605 at step 1, 26.3873 at step 50, and
  17.1370 at step 100.
- `STATUS.md`: August 26 50M ladder ran 3,940 steps, mean loss 6.84, throughput
  308.84 tokens/s.
- Candidate inventory: exactly these two checked manifests still reported
  `status=training` among the stale lifecycle records named above.

## What was not changed

No source code, checkpoints, candidate manifests, runtime logs, local evidence
artifacts, or truth surfaces were modified. The stale manifests were preserved
untouched.

## Gate

Documentation-only gate:

```powershell
python tmp\manus_audit_markdown.py plan_2026-08-27_0641_wave3-50m-candidate.md handoff_manus_2026-08-27_wave3-50m-candidate.md --require-regex "not a world-model|not world-model|not.*world-model" --require-regex "No promotion|no promotion|non-promotion" --forbid-regex "\bTODO\b|\bPLACEHOLDER\b"
git diff --check --cached
```

## Remaining boundary

Wave 3 remains a hardware and harness diagnostic on the Council corpus. It is
not a learned-world result, not a Stage 2 world-data training run, not a
promotion-eligible candidate, and not a product-capability result.
