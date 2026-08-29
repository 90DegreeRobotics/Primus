# Plan - Codex Both-Repo Verification

**Date:** 2026-08-29 1041 CDT
**Status:** COMPLETE
**Repos:** `C:\Primus`, `C:\chronos2`
**Lane:** Codex / verification

## Goal

Check the current Codex work order across both tandem repos and close any
Codex-owned verification gaps found during the check.

## Files Read

- `C:\Primus\AGENTS.md`
- `C:\Primus\task_2026-08-29_forward-model-sprint.md`
- `C:\Primus\handoff_claude_2026-08-29_r2-lane-a-corpus-integration.md`
- `C:\Primus\CCF_Sovereign\audit_geometry_corpus.py`
- `C:\chronos2\AGENTS.md`
- `C:\chronos2\task_2026-08-29_forward-model-sprint.md`
- `C:\chronos2\handoff_claude_2026-08-29_r2-lane-a-corpus-integration.md`
- `C:\chronos2\crates\chronos_geometry_plan\tests\no_recipe_guard.rs`
- `C:\chronos2\crates\chronos_geometry_plan\tests\novelty_ratchet.rs`
- emitted metric JSON under `C:\chronos2\out\metric_separation\`

## Files To Edit

- `C:\chronos2\crates\chronos_geometry_plan\tests\no_recipe_guard.rs`
- `C:\chronos2\crates\chronos_vision\tests\metric_separation_audit.rs`
- paired plan and handoff files in both repos

## Ordered Steps

1. Verify repo cleanliness and current commits in both repos.
2. Run the Primus audit against the real `seed_777` emitted corpus.
3. Add the missing Chronos metric-separation audit over emitted metrics.
4. Extend the Chronos guard to watch `mesh_metrics.rs` as well as
   `program_sampler.rs`.
5. Run focused Python and Rust gates.
6. Pull/rebase, stage explicit pathspecs, commit, push, and prove both repos
   clean with `HEAD == origin/main`.

## Test Gate

```pwsh
cd C:\Primus\CCF_Sovereign
python audit_geometry_corpus.py --corpus C:\chronos2\out\geometry_corpus\seed_777\corpus.jsonl --manifest C:\chronos2\out\geometry_corpus\seed_777\manifest.json --splits C:\chronos2\out\geometry_corpus\seed_777\splits.json
python test_no_recipe_guard.py
python test_geometry_corpus.py

cd C:\chronos2
cargo test -p chronos_vision --test metric_separation_audit -- --nocapture
cargo test -p chronos_geometry_plan --test no_recipe_guard
cargo test -p chronos_geometry_plan --test novelty_ratchet -- --nocapture
rustfmt --edition 2021 --check crates\chronos_geometry_plan\tests\no_recipe_guard.rs
rustfmt --edition 2021 --check crates\chronos_vision\tests\metric_separation_audit.rs
```

## Rollback Path

If the new metric audit or guard extension fails and cannot be fixed inside
Codex-owned files, park with a blocked handoff and do not touch Lane A/B files.

## Next-Agent Pickup

The real 23-record corpus passes the Primus audit. The 600-sample run directory
exists but did not expose a completed manifest during this check, so it is not
the audited corpus.

## Completion Notes

All focused gates listed above passed. The Chronos2 package-wide
`cargo fmt --check` was attempted and rejected as a useful gate because it
reports broad unrelated formatting drift outside Codex-owned files; file-scoped
`rustfmt --check` passed on the two touched Rust files.
