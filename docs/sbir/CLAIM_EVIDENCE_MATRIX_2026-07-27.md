# SBIR Claim/Evidence Matrix - 2026-07-27

## Purpose

This matrix is the guardrail for proposal language on the MDA26BZ04-NV006
Neuromorphic Hardware SBIR pursuit. It separates current repo evidence from
proposal hypotheses and future work.

No proposal text should promote a claim unless its row below supports that
claim. When in doubt, downgrade the language.

## Classification Vocabulary

| Status | Meaning | Proposal Use |
| --- | --- | --- |
| `VERIFIED` | Checked against current repo files, recorded commands, or cited source register. | May be stated as current evidence, with scope limits. |
| `WEAK EVIDENCE` | Some command or artifact exists, but the proof is smoke-level, unscored, local-only, or known to have false-green risk. | May be described as preliminary evidence only. |
| `HYPOTHESIS` | Plausible technical thesis, not yet demonstrated in this repo. | May be framed as Phase I hypothesis or objective. |
| `FUTURE WORK` | Required task not yet performed. | May appear only as planned work, milestone, or deliverable. |
| `BLOCKED` | Requires operator, DSIP, administrative, partner, hardware, or external access not present in this repo. | Must stay on compliance/blocker lists until resolved. |
| `NO-GO` | Unsupported or contradicted by current evidence. | Must not appear as a proposal claim. |

## Proposal Language Rule

- Use present tense only for `VERIFIED` rows.
- Use "prototype", "smoke-tested", "source baseline", or "preliminary" for
  `WEAK EVIDENCE` rows.
- Use "Phase I will test", "Phase I will quantify", or "Phase I will produce"
  for `HYPOTHESIS` and `FUTURE WORK` rows.
- Do not use "sentient", "conscious hardware", "finished neuromorphic system",
  "flawless integration", "zero resistance", "hardware demonstrated", or
  "learned Council persona" unless a future audit adds direct evidence.

## Opportunity And Compliance Claims

| Claim | Status | Current Evidence | Missing Evidence | Proposed Phase I Proof / Next Gate |
| --- | --- | --- | --- | --- |
| MDA26BZ04-NV006 exists as a neuromorphic hardware topic. | `VERIFIED` | `SBIR_plan.md` records official SBIR.gov topic check on 2026-07-27; `docs/sbir/README.md` source register points to SBIR.gov topic page. | None for topic existence. | Preserve source link and date in proposal source register. |
| Topic status, release date, open date, and proposal cutoff are known from official public sources. | `VERIFIED` | `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` records SBIR.gov and DSIP evidence: release 2026-07-01, open 2026-07-22, proposal cutoff 2026-08-19 at 12:00 p.m. ET. | None for public-package date/cutoff facts. | Recheck DSIP package on submission day before final certification. |
| DSIP and MDA component instructions control final submission requirements. | `VERIFIED` | `SBIR_plan.md`, `docs/sbir/README.md`, and `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` preserve the control hierarchy and official PDF fingerprints. | None for public package access. | Use the compliance register as the proposal gate; recheck before submission. |
| Official DSIP package is accessible and fingerprinted. | `VERIFIED` | `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` records the BAA preface and MDA instructions URLs, byte counts, page counts, and SHA-256 hashes. | Local PDFs are temp-only, not committed. | Redownload from official URLs if content must be inspected again. |
| MDA Phase I amount is `$307,500` base or `$314,000` with TABA. | `VERIFIED` | `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` records the official MDA Release 4 component instruction language. | Actual DSIP Cost Volume and TABA decision. | Build budget only after company rates and TABA decision are known. |
| MDA Technical Volume limit and format are known. | `VERIFIED` | Compliance register records 15-page limit, 10-point minimum font, 8.5 x 11 inch paper, one-inch margins, consecutive pages, header requirements, and no locked/encrypted/active-media uploads. | Actual final Volume 2 page count. | Check generated proposal PDF after DSIP upload/export and reject if over 15 pages. |
| ITAR/EAR/CMMC language is known from the official package. | `VERIFIED` | Compliance register records DSIP `itar=true`, MDA export-control language, CMMC Level 1, DD Form 2345/evidence requirement, and foreign-national disclosure constraints. | Company/team-specific DD Form 2345 status, CMMC/SPRS completion, and foreign-national disclosures. | Complete operator/company readiness gates before submission. |
| Public Topic Q&A is fully reconciled. | `WEAK EVIDENCE` | Public Q&A endpoint returned `[]`, but DSIP topic metadata showed a nonzero topic question count. | Resolve discrepancy by checking DSIP UI/API again before submission. | Recheck Topic Q&A and update compliance register if answers appear. |
| Company is administratively ready to submit. | `BLOCKED` | `STATUS.md` and the compliance register list UEI, SAM, Company Registry, SBC Control ID, Login.gov, DSIP access, DD Form 2345, CMMC/SPRS, ownership/control, employee count, TABA, and corporate-official certification as unverified. | Operator/company records and DSIP access. | Complete administrative readiness checklist and archive non-sensitive proof. |

