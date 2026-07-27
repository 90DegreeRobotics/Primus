# Plan: complete SBIR plan - 2026-07-27 10:02

## Status
COMPLETED

## Goal
Turn the builder's `SBIR_plan.md` residue into a clean, repo-ready Markdown plan for the MDA26BZ04-NV006 neuromorphic hardware SBIR opportunity, with source confidence, proposal work products, immediate next actions, and no unsupported claims.

## Context
- Relevant areas: root docs, SBIR proposal planning, repo truth.
- Files read:
  - `AGENTS.md`
  - `README.md`
  - `STATUS.md`
  - `handoff_codex_2026-07-27_git-governance-seed.md`
  - `SBIR_plan.md`
  - `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
  - `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`
- Files to edit:
  - `SBIR_plan.md`
  - `STATUS.md`
  - this plan
  - optional handoff
- External sources checked:
  - `https://www.sbir.gov/topics/12804`
  - `https://www.defensesbirsttr.mil/SBIR-STTR/Opportunities/`
  - `https://www.sbir.gov/faq/all`
  - `https://www.bwcoconsulting.com/fod/mda26bz04-nv006`

## Audit Findings
- [x] Confirmed current git state before edits.
- [x] Confirmed `SBIR_plan.md` is untracked builder output.
- [x] Confirmed `SBIR_plan.md` is not repo-ready Markdown: it begins with Python, writes to `/mnt/data`, contains a `sandbox:` link, and includes chat-response text.
- [x] Confirmed official SBIR.gov topic page shows the topic as open, topic number `MDA26BZ04-NV006`, solicitation `26.BZ`, release date July 1, 2026, open date July 22, 2026, and due/close date August 19, 2026.
- [x] Confirmed SBIR.gov warns its topic copy may not be the latest and agency solicitation/DSIP controls final forms and rules.
- [x] Confirmed DoW/Defense SBIR page says proposals must be submitted through DSIP and proposers must review both broad BAA/CSO and component-specific instructions.
- [x] Confirmed SBIR FAQ states SBIR Phase I small business workshare is minimum two-thirds of the research/analytical effort.
- [x] Confirmed BW&CO is only a secondary source for `$314,000` Phase I amount and detailed Phase I/II/III topic reproduction.

## Steps

### Step 1 - Replace builder residue with clean Markdown
- [x] Action: Rewrite `SBIR_plan.md` as direct Markdown with no Python wrapper, no sandbox links, no `utm_source` query strings, and clear source-confidence labels.
- Files touched: `SBIR_plan.md`.
- Expected outcome: The plan is readable and commit-worthy.

### Step 2 - Complete proposal work products
- [x] Action: Add one-sentence innovation, mission problem, technical hypothesis, Phase I objectives, milestones, success criteria, risk table, Phase II path, Phase III path, team/partner needs, compliance gates, and budget placeholders.
- Files touched: `SBIR_plan.md`.
- Expected outcome: The document becomes an actionable proposal assembly plan rather than a loose opportunity note.

### Step 3 - Preserve hard truth boundaries
- [x] Action: Mark unverified administrative items as operator action, mark DSIP-only items as blocked until login/download, and avoid claiming Primus/CCF is neuromorphic hardware.
- Files touched: `SBIR_plan.md`, `STATUS.md`.
- Expected outcome: No false funding, eligibility, hardware, or integration claims.

### Step 4 - Verify document quality
- [x] Action: Search for builder residue and run the docs gate.
- Files touched: none expected after fixes.
- Expected outcome: No Python/sandbox/utm residue remains; `git diff --check` is clean.

### Step 5 - Commit and push scoped work
- [x] Action: Stage only explicit SBIR/doc paths, commit, push `origin main`, and verify `HEAD == origin/main`.
- Files touched: git metadata only.
- Expected outcome: Remote has the completed SBIR plan without importing unrelated local source/corpus artifacts.

## Test Gate
```pwsh
Select-String -Path SBIR_plan.md -Pattern 'from pathlib','/mnt/data','sandbox:','utm_source'
git diff --check --cached
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

## Rollback
Do not delete. If the SBIR plan needs correction, apply a follow-up patch to `SBIR_plan.md` and commit it on `main`.

## Next-Agent Pickup
If Status is `INTERRUPTED`, resume at the first unchecked step. Do not stage unrelated untracked local surfaces.
