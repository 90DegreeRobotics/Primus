# Plan — multi-lane build charter (Claude, Codex, Manus)

**Created:** 2026-08-26 21:44 -05:00
**Author:** Claude (Opus 5) — sole auditor and director
**Status:** ISSUED — awaiting operator authorization to commit/push
**Authority:** Operator directive, 2026-08-26. Subordinate to
`C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`, then `AGENTS.md`.
If this charter conflicts with either, they prevail and the lane must say so.

---

## 0. Verified baseline

Every lane starts from this state. Re-verify before your first commit; if any
row differs, STOP and report to the director.

| Signal | Verified value | Method |
|---|---|---|
| `HEAD` | `856df203dbb3adeff10e351eaee20f3ba8063166` | `git log -1` |
| `origin/main` | `856df203dbb3adeff10e351eaee20f3ba8063166` | `git ls-remote origin main` |
| Protected parent | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` | `sha256sum`, live + frozen |
| GPU | idle, 0%, 18 W | `nvidia-smi` |
| Newest `.pt` | 2026-08-26 10:54 (ladder candidate) | `find -printf` |
| Operator context doc | `vision_deep_dive.md` = `cc0b11dc…` | `sha256sum` — see §1.5, required reading |

Stage 2 verification (25/25 gates, bit-identical regeneration from seed, holdout
contract confirmed non-leaking from the data itself) is recorded in
`plan_2026-08-26_2042_verify-stage2-claims.md`.

**Hard boundary, restated:** Stage 2 is dataset infrastructure. It is not
learned-world capability. Compiler/render grounding, ingestion, held-out
learning, and promotion are all open.

---

## 1. The shared-tree constraint — read before anything else

`AGENTS.md` §1.1 forbids branches and forbids worktrees. All three lanes
therefore share **one working directory and one HEAD**. The consequences are
not negotiable:

- **File editing can be parallel** — only because lanes own disjoint paths.
- **Git state changes cannot be parallel.** Every add/commit/push/pull moves
  the tree under the other two lanes. All git operations serialize through the
  director (§5).
- **The GPU cannot be parallel.** One holder at a time, granted by the
  director (§5.2).

Do not work around this with a branch, a worktree, a clone, or a stash. All
four are forbidden or destructive here. If the constraint blocks you, surface
the conflict — that is `AGENTS.md` §1.

---

## 1.5 Constellation context — required reading

**Every lane reads `vision_deep_dive.md` before its first plan document.**
The operator has directed that it be read so lanes understand what they are
building inside. It is operator-provided context, not a foreign builder's file.

**Primus is one star in a constellation, not the whole system.** The vision is
unified and dates to May–June 2025: AURA OS and the Council of Seven plus the
Witness Node; the Mind Plane spatial interface; **RFTP/RDP**, the Reflective
Data Protocol; the Sentinel Protocol; Chronos-Sophia procedural geometry; the
6FR humanoid embodiment; the CCF Sovereign learning substrate; all under the
Charter of Cognitive Sovereignty.

Consequences that bind lane work:

- **Do not design as if Primus were the terminal system.** The typed world
  schema, the compiler/render witness, and the promotion gate are substrate for
  a larger architecture. Interfaces outlive this repo.
- **Sibling repositories are live, not archives.** `C:\chronos2`
  (Chronos-Sophia), `C:\Prism` (RFTP lattice), `C:\aura-lab`, `C:\6fr`,
  `C:\sentinel-core` and others are separate stars under active work by other
  builders. Lane path ownership in §3 does not extend into them. Read-only,
  and only where a lane's phase requires it.
- **The Charter is supreme** and it governs the whole constellation, not just
  this repo.

### Document status — this file is context, not evidence

Classified deliberately, applying the lesson that a truth surface was quoted as
fact and was false:

| May be used for | May **not** be used for |
|---|---|
| Understanding scope, intent, and how the pieces connect | Any dated provenance or priority claim |
| Knowing which sibling systems exist and are live | Any capability claim |
| Orientation before writing a plan | Citation in a truth surface, benchmark, or evidence doc |

`vision_deep_dive.md` is affirming narrative prose written to the operator, and
some of its dating rests on filesystem timestamps, which do not survive copying
and are weak provenance. **All priority and chronology claims cite
`docs/provenance/PRIMUS_NAME_PROVENANCE_2026-08-26.md` and its sealed PDF —
never this file.** The careful legal boundary in the novelty report stands
unchanged: evidence of independent prior conception, and explicitly not a
patentability, inventorship, ownership, or trademark opinion.

---

## 2. Lane assignment

| Lane | Owner | Phases | Why this owner |
|---|---|---|---|
| **A — Grounding** | **Claude** | 1 (Compiler + Render Witness) | Cross-repo into chronos2; holds the doc-truth, `check_reachability`, and `CREATE_TAB_WITNESS` context |
| **B — Learning path** | **Manus** | 2 (Ingestion) → 3 (Transition Metrics) | Wrote the typed schema and the Stage 2 generator; ingestion is the direct continuation |
| **C — Governance** | **Codex** | 6 (Promotion Gate), budget/parity harness for 4–5 | Demonstrated record: shadow-compare gate, candidate-generation audit, compliance registers |
| **D — Truth surfaces** | **Claude only** | 7 | Single writer on the highest-collision files |

**Serialized phases — no lane owns them outright:**

- **Phase 4 — Small candidate run.** Manus executes, Codex gate armed, Claude
  witnesses. Requires operator authorization.
- **Phase 5 — Ablation A–F.** Only after Phase 4 produces a real result.

**Declared conflict of interest.** The director owns a build lane (A). To
mitigate: **Lane A's gates are re-run by Codex before any Lane A commit.** The
director does not self-certify Lane A. Codex is instructed to refuse the commit
window if Lane A's gates do not reproduce.

---

## 3. Path ownership

A lane may edit **only** the paths it owns. Touching another lane's path is a
stop-and-report event, not a conflict to resolve.

**Lane A — Claude**

- `CCF_Sovereign/src/world_compile/**` (new)
- `CCF_Sovereign/compile_world_programs.py` (new)
- `CCF_Sovereign/test_world_compiler.py` (new)
- `docs/defense_evidence/grounding/**` (new)
- `C:\chronos2` — **read-only.** No write without per-item operator approval.

**Lane B — Manus**

- `CCF_Sovereign/src/world_data/**` (new)
- `CCF_Sovereign/src/world_metrics/**` (new)
- `CCF_Sovereign/test_world_ingestion.py` (new)
- `CCF_Sovereign/test_transition_metrics.py` (new)

**Lane C — Codex**

- `CCF_Sovereign/src/promotion/**` (new)
- `CCF_Sovereign/test_promotion_gate.py` (new)
- `CCF_Sovereign/test_budget_parity.py` (new)
- `docs/governance/**` (new)

**Per-lane own files** — dated and agent-named, so they cannot collide:

- `plan_<YYYY-MM-DD_HHMM>_<topic>.md`
- `handoff_<agent>_<YYYY-MM-DD>_<topic>.md`

**Director-only (Lane D). No other lane writes these:**

- `README.md`, `STATUS.md`
- `CCF_Sovereign/README.md`
- `CCF_Sovereign/docs/WORLD_SCHEMA_V1.md`
- `docs/defense_evidence/benchmarks/**`
- `AGENTS.md`

A lane needing a truth surface changed emits a **TRUTH-SURFACE REQUEST** block
in its handoff: exact file, exact proposed wording, and the artifact hash
backing the claim. The director merges it. Lanes do not edit these files.

**Read-only for every lane — read it, never edit it:**

- `vision_deep_dive.md` — operator context, required reading per §1.5

**Never touched by any lane without per-item operator approval:**

- `CCF_Sovereign/checkpoints/**` — parent and frozen archive
- Any foreign untracked file that appears mid-task (§4)
- Anything under `C:\chronos2`, `C:\Prism`, or any sibling repo in write mode

---

## 4. Dirty-worktree law — the director adjudicates alone

This section is the operator's explicit instruction and overrides any lane's
convenience.

**Claude is the sole auditor of working-tree state.** No other lane
adjudicates, cleans, or reconciles dirty state, for any reason.

**Banned for Lanes B and C, without exception:**

```text
git add -A        git add .          git commit -a
git stash         git clean          git reset
git checkout --   git restore        git revert
git rm            git mv             git rebase
git push --force  git push --force-with-lease
```

**Required behaviour on unexpected tree state.** If you find a modified or
untracked file you do not own — including one that appears mid-task — you must:

1. **Stop.** Do not edit, move, delete, stash, or stage it.
2. Record its path, size, mtime, and SHA-256.
3. Report to the director and wait.

Do not infer that a file is stale, orphaned, or safe to remove. Codex
demonstrated the correct handling at 20:57 by preserving untracked files it did
not own, untouched, and reporting them.

This cuts both ways: a file that looks like abandoned residue may be operator
material. `vision_deep_dive.md` was initially classified here as a foreign
builder's in-flight file and held at arm's length; the operator corrected that
— it is required reading (§1.5). **When in doubt, read and report. Never
assume, and never remove.**

**Deletion requires per-item operator approval routed through the director.**
Nothing is deleted because it looks stale (`AGENTS.md` §1.4).

**Staging is explicit-pathspec only.** Every commit names its files. Never
stage a directory glob you have not enumerated.

---

## 5. Serialization protocol

### 5.1 Commit window

Only one lane holds the commit window at a time.

1. Lane completes work and runs its own gates. All green.
2. Lane **requests a window** from the director with:
   - the exact pathspec list it intends to stage
   - full gate output — command and exit code, not a summary
   - its plan file, updated
3. **Director verifies independently:** re-runs the gates, confirms the
   pathspec touches only owned paths, confirms the parent hash is unchanged,
   confirms no foreign file is in the pathspec.
4. Director **grants** the window.
5. Lane commits with explicit pathspecs, then pushes `main`.
6. Lane reports the resulting SHA. Director records it.
7. Window closes.

**Non-fast-forward on push:** STOP and report. Do not pull with rebase, do not
force, do not merge. The director resolves.

### 5.2 GPU token

Exclusive. One holder. Granted by the director, for Phases 4 and 5 only.
Before granting, the director verifies the GPU is idle and that no `.pt` has
appeared outside the expected candidate path. The holder releases explicitly.
No lane starts a training or ladder process without the token.

---

## 6. Evidence law — applies to every lane

**Synthetic output is never labelled `observed`.** This is the operator's
explicit instruction and it is a global rule, not a Phase 1 rule.

| Label | Means | Example |
|---|---|---|
| `generated` | Produced synthetically by our own code | Stage 2 fixtures |
| `inferred` | Derived from other data by our own code | uncertainty estimates |
| `observed` | A real execution ran and its output was hashed | a renderer that genuinely produced pixels |

A compiler receipt is `observed` **only if the compiler actually ran**. A
render hash is `observed` **only if the renderer actually produced pixels**. A
fixture that merely *could* be rendered is `generated`, always.

**No capability claim reaches a truth surface without both** a runnable command
and a hashed artifact. `AGENTS.md` §1.6: a stub is labelled a stub, first and
plainly. Terminal-green is not product-green.

**Failure is evidence.** Every phase records its failure classes explicitly. A
phase that records only successes has not been tested.

---

## 7. Phase gates

Acceptance criteria, not suggestions.

**Phase 1 — Compiler + Render Witness (Lane A).** Compiler receipts; S3V
hashes; render hashes; enumerated failure classes; evidence labels correct per
§6. Prove Stage 2 `WorldProgram` fixtures compile and render. Do not call
synthetic output observed.

**Phase 2 — Dataset Ingestion (Lane B).** Learner-side loader for the
7.4K-token records. Manifest binding; train/eval split isolation; whole-family
holdouts preserved through the loader; segmentation; batching; overlap
rejection. The holdout contract verified in §0 must survive ingestion —
re-verify it downstream of the loader, **from the emitted batches, not from the
manifest**.

**Phase 3 — Transition Metrics (Lane B).** Action-conditioned next-state
prediction scoring. State accuracy; relation accuracy; operation accuracy;
uncertainty handling; compiler-validity. **Held-out object, held-out operation,
and held-out composition scored and reported separately** — never pooled into
one number.

**Phase 4 — Small Candidate Run (serialized).** 50M-class only. No 150M
attempt. Equal resource budgets; **no promotion by default**; parent/candidate
comparison; checkpoint hash guards armed; failure captured rather than
discarded. Requires Phases 2, 3, 6 green, plus operator authorization, plus the
GPU token.

**Phase 5 — Ablation A–F (serialized).** Only after ingestion and metrics are
real. Test whether each added mechanism **improves measured behaviour**, not
merely whether loss is lower. A mechanism that lowers loss without improving
held-out behaviour is reported as not justified.

**Phase 6 — Promotion Gate (Lane C).** **Build nothing automatic.** No
auto-promotion path is wired unless the operator explicitly authorizes it.
Tests only: hash-gated promotion; protected-task regression rejection;
new-error rejection; manifest parity; parent checkpoint immutability.

**Phase 7 — Truth Surface Update (Lane D, director).** After each verified
phase. Docs diff review plus the relevant code gates. No capability claim is
promoted unless the matching command and artifact actually exist.

---

## 8. Execution waves

```text
WAVE 1  (parallel, path-disjoint, starts on authorization)
  Lane A  Claude  Phase 1  compiler + render witness
  Lane B  Manus   Phase 2  dataset ingestion
  Lane C  Codex   Phase 6  promotion gate tests (no automation)

WAVE 2  (after Phase 2 green)
  Lane B  Manus   Phase 3  transition metrics
  Lane A  Claude  Phase 1  continues
  Lane C  Codex            budget/parity harness for Phase 4

WAVE 3  (serialized; GPU token; operator authorization required)
  Phase 4  50M candidate run — Manus executes, Codex gate armed,
           Claude witnesses

WAVE 4  (serialized; only after Phase 4 produces a real result)
  Phase 5  ablation A–F

CONTINUOUS
  Lane D  Claude  Phase 7  truth surfaces, after each verified phase
```

---

## 9. Per-lane obligations

Every lane, every unit of work:

0. Read `vision_deep_dive.md` (§1.5) before your first plan document, and the
   Charter at `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md` before any
   substantive change. Know which star you are building.
1. Write `plan_<YYYY-MM-DD_HHMM>_<topic>.md` **before** editing files, running
   build/test commands, or changing git state (`AGENTS.md` §3).
2. Commit the plan first — candidate training refuses a dirty repository.
3. Run gates before every commit. Never commit broken code (§1.5).
4. Request a commit window (§5.1). Do not self-commit.
5. Write `handoff_<agent>_<date>_<topic>.md` at the end, including any
   TRUTH-SURFACE REQUEST block.
6. Report failures plainly. No completion theatre. No stub presented as real.

---

## 10. Rollback path

This charter creates no code and mutates no state. Rollback is deletion of this
file on operator instruction. Each lane carries its own rollback path in its own
plan document.

## 11. Next-agent pickup notes

If the director is unavailable, **no lane inherits the commit window or the GPU
token.** Work continues in owned paths, uncommitted, until a director is
re-appointed by the operator. Do not self-authorize either token.

**Open at issue time:** two uncommitted plan files
(`plan_2026-08-26_2042_verify-stage2-claims.md`,
`plan_2026-08-26_2058_repo-sync.md`), this charter, and `vision_deep_dive.md`.

`vision_deep_dive.md` is untracked but is required reading for every lane
(§1.5). **Recommendation to the operator: commit it**, so it survives, is
visible to all three lanes, and carries a hash. It is read-only for lanes
either way. The director holds all four files; no lane stages any of them.