## Current Technical Evidence Claims

| Claim | Status | Current Evidence | Missing Evidence | Proposed Phase I Proof / Next Gate |
| --- | --- | --- | --- | --- |
| Primus repo is under git governance on `main` with origin at `90DegreeRobotics/Primus.git`. | `VERIFIED` | `README.md`, `AGENTS.md`, `STATUS.md`, and pushed commits establish branch/remote rules. | None for repo governance. | Keep direct-main commit/push workflow and explicit staging. |
| CCF first-party source is present in git. | `VERIFIED` | `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md` lists imported CCF source/docs/tests; commit `6bad02e` imported it. | No missing evidence for source presence. | Treat as source baseline, not product proof. |
| CCF Python source and scripts compile. | `VERIFIED` | Audit recorded `python -m compileall -q CCF_Sovereign\src CCF_Sovereign\training CCF_Sovereign\train.py CCF_Sovereign\test_mvp.py CCF_Sovereign\test_inference.py` exit code 0. | None for syntax compilation. | Re-run after Python changes. |
| CCF fail-hard component checks run. | `VERIFIED` | On 2026-07-27, `test_mvp.py` was replaced with six assertion-backed `unittest` checks. `python test_mvp.py` exited 0 and verified config sanity, tokenizer fallback, STEB high-surprise gating, deterministic HRR identity-key round trip, tiny substrate forward outputs, and AdamW fallback sleep consolidation. | Runtime/daemon witness, full-scale config test, scored benchmarks, and production readiness remain missing. | Keep using the hardened component test after source changes; add runtime and shadow-cycle benchmarks before broader claims. |
| CCF checkpoint loads and generates text locally. | `WEAK EVIDENCE` | Audit recorded `python test_inference.py` exit code 0 using ignored local checkpoint with CUDA. | Scored benchmark, stable prompts/outputs, checkpoint provenance, safe `torch.load` mode. | Create scored inference/persona benchmark and checkpoint manifest. |
| CCF has a verified learned Council persona. | `NO-GO` | Audit saw mixed output, corpus echo, topic drift, SQL fragment, box-drawing fragment, and no scored benchmark. | Direct scored persona benchmark with acceptance criteria. | Do not claim; propose benchmark as Phase I or internal hardening work. |
| CCF is product-live or product-ready. | `NO-GO` | `STATUS.md` says no product capability is marked live; audit says prototype only. | End-to-end runtime witness, robust tests, nonblocking service harness, failure behavior. | Do not claim; use "local prototype" only. |
| CCF demonstrates autonomous continual learning. | `NO-GO` | No training run, shadow cycle, or reliable sleep consolidation was executed. | Observed learning cycles with manifests, candidate outputs, benchmarks, and promotion/rejection records. | Phase I shadow-cycle proof. |
| CCF demonstrates reliable sleep consolidation. | `NO-GO` | Audit found blocking `input()` loop, placeholder GPU load, missing `galore-torch`, and no real Adam fallback despite message. | Nonblocking harness, real idle telemetry, consolidation test with STEB data, optimizer proof. | Build runtime harness and consolidation test before claiming. |
| Current repo contains a real training command and training code. | `WEAK EVIDENCE` | `CCF_Sovereign/train.py`, parser scripts, and requirements are imported. | No current training run; `training_data` is ignored/local; missing `galore-torch`; no manifest in git. | Run controlled training from frozen manifest and record output hashes. |
| Current repo contains a canonical checkpoint/candidate format. | `WEAK EVIDENCE` | `test_inference.py` loads an ignored `.pt` checkpoint with `model_state_dict`, `training_turns`, and `epochs` keys. | Checkpoint is not in git; no manifest; no candidate schema; no safe unpickle policy. | Define candidate/checkpoint manifest and hashing policy. |
| Root research documents support conceptual hardware mapping. | `WEAK EVIDENCE` | Root Markdown docs are imported as source notes. | Source claims not independently revalidated in this pass; some language is speculative. | Use as hypothesis context only; cite primary technical sources separately in proposal. |

