# Primus world core — day one, unattended

**Written:** 2026-08-26 06:05 · **For:** Manus (IDE, direct disk access, local GPU)
**Repo:** `C:\primus`, branch `main`, one branch only
**Operator:** away at work. Do not wait on him. Do not stop and ask unless a
STOP condition below is hit.

---

## Read this part first

You have four workstreams. Three are safe to land on `main` today. One has a
hard prerequisite that will **permanently destroy 1.78 GB of unrecoverable work**
if you get the order wrong.

> **THE HAZARD.** `CCF_Sovereign/train.py:224` hardcodes its output path to
> `checkpoints/primus_council_trained.pt` — the frozen parent. Every training
> run overwrites it. `.gitignore` excludes `*.pt` and `checkpoints/`, so **git
> cannot restore it.** There is no remote copy.
>
> **Workstream A must land before you run ANY training.** Not "should." Must.

A verified archive was taken before this brief was written:

```
CCF_Sovereign/checkpoints/frozen/parent_5e36cc9a_2026-08-26.pt
sha256 5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b
```

That is a second line of defence, **not permission to be careless.** Never write
into `checkpoints/frozen/`.

---

## The rules you are operating under

Read `C:\primus\AGENTS.md` in full before your first edit. You have disk access,
so also read the Charter it points at:
`C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`. Where anything here
conflicts with the Charter, the Charter wins and you must say so.

The non-negotiables that most often get broken by an autonomous agent:

1. **`main` only.** No feature branches, no worktrees.
2. **`git add -A` is banned** (§1.7). Explicit pathspecs, every time. The tree
   may contain other builders' in-flight work — it did this morning.
3. **Never force-push, rebase pushed commits, `reset --hard`, or amend after
   push.**
4. **Never delete anything** without per-item operator approval. Not files, not
   branches, not "stale-looking" output. Preserve first.
5. **Never commit broken code.** Run the stated gate before every commit.
6. **Never present a stub as real.** Terminal-green is not product-green.
7. **Plan first.** `plan_<YYYY-MM-DD_HHMM>_<topic>.md` in the repo root before
   editing files, running commands, or changing git state.
8. Commit as `NeuroCognica <holtmichael1@gmail.com>`, Conventional Commits,
   subject ≤72 chars.

**Environment:** use system Python (3.12.10, torch 2.5.1+cu121, CUDA True). The
bundled `CCF_Sovereign/venv` is a Linux-layout tree and does not work on this
host. `transformers` is NOT installed — the tokenizer falls back to
character-level. Do not install it without asking; the fallback is fine for
today and is arguably what we want (see D).

---

## Context: what we are building and why today looks like this

Full plan: `C:\chronos2\plan_2026-08-26_0531_primus-world-core.md`. Read it.

Short version. The Primus checkpoint is 446M parameters, of which **411.7M
(92.3%) is a GPT-2 vocabulary coat** — a 50,257-token embedding plus an untied
head at dim 4096. The actual Mamba backbone is **~17.7M parameters**, trained on
**780k tokens**. It scored 0/3 on its first protected benchmark. It did not fail
because the architecture is wrong; it failed because ~96% of the capacity was
spent on a language the world core does not need to speak.

The fix is a typed world vocabulary (~4k symbols) and a backbone that dominates
the parameter count. That is Workstream B.

**There is no world-core training data yet.** So today's GPU work is not "train
the model." It is: make training *safe* (A), design the thing that makes data
possible (B), remove the throughput ceiling (C), and **measure the numbers the
plan currently only estimates** (D).

---

## Workstream A — candidate isolation (DO THIS FIRST, blocks D)

**Problem:** `train.py` writes over the frozen parent. This is the blocker
recorded in `handoff_codex_2026-07-27_candidate-generation-audit.md`.

**Deliver:**
- Training writes to an isolated per-candidate destination, never the parent.
- Parent checkpoint + corpus manifest frozen and hashed; a run refuses to start
  if the parent hash has changed.
- Each run emits a manifest: config, data hash, seed, code commit, metrics,
  output path.
- Promotion is a separate, explicit, atomic step — never a side effect of
  training.
- A regression test that **fails** if a training run can write the parent path.

**Gate:** `python -m compileall -q <touched>` and `python test_mvp.py` (6 tests,
must stay OK). Plus your new regression test.

**Then push.** Nothing else in this brief may run training until this is on
`main`.

---

## Workstream B — the typed world schema (highest value, no GPU)

This is the hard problem and the one that gates everything downstream. It is
design work; it does not compete with the GPU workstreams, so run it in parallel.

**Deliver a design document plus a round-trippable implementation:**
- Token schema for world state and actions: entity ids, relation types
  (part-of, attached-to, supports, occludes, constrained-by), op types,
  quantized transforms / materials / cameras, evidence bindings, uncertainty.
