# Plan - Cross-Repo Manus Clean Handoff

## Goal

Give Manus the correct coordination surface from `C:\Primus`, because this work
currently spans two repositories: Primus produces the typed S3V/transition
evidence, and Chronos2 consumes it for native Dreamer witness work.

The outcome requirement is explicit: every worked file in every touched repo is
audited, committed, pushed to `main`, and both worktrees are empty at handoff.

## Starting State

- Primus repo: `C:\Primus`
- Primus branch: `main`
- Primus starting commit:
  `d8752ffc2524c31d99f7d75b5f0486504423db33`
- Primus starting state: clean, `HEAD == origin/main`
- Chronos2 repo: `C:\chronos2`
- Chronos2 required clean-handoff plan:
  `C:\chronos2\plan_2026-08-28_1734_manus-native-witness-clean-handoff.md`
- Chronos2 latest known pushed clean-handoff commit:
  `d1081db00a986858d67b9ea90b96d3e4e581c091`

## Read First

In `C:\Primus`:

- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `plan_2026-08-28_1515_worktree-clean-handoff.md`
- `plan_2026-08-28_1515_typed-s3v-operation-emission.md`
- this plan

In `C:\chronos2`:

- `AGENTS.md`
- `CLAUDE.md`
- `docs\NEUROCOGNICA_BUILD_DOCTRINE.md`
- `plan_2026-08-28_1734_manus-native-witness-clean-handoff.md`
- `plan_2026-08-28_1657_native-extrude-face-witness.md`
- `handoff_codex_2026-08-28_native-extrude-face-witness-refresh.md`

## Scope

Manus may need to work in both repos, but must treat them as separate audit
surfaces:

- Primus owns evidence production, typed S3V emission, model/evaluation
  records, and transition contracts.
- Chronos2 owns native consumption, Dreamer/BlenderMCP execution, rendered
  artifacts, product truth surfaces, and Chronos evidence viewers.

Do not blur the evidence claim across repos. A Primus source/evaluation result
is not a Chronos native render. A Chronos native render is not Primus model
promotion or learned-world proof.

## Non-Negotiable Clean-Handoff Rule

If Manus touches a repo, Manus owns that repo's final state.

For every touched repo, all of these must be true before handoff:

1. `git status --short --branch` has no modified, deleted, staged, or untracked
   paths after the branch header.
2. `git rev-parse HEAD` equals `git rev-parse origin/main`.
3. Every edited or created source/doc/test file is committed and pushed to
   `origin main`.
4. Every local generated evidence directory is either ignored and named in the
   handoff, or converted into a committed pointer/receipt if the repo law
   requires it.
5. No scratch scripts, extraction helpers, reports, plans, handoffs, temp files,
   or review-source directories remain visible in `git status --short`.
6. No "formatter drift" or "other agent files" are left for Codex or Michael to
   interpret later. Audit them, commit them if they belong to the work, or stop
   and name the blocker.

Do not use `git add -A`. "All worktree files" means all audited worktree files
staged by explicit pathspec, not blind bulk staging.

## Required Start Commands

Run these before making or continuing changes:

```pwsh
git -C C:\Primus status --short --branch
git -C C:\Primus diff --stat
git -C C:\Primus rev-parse HEAD
git -C C:\Primus rev-parse origin/main

git -C C:\chronos2 status --short --branch
git -C C:\chronos2 diff --stat
git -C C:\chronos2 rev-parse HEAD
git -C C:\chronos2 rev-parse origin/main
```

If either repo is dirty at the start, identify every path before touching it.

## Native Witness Boundary

If the next task is the native `extrude_face` witness, follow the Chronos2 plan:

`C:\chronos2\plan_2026-08-28_1657_native-extrude-face-witness.md`

Before running Dreamer, pin:

- exact Primus-emitted typed S3V file path;
- S3V SHA-256;
- exact action id;
- exact `action.operation` payload;
- fresh Chronos2 run root;
- BlenderMCP endpoint availability.

If the exact S3V input cannot be located from Primus, stop and report the
blocker. Do not invent a synthetic replacement unless Michael explicitly
authorizes it and the handoff labels it synthetic.

## Verification Gate

Use the smallest gate that proves the touched surface in each repo. At minimum,
before commit in each touched repo:

```pwsh
git diff --check
git add -- <explicit audited paths>
git diff --check --cached
```

If Primus source/tests are touched, run the focused Primus tests named by the
local plan.

If Chronos2 source/tests are touched, run the focused Chronos2 tests named by
the local plan, and include `cargo check -p chronos_cli` for Dreamer/CLI paths.

If a native render witness is run, record exact commands, stdout/stderr summary,
artifact paths, hashes, pixel/visual inspection result, and all non-claims.

## Mandatory End Commands

Run these after final push:

```pwsh
git -C C:\Primus status --short --branch
git -C C:\Primus rev-parse HEAD
git -C C:\Primus rev-parse origin/main

git -C C:\chronos2 status --short --branch
git -C C:\chronos2 rev-parse HEAD
git -C C:\chronos2 rev-parse origin/main
```

Expected ending for both touched repos:

```text
## main
```

or, if the repo tracks upstream in the status line:

```text
## main...origin/main
```

with no paths listed underneath, and matching `HEAD` / `origin/main` hashes.

## Final Handoff Must State

- Which repo or repos were touched.
- Starting and final commit for each touched repo.
- Exact file list worked.
- Exact commands run.
- Exact test/build/witness results.
- Exact local evidence paths and hashes.
- What was not run.
- What remains local-only or blocked.
- Final clean status and `HEAD == origin/main` proof for each touched repo.

## Stop Conditions

Stop and ask Michael instead of improvising if:

- cleanup would require deleting or resetting files;
- a repo has unrelated dirty work that cannot be attributed;
- exact S3V input cannot be found;
- BlenderMCP is unavailable;
- a witness fails and source fixes are needed;
- a generated artifact should be committed but is large/private/ignored by
  policy.

## Next-Agent Pickup Notes

The active lane is two-repo work. Parked location does not define the whole
scope. If Manus is in `C:\Primus`, he must still verify `C:\chronos2` before
and after Chronos work. If Manus switches to `C:\chronos2`, he must still verify
`C:\Primus` before and after Primus evidence work.

No repo should be left as a puzzle for the next agent.