## Proposal Technical Claims

| Claim | Status | Current Evidence | Missing Evidence | Proposed Phase I Proof / Next Gate |
| --- | --- | --- | --- | --- |
| NeuroCognica can propose an auditable continual-learning control layer for neuromorphic processors. | `HYPOTHESIS` | `SBIR_plan.md` defines the architecture story; CCF provides prototype source context; Charter/Annex define audit, authority, and memory doctrine. | No integrated shadow-learning loop yet. | Build and test shadow loop with frozen manifests, benchmark evidence, and rejection/promotion logs. |
| Separating wake acquisition from controlled consolidation can reduce silent regression. | `HYPOTHESIS` | CCF design docs and SBIR plan describe the lifecycle. | No controlled experiment comparing ordinary adaptation vs circadian lifecycle. | Run continual-learning control experiment and report retention/regression metrics. |
| Candidate states can be validated against protected prior capability before promotion. | `FUTURE WORK` | `SBIR_plan.md` defines this as Phase 2/4 work. | Parent/candidate benchmark harness, protected-task suite, atomic promotion mechanism. | Execute at least three complete shadow cycles. |
| Candidate promotion can be cryptographically bound to evidence. | `FUTURE WORK` | Charter/Annex and SBIR plan define provenance/Forever Law need. | No Forever Law event-chain integration verified in Primus path. | Implement and verify event-chain sealing for training/evaluation/promotion. |
| The software lifecycle can be translated into neuromorphic hardware requirements. | `HYPOTHESIS` | `SBIR_plan.md` defines translation study and hardware requirement categories. | No measured lifecycle data, no hardware partner input, no physical substrate decision. | Phase I translation study from measured software runs to substrate requirements. |
| Shadow-cycle manifest primitives exist. | `VERIFIED` | `CCF_Sovereign/src/evaluation/shadow_manifest.py` defines file evidence, benchmark cases, canonical manifest JSON, manifest SHA-256, and train/eval source-overlap warnings. `python test_shadow_manifest.py` exited 0. | No real shadow-cycle manifest from live artifacts; no parent/candidate runner; no benchmark scoring. | Generate first real manifest and build parent/candidate benchmark runner. |
| No-training parent baseline result writer exists. | `VERIFIED` | `CCF_Sovereign/src/evaluation/shadow_baseline.py` consumes a validated manifest and responder callable, records raw responses, response hashes, pass/fail expected-string checks, responder errors, aggregate counts, latency, manifest hash, and explicit no-mutation/no-promotion flags. `python test_shadow_baseline.py` exited 0. | No live run against the ignored local checkpoint or other real parent artifact; no candidate comparison; expected-string checks are a first scoring primitive, not a complete benchmark suite. | Run the first live parent baseline from a real manifest, then add parent/candidate comparison and richer metrics. |
| A substrate-independent neuromorphic emulator can model intended hardware behavior. | `FUTURE WORK` | `SBIR_plan.md` defines emulator scope. | No emulator exists in repo. | Build emulator with explicit time constants, energy/latency assumptions, and plasticity model. |
| The program can produce a TRL-6 roadmap. | `HYPOTHESIS` | `SBIR_plan.md` drafts roadmap structure and DTE package. | Official MDA instructions, partner/lab assumptions, measured Phase I data. | Produce MDA deliverable package after DSIP and technical evidence gates. |
| Phase II should demonstrate adaptive RF waveform generation on or with neuromorphic processing. | `FUTURE WORK` | `SBIR_plan.md` maps this to topic direction. | RF partner, waveform workload, neuromorphic substrate, representative RF test environment. | Add RF/waveform advisor or partner and define hardware-in-loop test concept. |