- Ground it in what exists: `C:\chronos2\crates\chronos_s3v`,
  `chronos_geometry_plan`, `chronos_lexicon` (atoms/verbs/recipes), and
  `C:\chronos2\data\capability_ledger.json`. **Do not invent a vocabulary that
  the existing compiler cannot express.**
- **Round-trip test: schema → S³V → schema, lossless.** This is the gate.

**The failure mode you are designing against is not compute — it is generator
entropy.** If the eventual data generator's program space is small, the model
learns to invert the generator rather than learn dynamics, and it will look
excellent on validation while failing on anything unscripted. The mitigations
are schema decisions, so they belong to you, today:
- Measure **unique-program coverage**, not token count.
- Hold out **entire operation families and object classes**, never random samples.
- Make **"composes two operations it never saw together"** the pass criterion.

---

## Workstream C — replace the scan (big payoff, needs a real gate)

`CCF_Sovereign/src/substrate/mamba_custom.py` uses a Hillis-Steele parallel
prefix scan that materialises `h: (B, L, d_inner, d_state)` and **forces float32
for the whole SSM** (line ~322, "softplus and exp overflow in fp16").

Consequences: no bf16 tensor-core benefit in the dominant kernel, O(L log L)
full-tensor traffic on a 360 GB/s card, and at D=1024/L=2048/B=4 that state
tensor is **~1.07 GB per layer**.

**Deliver:** a chunked/associative scan that does not materialise the full
`(B,L,D,N)` state in fp32, keeping numerics stable (fp32 accumulate, bf16
elsewhere is fine).

**Do NOT `pip install mamba_ssm`.** The pure-PyTorch choice was a sovereignty
decision. Owning a correct chunked scan ourselves is more sovereign than
importing someone's kernel, not less. If you believe that trade is wrong, write
the argument down and leave it for the operator — do not make the call.

**Gate — this one is not optional.** A wrong scan silently corrupts every future
training run:
- A differential test against the existing implementation: random inputs, several
  shapes, `d_state` and `d_conv` values, batch and sequence lengths, asserting
  `allclose` within a stated tolerance.
- A gradient check (the backward path must match too).
- Only after both pass: a GPU benchmark reporting tokens/sec before vs after,
  and peak VRAM before vs after.

If the differential test does not pass, **do not land it.** Leave the branchless
work in place and report.

---

## Workstream D — the ladder and the real numbers (GPU, all day)

**Blocked until A is on `main`. Verify that first.**

The plan currently *estimates* 6–12 days for a Chinchilla-fed 163M run, from
3–6 effective TFLOP/s. Estimates are not allowed to schedule a multi-day run.
Your job is to replace them with measurements.

**Use the existing council corpus** (`training/training_data/council_turns.jsonl`,
845 turns / ~780k tokens). The goal is **not** a good model — it is a validated
harness and real hardware numbers.

**Configure it to resemble the future regime, not the current mistake:**
- Character-level (or a small BPE trained on the corpus) — vocab ~2–4k, not
  50,257.
- **Tie the LM head to the embedding.**
- No 4096→512 bottleneck; let the backbone dominate the parameter count.

**Run the ladder: ~5M, ~15M, ~50M, ~150M params on identical data.**

**Report, as a committed artifact:**
1. Loss vs parameters. Where is the knee?
2. **Measured tokens/sec at each size** — the number Correction 2 demands.
3. Peak VRAM at each size.
4. **The empirical ceiling: at what D / L / batch does the current scan OOM on
   12 GB?** This tells us how urgent C is.

**Interpretation warning:** 780k tokens against a 150M-param model is ~0.005
tokens/param. Every rung will overfit hard. **That is expected and is not a
finding.** You are validating the harness and measuring throughput. Do not
report the ladder's loss curve as evidence about model capability, and do not
promote anything.

---

## STOP conditions — surface, do not improvise

Stop and write a handoff rather than working around any of these:

- `test_mvp.py` fails and the cause is inherited code you did not write.
- The differential scan test fails and you cannot explain why.
- Anything wants you to delete, force-push, or rewrite history.
- You need to install a package, or you want to change a dependency.
- The parent checkpoint hash no longer matches `5e36cc9a…`.
- A workstream turns out to need a decision the operator has not made.

Do not "fix" inherited work to make a gate pass. Do not widen scope.

---

## Handing back

Update your plan docs as you go; mark `INTERRUPTED` with the first unfinished
step if you stop. At the end of the day leave one root handoff
`handoff_manus_2026-08-26_<topic>.md` stating, plainly:

- what landed on `main` and at which SHAs
- what was measured, with the actual numbers
- what failed, and what you did not attempt
- what the next agent should pick up first

**Report what is true, not what is tidy.** A day that produced four honest
measurements and no working model is a good day. A day that produced a
promoted checkpoint and a fabricated benchmark is the failure mode this whole
project exists to avoid.
