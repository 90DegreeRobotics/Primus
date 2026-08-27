# Plan - Wave 3 evidence correction

**Created:** 2026-08-27 07:02 CDT
**Author:** Codex
**Status:** IN PROGRESS

## Goal

Apply the audit corrections for the Wave 3 50M documentation so the evidence
cannot be misread as a regression against the August 26 full 50M ladder run,
and so stale candidate lifecycle manifests are counted accurately.

## Files to read

- `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `plan_2026-08-27_0641_wave3-50m-candidate.md`
- `handoff_manus_2026-08-27_wave3-50m-candidate.md`
- `CCF_Sovereign\checkpoints\candidates\wave3-50m-20260827-0641-50m\run.manifest.json`
- `CCF_Sovereign\checkpoints\candidates\ladder-ab-150m-20260826-150m\run.manifest.json`
- `CCF_Sovereign\checkpoints\candidates\ladder-chunked-20260826b-15m\run.manifest.json`
- `CCF_Sovereign\tmp\manus_wave3_50m_20260827_0641.log`

## Files to edit

- `plan_2026-08-27_0641_wave3-50m-candidate.md`
- `handoff_manus_2026-08-27_wave3-50m-candidate.md`
- `handoff_codex_2026-08-27_wave3-evidence-correction.md`
- This plan file.

## Ordered steps

1. Verify repository status and sync state.
2. Verify Wave 3 loss/step evidence from the manifest and runtime log.
3. Verify the August 26 50M ladder comparison source from `STATUS.md`.
4. Verify stale candidate manifests and preserve them untouched.
5. Patch the Wave 3 plan and handoff with step-context and plural stale-manifest
   wording.
6. Run documentation gates.
7. Commit the documentation-only correction with explicit pathspecs.
8. Push `main` and verify `HEAD == origin/main`.

## Test gate

Docs-only:

```powershell
git diff --check --cached
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

If the local markdown audit helper is available and still applies, run it on
the edited Wave 3 plan and handoff.

## Rollback path

This is documentation-only. Roll back by a normal follow-up commit that restores
the previous wording. Do not reset, clean, or delete ignored candidate
artifacts.

## Next-agent pickup notes

The correction must not alter checkpoints, manifests, logs, or local run
artifacts. It should only make the evidence interpretation narrower and more
legible.