## Explicit No-Go Claims

| Claim | Status | Current Evidence | Missing Evidence | Proposed Phase I Proof / Next Gate |
| --- | --- | --- | --- | --- |
| NeuroCognica already demonstrates neuromorphic hardware. | `NO-GO` | `docs/sbir/README.md`, `SBIR_plan.md`, and CCF audit all say current software is not hardware. | Physical/hardware-in-loop witness does not exist. | Do not claim. Phase I may derive requirements and emulator; Phase II targets hardware. |
| Current stack already demonstrates adaptive RF waveform generation. | `NO-GO` | No RF waveform workload or test exists in current audit record. | RF workload, RF-contested test, measurements. | Future Phase II target only. |
| Primus/CCF is sentient or conscious. | `NO-GO` | Current evidence is source/smoke/inference only; CCF audit rejects sentience/persona overclaims. | Not a proposal-appropriate technical claim. | Avoid language. Use constitutional doctrine only as governance philosophy if relevant. |
| System has flawless integration or zero resistance cognition. | `NO-GO` | Root research docs contain such phrases, but audit classifies them as speculative source notes. | Direct engineering proof does not exist. | Remove from technical proposal language. |
| Current tests prove MVP/product readiness. | `NO-GO` | The old `test_mvp.py` false-green path has been hardened, but current tests are still component checks and manifest checks only. They do not prove runtime daemon reliability, autonomous continual learning, product readiness, RF adaptation, or hardware behavior. | End-to-end runtime witness, shadow-cycle artifacts, scored benchmarks, failure behavior, and product-facing acceptance criteria. | Say "fail-hard component checks passed" only. |

## Minimum Proposal Acceptance Gates

- [x] DSIP 26.BZ BAA and MDA component instructions summarized and
  fingerprinted in a non-sensitive compliance register.
- [x] Exact deadline time, page limits, funding ceiling, period of performance,
  required forms, cybersecurity, and export language confirmed.
- [ ] Company readiness confirmed: UEI, SAM, SBIR.gov Company Registry, SBC
  Control ID, DSIP access, ownership/control, and employee count.
- [ ] CCF/Primus technical claims limited to `VERIFIED` and `WEAK EVIDENCE`
  rows unless phrased as Phase I work.
- [ ] No `NO-GO` claim appears in the technical volume.
- [ ] Every metric claim names raw artifact, command, or measurement source.
- [ ] Any partner-dependent claim has a named partner, letter, SOW, or explicit
  "to be secured" risk.

## Immediate Next Work

1. Use `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md` as the active strategy
   gate while company readiness remains blocked.
2. If the August 19 prime-submission track is reopened, complete
   operator/company readiness: UEI, SAM, SBIR.gov Company Registry, SBC Control
   ID, Login.gov/DSIP access, DD Form 2345, CMMC/SPRS, ownership, employee
   count, TABA decision, and corporate official certification.
3. Generate the first real Primus shadow-cycle manifest from live artifacts.
4. Run the no-training parent baseline against that real manifest.
5. Define the first parent/candidate benchmark runner and scoring schema.
6. Recheck public Topic Q&A before any final MDA submission.
7. Identify RF/waveform and neuromorphic hardware partner candidates.
