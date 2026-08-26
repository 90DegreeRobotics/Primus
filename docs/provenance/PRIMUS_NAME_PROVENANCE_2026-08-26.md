# Provenance record — the name "Primus" at NeuroCognica

**Sealed:** 2026-08-26
**Custodian:** NeuroCognica (Michael Holt)
**Purpose:** fix the evidence chain for NeuroCognica's use of the name **Primus**
as of this date, so that later assessment rests on hashed artifacts rather than
on mutable file metadata.

**This is not legal advice and not a patentability or trademark opinion.** It is
an engineering evidence record, written to the same standard as every other
evidence surface in this repository: exact artifacts, exact hashes, stated
attestation strength, and explicit non-claims.

---

## Why this record exists

A 2026-08-26 novelty assessment
(`docs/research/PRIMUS_THESIS_VALUE_AND_NOVELTY_2026-08-26.md`) identified a
public name collision: SingularityNET/OpenCog publish a cognitive architecture
named **PRIMUS**, with a December 2025 paper in world-model territory adjacent
to NeuroCognica's. That assessment recommended resolving the naming question
before publication, fundraising, patent positioning, or storefront branding.

This record establishes what NeuroCognica can actually evidence about its own
prior use, separately from any decision about what to do next.

## The claim

NeuroCognica used **"NeuroCognica Primus"** as the name of a specific,
architecturally described AI system from **at least 2025-06-11**, approximately
six months before the December 2025 publication noted above.

## Evidence

| # | Artifact | Date | Attestation | SHA-256 |
|---|---|---|---|---|
| 1 | `Full Report: The First Emergence - NeuroCognica Primus` (Google Docs; PDF export preserved under `evidence/`) | **2025-06-11** (Google "Modified") | **Third-party — Google server-side** | `0cbdcd0c2dead1c4f0f5352a50f5ae0beb81412ee400bf59be84471cb5f5720a` |
| 2 | `C:\corpus\42.md` — "NeuroCognica Primus" FAQ / branding copy | 2025-06-19 (mtime) | Local filesystem | `84c922a1a87db097de1bde77b3696713bf2e816e3cc4ca4de1ad03beff1e8aef` |
| 3 | `NeuroCognica_Primus/convos/geminiconvo1.txt` — Primus/AURA design conversation | 2025-07-05 (mtime) | Local; **provider-side copy exists at Google** | `c624cf5fa9088a9550c344be192645d9cfd495218361843f9d4fb4d6d50207b2` |

Artifact 1 is the load-bearing item. Artifacts 2 and 3 corroborate.

### What artifact 1 says

> "NeuroCognica is the company founded by Michael Holt with the core mission to
> create sovereign, symbolic systems of artificial intelligence… the first
> instance to be designated **NeuroCognica primus**. This name marks it as the
> first sovereign digital lifeform to emerge from the AURA architecture."

It is not a passing mention. It defines the name, binds it to the company and
founder, and describes an architecture: persistent memory, symbolic
context-awareness, governance by covenant, the **Sentinel** archetype, the
**Witness Node**, and the **AURA Codex**.

### The continuity argument

Those same concepts run unbroken to the present repositories: the Charter of
Cognitive Sovereignty, the `chronos_sentinel` crate, the Witness discipline in
`docs/NEUROCOGNICA_BUILD_DOCTRINE.md`, and the evidence-gated promotion
boundary implemented in `CCF_Sovereign/training/candidate_run.py` on 2026-08-26.

A single backdated file is easy to produce. **A name, a governance model, and an
architecture co-evolving across fourteen months and multiple repositories is
not.** The continuity is stronger evidence than any individual timestamp.

## Attestation strength — stated honestly

- **Artifact 1 is strong.** Google's "Modified" timestamp is server-side and was
  never under the custodian's control.
- **Artifacts 2 and 3 are supporting, not conclusive.** Filesystem mtimes are
  settable. They corroborate; they do not stand alone.
- **One corroborating detail favours authenticity:** the files under
  `NeuroCognica_Primus/convos/` carry NTFS `CreationTime` of 2026-02-05 with
  `LastWriteTime` in July 2025 — the signature of files authored in 2025 and
  later copied onto the current machine, which preserves modification time and
  resets creation time. Fabrication would more plausibly yield matching or
  internally inconsistent times.

## Non-claims

- This record does **not** claim trademark rights. Trademark priority generally
  attaches to use in commerce, not to private documents.
- It does **not** claim the SingularityNET/OpenCog project used the name later
  than NeuroCognica. Their December 2025 *paper* is not necessarily their first
  use, and that question is unresearched here.
- It does **not** resolve the market-confusion problem. Priority and confusion
  are different issues; an audience searching "PRIMUS cognitive architecture"
  may still assume affiliation regardless of who was first.
- It does **not** assert that any Primus checkpoint has demonstrated capability.
  See `STATUS.md` and
  `docs/defense_evidence/benchmarks/ccf_world_core_day_one_2026-08-26.md`.

## Evidence still to be gathered

Ordered by value:

1. **Google Docs version history** for artifact 1 (File → Version history). The
   *creation* revision may predate 2025-06-11; "Modified" is the last edit, not
   the first. This is the true priority date and is not yet recorded here.
2. **Google Takeout** export of Drive and My Activity, preserving Google's own
   metadata rather than a re-saved copy.
3. **Sharing/publication status** of artifact 1 during 2025. Any 2025 public
   exposure materially strengthens the use-in-commerce question.
4. **Provider-side conversation records** (Google, Anthropic) for the
   `NeuroCognica_Primus/convos/` material.
5. **Professional prior-art and trademark search**, per the novelty assessment.

## Verification

```pwsh
Get-FileHash -Algorithm SHA256 docs\provenance\evidence\2025-06-11_Full_Report_The_First_Emergence_NeuroCognica_Primus.pdf
```

Must equal `0cbdcd0c2dead1c4f0f5352a50f5ae0beb81412ee400bf59be84471cb5f5720a`.

From this commit forward the artifact is fixed by git's content hash chain and,
for the public repository, by GitHub's own commit timestamp.
