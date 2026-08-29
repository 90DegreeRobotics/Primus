# AGENTS.md

> **SUPREME LAW.** Above this SOP stands **The Charter of Cognitive
> Sovereignty**, the constitutional core of AURA, Sophia, Sentinel, Primus, and
> every NeuroCognica system. Load and obey
> `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md` before any substantive
> change. Jurisprudence lives in
> `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`. If this file or any instruction
> conflicts with the Charter, the Charter prevails and the agent must say so.

This file is the canonical operating procedure for AI and human contributors
working in the Primus repository. Every agent must read it before changing code,
docs, data, scripts, git state, or release surfaces.

Primus is being brought under git governance from a local working tree that
already contains prototypes, corpus exports, checkpoints, and research docs.
Coordination beats heroics. The job is repo truth: exact files, exact commands,
verified behavior, and no completion theater.

---

## 1. Non-negotiable rules

1. **Main only.** The only working branch is `main`. Do not create feature
   branches. Do not create or use git worktrees. If you find work in another
   branch or worktree, do not sweep it; surface it and assimilate only the
   verified work back to `main`.
2. **Origin is the audit surface.** The remote for this repo is
   `https://github.com/90DegreeRobotics/Primus.git`. Once a verified unit of
   work is complete, commit it on `main` and push `origin main`.
3. **Never force-push or rewrite shared history.** No `--force`, no
   `--force-with-lease`, no rebasing pushed commits, no `reset --hard`, no
   `commit --amend` after push.
4. **Never delete without explicit per-item operator approval.** No
   `git clean`, no bulk `Remove-Item`, no branch/worktree/file deletion because
   it "looks stale." Preserve first, ask when removal is needed.
5. **Never commit broken code.** Run the relevant gate before every commit. If a
   gate cannot be run, say so plainly and do not claim the change works.
6. **Never present a stub as real.** Stubs, mocks, placeholders, random-output
   demos, and unwired prototypes must be labeled as such, first and plainly.
   Terminal-green is not product-green.
7. **Never bulk-stage a shared tree.** Use explicit pathspecs. `git add -A` is
   banned here because this tree may contain active builder work, private corpus
   exports, large checkpoints, and generated artifacts.
8. **Docs are part of done.** Any change that alters behavior, entry points,
   training claims, artifact locations, or operator workflow must update the
   affected truth surfaces in the same unit of work.
9. **No recipe systems.** A lookup table of named things is not a capability.
   Do not add per-noun recipes, per-macro defaults, hardcoded parameter tables,
   or index-driven branches that stand in for a decision the system is supposed
   to make.
   - **The test:** ask "what decided this value?" If the honest answer is a
     literal, a counter, an index, a `variant` number, or a modulo of one, it is
     a recipe. Something must decide it from state, and must be capable of being
     measurably wrong.
   - Templates and fixed generators are permitted **only** as declared
     scaffolding. Label them as scaffolding in `STATUS.md`, and name the
     condition under which they get retired. Scaffolding without a stated
     retirement condition is a recipe wearing a lab coat.
   - A positive control on template data proves the learner can recover the
     template. Do not report it, extend it, or build on it as evidence of
     learned behavior. Run it once, record it, move on.
   - **The primary defence is a measurement on OUTPUTS, not a scan of source.**
     A source scan is evadable by construction: a table can move into data, a
     JSON seed file, a prompt template, or hardcoded magic-number profiles.
     What defines a recipe book is that **the number of distinct outputs is
     bounded by a table somebody maintains**. That is measurable, and it cannot
     be evaded by moving the table.
     The gate lives in `C:\chronos2` at
     `crates/chronos_geometry_plan/tests/novelty_ratchet.rs`. Measured
     2026-08-29: **200 compositional briefs produced 7 distinct programs**, and
     all 7 came from the modifier words, so the subject contributed nothing.
     It is a ratchet, not a red test, because a permanently-failing test gets
     switched off and then defends nothing. **Raise the floor when the system
     improves. Lowering it to make the test pass is a law violation, not a fix.**
   - A model may be called *learned* only when distinct outputs scale with
     distinct inputs instead of saturating, when it produces structures absent
     from its training set, and when perturbing one input changes the output
     continuously rather than switching branches. This is the same standard the
     BridgeData lane already meets and the geometry lane does not.
   - **Operator directive, 2026-08-29: the system will be able to learn or not
     exist.** A capability that cannot be learned does not get a lookup table as
     a consolation prize. It ships learned, or it does not ship.
   - This rule exists because the constraint was stated clearly in
     `C:\chronos2\plan_2026-08-15_2046_shape-thinking-not-recipes.md` and then
     lived only in that plan. Plans get marked COMPLETE and stop being read.
     Repo law does not.
10. **Tandem repos.** `C:\Primus` and `C:\chronos2` are one build in two
    repositories. Primus is the learner: frozen inputs, candidate lifecycle,
    declared baselines, structural holdouts, promotion governance. Chronos2 is
    the world: operation space, executor, renderer, scorer, sealed evidence.
    - Before starting work in either, read the current plan and handoff in
      **both**. A plan that exists in only one repo is not in effect.
    - Every plan document, handoff, truth-surface update, manual, and guide
      change lands in **both** repos in the same unit of work. Paired documents
      carry the same date-stamped filename.
    - If you touch a repo, you own its final state: audited, staged by explicit
      path, committed, pushed, and `HEAD == origin/main` with an empty
      `git status`.
    - Neither repo may claim a capability that depends on the other without
      naming the exact commit in the other that supplies it.

