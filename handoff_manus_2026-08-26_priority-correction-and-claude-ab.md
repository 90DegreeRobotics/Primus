# Handoff — Primus priority correction and chunked-scan A/B closure

**Date:** 2026-08-26
**Prepared by:** Manus AI
**Operator:** Michael Holt, NeuroCognica
**Repository:** `C:\primus`
**Branch law:** `main` only; push completed work to `origin/main`
**Status:** Documentation handoff; no model promotion is authorized or implied

## 1. Read this first

Before substantive work, load and obey these files in order:

1. `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
2. `C:\primus\AGENTS.md`
3. `C:\primus\STATUS.md`
4. `C:\primus\CCF_Sovereign\README.md`
5. `C:\primus\plan_2026-08-26_1045_chunked-ladder-rerun.md`
6. `C:\primus\docs\provenance\PRIMUS_NAME_PROVENANCE_2026-08-26.md`
7. `C:\primus\docs\research\PRIMUS_THESIS_VALUE_AND_NOVELTY_2026-08-26.md`

> If the repository, a manifest, and this handoff disagree, inspect the committed evidence and executable path before making a claim. Do not infer capability from architecture, a training process, or a stale status field.

## 2. Michael Holt’s authorship and chronology

Michael explicitly clarified that **Primus is his idea** and provided a Google Drive screenshot plus a PDF export of `Full Report: The First Emergence - NeuroCognica Primus`.

The repository now preserves the evidence chain in:

- `docs/provenance/PRIMUS_NAME_PROVENANCE_2026-08-26.md`
- `docs/provenance/evidence/2025-06-11_Full_Report_The_First_Emergence_NeuroCognica_Primus.pdf`

The sealed PDF SHA-256 is:

```text
0cbdcd0c2dead1c4f0f5352a50f5ae0beb81412ee400bf59be84471cb5f5720a
```

The strongest dated evidence is the Google Docs server-side **Modified** date of **2025-06-11**. The unrelated OpenCog/SingularityNET PRIMUS world-model publication is dated **2025-12-27**. The correct repository position is therefore:

> **Michael Holt and NeuroCognica independently conceived and documented Primus at least by 2025-06-11. The later external PRIMUS publication is relevant prior art and creates a naming issue; it is not evidence that NeuroCognica derived Primus from that work or that the idea originated there.**

This evidence record is not a patentability, inventorship, ownership, or trademark opinion. Preserve that legal boundary.

The novelty report was corrected to state this explicitly. The correction commit is `d5299868b8455d806fe771337452dd6305a66b45`.

## 3. Claude’s completed chunked-scan A/B test

Claude’s final committed record is:

- `plan_2026-08-26_1045_chunked-ladder-rerun.md`
- final closure commit: `145f85a` — `docs(ccf): close the A/B - 150m fits memory but does not converge`
- in-flight finding commit: `b53090c`
- provenance commit: `fdaff6d`

The 150M probe used **155,347,584 parameters** at the same model configuration that had previously OOMed after one step under the old full-state scan. The final measurements were:

| Signal | Recorded result |
|---|---:|
| Runtime before deliberate stop | 6.39 hours |
| Steps completed | 85 of 300 |
| Peak memory | approximately 12.08 GB |
| Throughput | 0.95 tokens/s |
| Step time | 271 seconds |
| Projected full run | 22.6 hours |
| Mean loss | 112.93 |
| Random baseline | `ln(2048) = 7.62` |

The defensible conclusion is:

> **The chunked scan removed the old practical memory ceiling for this 150M configuration, but the configuration is not training-viable.**

Loss remained roughly fifteen times worse than random and flat across steps 2–85. Claude’s final plan identifies an optimization or initialization defect at depth 30; learning rate `3e-4` with no warmup is the leading suspect. This is not evidence that the world-model thesis failed, and it is not evidence that the 150M candidate learned anything useful.

## 4. Protected parent and candidate integrity

The protected parent checkpoint remained byte-identical throughout monitoring:

```text
CCF_Sovereign/checkpoints/primus_council_trained.pt
SHA-256: 5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b
```

No candidate was promoted. No active ladder process remained at final audit.

Some ignored candidate manifests may still say `training` after their process has exited, including the dedicated A/B 150M candidate. Treat those fields as **stale lifecycle evidence**, not as evidence that a run is active. Do not edit or reconcile ignored manifests casually; first inspect the candidate-safety contract and preserve the original evidence.

## 5. What this Manus instance changed

The only intended tracked correction from the final lane is:

- `docs/research/PRIMUS_THESIS_VALUE_AND_NOVELTY_2026-08-26.md`
- this handoff file

The novelty report now:

- names Michael Holt and NeuroCognica as the independent source of the assessed Primus architecture;
- cites the sealed 2025-06-11 provenance ledger and PDF;
- distinguishes later prior art from origin or derivation;
- retains patent and trademark caveats;
- does not claim that the current checkpoint demonstrates the thesis.

No model source, checkpoint, training corpus, candidate manifest, runtime evidence file, or ChronoSophia source file was intentionally changed by this lane.

## 6. Existing world-core work that remains important

The August 26 world-core implementation landed before Claude’s A/B test:

- `e2378fe` — typed world-state schema, lossless S³V bridge, chunked selective scan, tests, and evidence summary
- `b2b138f` — completed day-one execution ledger

Important truth boundaries remain:

- The typed world schema is tested as a representation and compiler bridge.
- It is **not yet wired into model training or runtime prediction**.
- The protected parent was trained on a small conversation-derived corpus and scored `0/3` on its first protected live baseline.
- The scaling ladders measured execution feasibility, memory, throughput, and optimization behavior; they did not prove reasoning, continual learning, learned world dynamics, or a product-live world-builder.
- The next valuable training experiment is grounded world-trajectory learning, not another transcript-only scaling run.

## 7. Recommended next technical sequence

1. **Reconcile optimization before scale.** Re-run a bounded 150M diagnostic with warmup, lower learning rate, gradient and activation statistics, and depth ablations. Keep it candidate-isolated and stop early if loss does not cross the random baseline.
2. **Prefer the 50M-class core for grounded experiments.** It is materially cheaper and already fits the target machine with room for data and instrumentation.
3. **Wire the typed world program into the objective.** Train on state transitions, cameras, entities, relations, geometry, evidence, uncertainty, and action-conditioned outcomes rather than prompt-response prose alone.
4. **Use whole-family holdouts and structural program signatures.** Do not let generator templates substitute for generalization.
5. **Preserve evidence-versus-inference labels.** A surface or relation must retain whether it was observed, geometrically supported, or generatively completed.
6. **Keep promotion separate.** No candidate becomes the parent without protected evaluation, explicit evidence, and the repository’s promotion contract.
7. **Review naming and intellectual-property strategy professionally.** The chronology evidence supports earlier independent conception; formal patent and trademark conclusions require qualified counsel.

## 8. Verification commands

Run from `C:\primus`:

```powershell
git status --short --branch
git log -8 --oneline
git diff --check
git rev-parse HEAD
git rev-parse origin/main
Get-FileHash CCF_Sovereign\checkpoints\primus_council_trained.pt -Algorithm SHA256
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'ladder-(ab|chunked).*20260826' } |
  Select-Object ProcessId, CreationDate, CommandLine
