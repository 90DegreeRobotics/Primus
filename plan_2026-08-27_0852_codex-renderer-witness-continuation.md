# Plan - Codex renderer witness continuation

**Created:** 2026-08-27 08:52 CDT
**Owner:** Codex, continuing after Manus renderer-witness block
**Repository:** `C:\Primus` / `main`
**Status:** EXECUTION COMPLETE - documentation closure pending

## Goal

Attempt the smallest safe local Blender renderer witness for one typed
WorldProgram. Preserve Manus's existing untracked plan, keep `C:\chronos2`
source read-only, avoid training/checkpoint/candidate mutation, and write only
isolated ignored evidence under `C:\Primus\CCF_Sovereign\tmp\` unless a tracked
handoff/plan update is required.

This is a renderer-observation attempt only. It must not be described as visual
correctness, physical dynamics, learned-world capability, or promotion evidence
unless those exact artifacts exist.

## Files To Read

- [x] `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
- [x] `AGENTS.md`
- [x] `README.md`
- [x] `STATUS.md`
- [x] `CCF_Sovereign\README.md`
- [x] `CCF_Sovereign\MVP_STATUS.md`
- [x] `CCF_Sovereign\requirements.txt`
- [x] `handoff_manus_2026-08-27_balanced-compiler-witness.md`
- [x] `plan_2026-08-27_0830_blender-renderer-witness.md`
- [x] Relevant Chronos2 Blender/MCP scripts and local Blender configuration

## Files To Edit Or Add

- [x] `plan_2026-08-27_0852_codex-renderer-witness-continuation.md`
- [x] `handoff_codex_2026-08-27_renderer-witness-continuation.md`

No source-code edits are planned. No `chronos2` source file is edited. Blender
user configuration may be inspected and, only if required for the local add-on,
modified by Blender/add-on enablement as an external application state.

## Ordered Steps

- [x] Inspect Blender executable availability and version.
- [x] Inspect `C:\chronos2\blender-mcp\addon.py` and any local startup/server
      instructions without modifying source.
- [x] Inspect existing Blender user add-on/config paths and record whether a
      prior configuration exists.
- [x] Locate one existing manifest-bound typed program suitable for rendering,
      preferring the recent balanced compiler witness source when available.
- [x] Create a fresh ignored evidence directory and verify it does not already
      exist.
- [x] Start/enable the local Blender MCP/add-on path only as needed.
- [x] Attempt one deterministic render/export to the evidence directory.
- [x] Hash every output artifact and record command/config/process evidence.
- [x] If blocked, preserve the exact blocker and do not manufacture observed
      render evidence.
- [x] Write a handoff with what ran, outputs, hashes, unrun items, and git state.

## Result

Native `chronos dreamer run-s3v` did not render; it failed before render because
`entity_actor` was missing from the Chronos asset registry. That blocker is
preserved in `CCF_Sovereign\tmp\codex_renderer_witness_20260827_0852\chronos_run_s3v.log`.

The fallback direct Blender witness succeeded through Blender 5.0 headless. It
rendered the selected manifest-bound S3V file to PNG and saved a `.blend` plus
metadata under `CCF_Sovereign\tmp\codex_renderer_witness_20260827_0852\direct_blender\`.
This proves only that Blender produced nonblank pixels from a typed S3V-derived
scene script. It does not prove native Chronos Dreamer integration, visual
correctness, physical dynamics, learned dynamics, or promotion eligibility.

## Test Gate

There is no Python source change planned. Verification is the real local command
or application evidence:

```powershell
git status --short --branch
Get-FileHash <evidence-files> -Algorithm SHA256
```

If any tracked file is staged for documentation closure:

```powershell
git diff --check --cached
```

## Rollback Path

Do not delete existing Blender config, source files, candidates, checkpoints,
or generated datasets. If add-on enablement creates Blender user-config changes,
record their paths and restore only if the exact touched files are known and
safe. Failed render attempts remain preserved as evidence in a fresh ignored
directory.

## Next-Agent Pickup Notes

The generated-transition learning path is already complete and pushed. The next
truth gap is renderer observation: the balanced compiler witness proved local
Chronos validation for 16/16 selected programs, but `render_observed=false`.
This continuation exists only to attempt that missing render witness.