Violations of these rules have real cost: lost work, false confidence, broken
handoffs, and polluted repos. If finishing a task requires violating a rule,
stop and surface the conflict.

---

## 2. Read before you write

Before substantive work, read:

- `AGENTS.md` - this file, the repo-law surface.
- `README.md` - current repo purpose and operator-facing orientation.
- `STATUS.md` - current verified state and known boundaries.
- The latest root `plan_*.md` or `handoff_*.md`, if present.

For work under `CCF_Sovereign`, also read:

- `CCF_Sovereign\README.md`
- `CCF_Sovereign\MVP_STATUS.md`
- `CCF_Sovereign\requirements.txt`
- The specific source, training, test, and checkpoint files touched by the task.

For corpus or training-data work, inspect the source and destination paths before
running any parser, copy, sync, tokenizer, or training command.

---

## 3. Plan documents

Before editing files, running build/test/install commands, or changing git
state, create a dated root plan:

```text
plan_<YYYY-MM-DD_HHMM>_<short-topic>.md
```

The plan must include:

- goal
- files to read
- files to edit
- ordered steps
- test gate
- rollback path
- next-agent pickup notes

Reading files, `git status`, `git diff`, and writing the plan itself do not
require a prior plan. If an active IDE or harness mode asks for plan-only work,
stop at the plan and wait for explicit operator authorization.

Update the plan as work completes. If interrupted, mark it `INTERRUPTED` and
name the first unfinished step.

---

## 4. Dirty tree protocol

This repo may be worked by more than one builder at once. Start every session
with:

```pwsh
git status --short --branch
git diff --stat
git ls-files --deleted
```

If there is no `.git` directory yet, establish git metadata before treating any
file as tracked.

When the tree is dirty:

- Identify what changed before touching it.
- Do not revert another agent's or the operator's work.
- Do not stage unrelated files.
- Do not import `venv`, `.venv`, checkpoints, private conversation exports,
  generated maps, logs, caches, or scratch output.
- Attribute inherited work honestly in the commit body or `Co-authored-by:`
  trailer.

If a file appears modified but the diff is empty, verify with blob hashes before
calling it real work.

---

## 5. Commit and push

Use Conventional Commit prefixes:

- `feat(<scope>): ...`
- `fix(<scope>): ...`
- `docs(<scope>): ...`
- `test(<scope>): ...`
- `chore(<scope>): ...`
- `refactor(<scope>): ...`

Keep the subject line at 72 characters or less. The body explains why. Use the
operator identity unless instructed otherwise:

```text
NeuroCognica <holtmichael1@gmail.com>
```

Push completed, verified work:

```pwsh
git push origin main
```

Never push branches unless the operator explicitly names one for a one-off
operation. The default is direct `main`.

---

## 6. Verification gates

Pick the smallest gate that actually proves the touched surface.

For governance/docs-only changes:

```pwsh
git diff --check --cached
```

For Python source changes:

```pwsh
python -m compileall -q <touched paths>
```

For `CCF_Sovereign` MVP component changes:

```pwsh
python test_mvp.py
```

For checkpoint or persona-quality claims:

```pwsh
python test_inference.py
```

For training-data parser changes:

```pwsh
python training\analyze_data.py
```

If a test script catches exceptions and still prints success, call that out as a
false-green risk. A test that never fails cannot certify the thing it names.

---

## 7. Storage and artifact hygiene

Large or private artifacts do not enter git by accident.

Keep these local unless the operator explicitly says otherwise:

- virtual environments
- model weights and checkpoints
- generated maps and tree dumps
- raw conversation exports
- training scratch and run outputs
- logs, caches, temp files, and process IDs

If an operation may write multi-GB output, declare the destination and expected
scale first. Prefer ignored local paths or named remote storage for corpus-scale
payloads. Do not make the operator workstation the silent archive of everything.

---

## 8. Truth surfaces

`README.md` and `STATUS.md` are the current Primus truth surfaces. Until a
dedicated capability map exists, `STATUS.md` must separate:

- live and verified
- wired but unverified
- local-only prototype
- stub/mock/placeholder
- blocked

Do not describe a capability as live, done, shipped, trained, or learned unless
the corresponding command, runtime path, artifact, or user-facing surface was
actually run and inspected in the current repo state.

---

## 9. Handoffs

For meaningful work, write a root handoff:

```text
handoff_<agent>_<YYYY-MM-DD>_<topic>.md
```

Include:

- what changed
- files touched
- commands run and real output summary
- what was not run
- what remains dirty or untracked
- next step

Do not delete handoffs. Archive by moving only when the repo has an archive
policy and the operator has not objected.

---

## 10. Done report contract

Every done report must answer:

- What changed.
- What was run, with real result.
- What was not run.
- What remains stubbed, local-only, blocked, dirty, or untracked.
- Exact git state: branch, commit, remote, push status.

If you did not run it, you do not get to say it works.