```

For the authorship evidence:

```powershell
Get-FileHash docs\provenance\evidence\2025-06-11_Full_Report_The_First_Emergence_NeuroCognica_Primus.pdf -Algorithm SHA256
Select-String -Path docs\research\PRIMUS_THESIS_VALUE_AND_NOVELTY_2026-08-26.md `
  -Pattern 'Authorship and chronology|not evidence of origin or derivation|\[27\]:|\[28\]:'
```

## 9. Final repository state expected after this handoff lands

| Field | Expected state |
|---|---|
| Branch | `main` |
| Local versus remote | synchronized with `origin/main` |
| Working tree | clean |
| Protected parent hash | `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b` |
| Active ladder processes | none |
| Candidate promotion | none |
| Novelty-report correction | committed and pushed |
| This handoff | committed and pushed |

## 10. Do not overclaim

Do not say that Primus has demonstrated consciousness, AGI, stable continual learning, learned world dynamics, or general world-building. Do not say the 150M probe trained successfully: it fit memory and executed, but its loss failed catastrophically. Do not say later prior art is the origin of Primus. Do not convert Michael’s chronology evidence into a legal conclusion.

The accurate summary is narrower and stronger:

> **Primus is Michael Holt and NeuroCognica’s independently conceived, evidence-first sovereign world-model research program. Its current repository contains substantive proprietary engineering and a falsifiable research architecture. The central learned-world thesis remains unproven, and the next work must test it directly with grounded trajectories and controlled ablations.**
