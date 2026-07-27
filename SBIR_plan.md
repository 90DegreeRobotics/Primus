# MDA Neuromorphic Hardware SBIR Opportunity

## Topic MDA26BZ04-NV006 — NeuroCognica Phased Pursuit Plan

**Status checked:** July 27, 2026
**Agency:** Defense SBIR/STTR / Missile Defense Agency (MDA)
**Solicitation:** 26.BZ
**Topic:** MDA26BZ04-NV006 — Neuromorphic Hardware
**Status:** Open
**Release date:** July 1, 2026
**Open date:** July 22, 2026
**Proposal due date:** August 19, 2026

> **Important verification note:** The official SBIR.gov topic page confirms the topic, status, dates, and MDA technical need. SBIR.gov also warns that topic pages are copies and may not be the latest version, so the Defense SBIR/STTR Innovation Portal (DSIP), the active BAA document, and the MDA component-specific instructions control final forms, format, deadlines, cost limits, and compliance requirements. On July 27, 2026, the public DSIP topic API and official PDF package confirmed the Release 4 BAA preface, MDA instructions, 12:00 p.m. ET cutoff, 15-page Technical Volume limit, six-month Phase I period, CMMC Level 1, ITAR/EAR restriction, and MDA Phase I cap of **$307,500 base / $314,000 with TABA**. See `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md`.

---

## 0. Completion Status For This Planning Pass

- [x] Audited the builder output and identified non-Markdown residue.
- [x] Removed the Python wrapper, stale local write target, broken download link, and chat-response tail.
- [x] Rechecked the official SBIR.gov topic page on July 27, 2026.
- [x] Rechecked the Defense SBIR/STTR opportunities instructions on July 27, 2026.
- [x] Rechecked SBIR.gov FAQ workshare/company-registry guidance on July 27, 2026.
- [x] Preserved the hard boundary: current NeuroCognica software is a risk-reduction and verification layer, not already neuromorphic hardware.
- [x] Added proposal assembly content: innovation sentence, mission problem, hypothesis, objectives, milestones, success criteria, risk table, Phase II/III path, team gaps, and budget framework.
- [x] Established `docs/sbir/` as the proposal compliance/source register folder.
- [x] Created `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` to classify proposal claims against current evidence.
- [x] Downloaded, inspected, and fingerprinted the official public DSIP 26.BZ BAA preface and MDA component-specific instructions.
- [x] Confirmed exact Phase I ceiling, period of performance, cutoff time, page limits, and required DSIP volumes from the official package.
- [x] Created `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` for package fingerprints, confirmed facts, operator gates, and no-go rules.
- [x] Reconciled `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` with the official package so stale DSIP blockers no longer survive.
- [x] Created `docs/sbir/TECHNICAL_VOLUME_OUTLINE_2026-07-27.md` as a 15-page, claim-tagged Volume 2 outline in the official section order.
- [ ] Confirm company administrative readiness: UEI, SAM, SBIR Company Registry, SBC Control ID, DSIP account, ownership/control, and employee count.
- [x] Audited the post-deadline/pivot strategy against official sources in `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`.
- [x] Recorded August 19 as a conditional/admin-gated proposal track, not the expiration date of the technology program.
- [x] Established a defense evidence package backlog for future MDA, DIU, DARPA, prime-subcontract, and later SBIR/STTR paths.
- [ ] Complete the operator/company administrative gate if the August 19 prime-submission track is reopened.

---

## 0A. Strategic Pivot As Of 2026-07-27

The August 19, 2026 deadline remains the cutoff for this specific
`MDA26BZ04-NV006` submission. It is not the end of the underlying technical
path.

Because NeuroCognica administrative readiness is not confirmed, the default
strategy is now:

1. Keep the MDA proposal package as a compliance and market-signal record.
2. Do not burn the remaining time on proposal theater unless the administrative
   gate clears.
3. Build a defense evidence package around real shadow-learning runs,
   benchmark manifests, failures, raw measurements, and reproducibility.
4. Use that evidence for future MDA outreach, prime-subcontracting, DIU,
   DARPA, or later SBIR/STTR opportunities.

See `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md` for the source audit,
no-go rules, operator checklist, outreach rules, and evidence backlog.

### Reopened August 19 Gate

Only reopen a full prime-submission sprint if these become true fast enough to
leave real proposal time:

- [ ] confirmed U.S. for-profit applicant identity;
- [ ] ownership/control and employee-count eligibility can be certified;
- [ ] Login.gov access;
- [ ] SAM.gov registration/UEI path submitted and moving;
- [ ] SBIR.gov Company Registry and SBC Control ID;
- [ ] DSIP account access;
- [ ] DD Form 2345 certification or application evidence;
- [ ] CMMC Level 1 / SPRS path;
- [ ] credible Cost Volume assumptions;
- [ ] partner/advisor gap either closed or explicitly carried as proposal risk.

If those do not clear, the next real work is technical evidence, not a prettier
PDF.

---

## 1. Opportunity Summary

MDA is seeking **next-generation neuromorphic technology** for terrestrial and space applications. The stated mission need includes:

- continuous adaptation and self-optimization;
- distributed sensing;
- real-time learning;
- autonomously adaptive arbitrary waveform generation;
- operation in radio-frequency and cyber-contested environments;
- low-latency edge processing;
- high throughput and efficient computation.

The topic explicitly connects neuromorphic processing to the Missile Defense System and emphasizes the need for adaptive processing in contested environments.

### Phase I funding

**Confirmed MDA Phase I ceiling:** `$307,500` base, or `$314,000` if TABA is included. MDA does not use a Phase I Option.

### Phase I purpose

Phase I is intended to **demonstrate a pathway to a product** that addresses neuromorphic-hardware challenges and is relevant to Missile Defense sensing and real-time learning.

Official Phase I deliverables include:

- assessment of performance, packaging, and survivability challenges;
- roadmap to a **Technology Readiness Level (TRL) 6** product;
- identification of hardware, software, and materials required for Phase II;
- Development, Test, and Evaluation plan for a TRL 6 prototype.

### Phase II direction

The stated Phase II target is much more hardware- and mission-specific:

**Demonstrate autonomously adaptive arbitrary waveform generation using neuromorphic processing.**

Evaluation areas include:

- incorporation of neuromorphic technology;
- operation in an RF-contested environment;
- operation in a space environment;
- high throughput;
- efficient processing;
- real-time latency.

Performance categories of interest include:

- latency;
- plasticity;
- mathematical-computation complexity;
- computations per second per watt;
- throughput;
- power utilization;
- machine action/reaction speed.

The topic states that solutions using **neuromorphic semiconductor chips with bio-inspired learning and parallel processing** are prioritized, with possible implementations ranging from an SoC to a complete circuit-card assembly.

### Phase III / dual-use direction

The official Phase III direction is production, test, and evaluation in a realistic system-level environment, potentially including airborne or space **low size, weight, and power (SWaP)** platforms.

---

## 2. Why NeuroCognica May Fit

The strongest alignment is not simply “AI that sleeps.” The relevant engineering thesis is:

> A continuously adaptive intelligence can separate active learning from offline consolidation, generate candidate cognitive states, validate them against protected historical capability, and promote only evidence-backed improvements.

Current `chronos_circadian` work can be positioned as the **software risk-reduction and verification layer** for a future neuromorphic implementation.

Potential alignment:

- **Continuous adaptation / self-optimization:** circadian learn → consolidate → validate lifecycle.
- **Plasticity:** explicit candidate generation and selective promotion rather than permanent uncontrolled overwrite.
- **Real-time learning:** wake-state experience acquisition separated from controlled consolidation.
- **Operational assurance:** deterministic auditing, trusted observation, cryptographic provenance, rollback.
- **Neuromorphic pathway:** software lifecycle first, then migration of consolidation/plasticity functions into neuromorphic substrates.
- **SWaP pathway:** future physical substrate can target computation-per-watt and latency advantages unavailable to conventional retraining pipelines.

### Critical positioning constraint

The current software architecture is **not itself neuromorphic hardware**.

Do not claim that `chronos_circadian`, Primus, or CCF already satisfies the Phase II hardware objective.

Instead:

1. use the software system to prove the learning/consolidation lifecycle;
2. establish measurable performance requirements;
3. define the neuromorphic hardware mapping;
4. use Phase I to demonstrate feasibility and produce a credible TRL-6 development path;
5. reserve physical neuromorphic implementation and adaptive waveform demonstration for the subsequent hardware program.

This keeps the proposal technically honest while making the software prototype valuable as an experimental control system and verification environment.

---

# 3. Proposed Technical Program

## Phase 0 — Administrative Readiness

**Goal:** Make NeuroCognica legally and administratively capable of submitting.

### Checklist

- [ ] Confirm applicant is a U.S. for-profit small business.
- [ ] Confirm company ownership/control satisfies current SBIR eligibility rules.
- [ ] Confirm total employee count including affiliates is 500 or fewer.
- [ ] Confirm Unique Entity Identifier (UEI).
- [ ] Confirm Login.gov access.
- [ ] Confirm SBIR.gov Company Registry registration and SBC Control ID.
- [ ] Confirm SAM.gov entity registration/status as required for federal contracting/award.
- [ ] Create/link Defense SBIR/STTR Innovation Portal (DSIP) account.
- [x] Download and fingerprint the current official 26.BZ BAA preface and MDA component instructions from DSIP.
- [x] Confirm exact submission cutoff time, not just the August 19 date.
- [x] Review current ITAR/EAR language and foreign-national disclosure requirements.
- [x] Review current CMMC/cybersecurity requirements in the MDA component instructions.
- [ ] Decide whether any subcontractor, university, materials lab, RF lab, or neuromorphic-hardware partner is required.
- [ ] Confirm Phase I workshare remains SBIR-compliant if subcontractors are used.
- [x] Establish proposal repository folder.
- [ ] Create immutable source snapshot after source-import audit.

---

## Phase 1 — Truth Baseline / Existing-System Audit

**Goal:** Establish exactly what exists before making proposal claims.

### Checklist

- [ ] Preserve `chronos_circadian` audit history v0.1–v0.4.
- [ ] Complete Primus/CCF/live-lab integration audit.
- [x] Record actual build/test results.
- [ ] Identify real training command and environment.
- [ ] Identify real candidate/checkpoint format.
- [ ] Identify real benchmark entry points.
- [ ] Verify Forever Law event-chain functionality in the integration path.
- [x] Produce a single claim/evidence matrix:
  - claim;
  - current evidence;
  - missing evidence;
  - proposed Phase I proof.
- [ ] Remove unsupported terms such as “sentient,” “zero resistance,” or “flawless integration” from technical proposal language.

**Exit criterion:** Every technical claim in the proposal is labeled **verified, experimental hypothesis, or future work**.

---

## Phase 2 — Primus Shadow Integration

**Goal:** Observe a real learning cycle without permitting autonomous replacement of the canonical parent.

### Checklist

- [ ] Connect actual CCF/Primus training process to `TrustedObserver`.
- [ ] Freeze wake traces at T0.
- [ ] Generate immutable training manifest.
- [ ] Produce isolated candidate workspace.
- [ ] Run training as an observed child process.
- [ ] Hash real candidate output from disk.
- [ ] Run parent and candidate against the same frozen benchmark.
- [ ] Compute per-case and aggregate metrics from raw results.
- [ ] Detect protected-task regression.
- [ ] Detect train/eval leakage from actual manifests.
- [ ] Verify candidate hash at final decision.
- [ ] Seal cycle through Forever Law.
- [ ] Prove canonical Primus hash is unchanged by shadow operation.
- [ ] Execute at least three complete shadow cycles.
- [ ] Record failures rather than repairing them before audit.

**Deliverable:** Repeatable, auditable candidate-generation pipeline.

---

## Phase 3 — Continual-Learning Control Experiment

**Goal:** Produce the first falsifiable proof that the circadian lifecycle adds value.

### Experimental arms

**Control:** ordinary/continuous adaptation path.

**Experimental:** wake → seal → consolidate → validate → audit → shadow-accept/reject.

Both must use:

- the same parent;
- the same training traces;
- the same benchmark manifest;
- the same hardware environment where practical;
- the same scoring rules.

### Metrics

- [ ] Retention of previously learned tasks.
- [ ] Catastrophic-forgetting magnitude.
- [ ] Backward transfer.
- [ ] New-task learning rate.
- [ ] Per-task regressions.
- [ ] Aggregate benchmark score.
- [ ] Candidate rejection rate.
- [ ] Consolidation runtime.
- [ ] Inference latency.
- [ ] Memory/checkpoint growth.
- [ ] GPU/CPU utilization.
- [ ] Energy estimate or measured power where instrumentation permits.
- [ ] Audit/provenance overhead.

**Exit criterion:** A reproducible result showing whether the circadian learner materially improves retention/adaptation versus the control.

---

## Phase 4 — Atomic Promotion

**Goal:** Allow a validated candidate to become the new parent without risking half-applied state.

### Checklist

- [ ] Design atomic candidate promotion.
- [ ] Re-hash candidate immediately before promotion.
- [ ] Verify benchmark and evidence bindings.
- [ ] Verify Forever Law chain and T0 state.
- [ ] Promote through atomic pointer/version switch.
- [ ] Preserve previous canonical parent.
- [ ] Implement deterministic rollback.
- [ ] Simulate crash/power-loss during promotion.
- [ ] Prove no half-promoted state can become canonical.
- [ ] Seal T1 and promoted lineage.

**Deliverable:** Safe software continual-learning lifecycle.

---

## Phase 5 — Neuromorphic Translation Study

**Goal:** Translate the demonstrated software lifecycle into hardware requirements relevant to MDA.

This is the bridge from software research to the actual MDA neuromorphic topic.

### Checklist

- [ ] Identify which circadian operations should remain conventional software.
- [ ] Identify which operations may benefit from physical neuromorphic plasticity.
- [ ] Define candidate hardware classes:
  - memristive networks;
  - neuromorphic semiconductor processors;
  - spiking/parallel architectures;
  - hybrid ionic/electronic devices.
- [ ] Define measurable substrate requirements:
  - update latency;
  - retention;
  - plasticity;
  - energy per adaptation;
  - throughput;
  - recovery/reconfiguration speed;
  - environmental survivability.
- [ ] Map software events to hardware operations.
- [ ] Define wake/consolidation control protocol.
- [ ] Define hardware telemetry required by the Trusted Observer.
- [ ] Define how physical state can be measured and cryptographically represented.
- [ ] Identify packaging and survivability risks.
- [ ] Identify likely RF/space-environment partners or test facilities.
- [ ] Produce bill-of-materials classes and Phase II resource list.
- [ ] Produce TRL roadmap to TRL 6.

**Deliverable:** Neuromorphic architecture and Phase II prototype roadmap.

---

## Phase 6 — MDA-Oriented Neuromorphic Emulator

**Goal:** Demonstrate the proposed hardware behavior before fabrication.

### Checklist

- [ ] Build substrate-independent plasticity emulator.
- [ ] Model hardware time constants rather than copying biological frequencies blindly.
- [ ] Model energy and latency budgets.
- [ ] Model conductance/topology change.
- [ ] Run continual-learning benchmark through emulator.
- [ ] Compare emulator against conventional implementation.
- [ ] Demonstrate adaptation under simulated resource/communication constraints.
- [ ] Define interface to RF waveform-learning experiment.
- [ ] Produce reproducible test package.

**Deliverable:** Digital proof of proposed neuromorphic behavior and measurable requirements for hardware.

---

## Phase 7 — Phase I MDA Deliverable Package

**Goal:** Produce exactly the evidence MDA needs to justify Phase II.

### Required MDA-facing outputs

- [ ] Neuromorphic performance/challenge assessment.
- [ ] Packaging challenge assessment.
- [ ] Survivability challenge assessment.
- [ ] Missile Defense System relevance analysis.
- [ ] Real-time learning feasibility evidence.
- [ ] TRL-6 product roadmap.
- [ ] Hardware requirements.
- [ ] Software requirements.
- [ ] Materials requirements.
- [ ] Development, Test, and Evaluation plan.
- [ ] Phase II prototype architecture.
- [ ] RF-contested-environment test concept.
- [ ] Space-environment test concept.
- [ ] Latency target.
- [ ] Plasticity target.
- [ ] Computations-per-second-per-watt target.
- [ ] Throughput target.
- [ ] Power target.
- [ ] Action/reaction-speed target.
- [ ] Risks and mitigations.
- [ ] Commercial/dual-use pathway.

---

## Phase 8 — Phase II Target

**Goal:** Demonstrate neuromorphic adaptive waveform capability.

Expected technical direction from the topic:

- neuromorphic processing;
- autonomous adaptive arbitrary-waveform generation;
- RF-contested operation;
- space-environment relevance;
- high throughput;
- low latency;
- efficient processing.

### Checklist

- [ ] Select/fabricate physical neuromorphic substrate.
- [ ] Integrate waveform-generation/control workload.
- [ ] Demonstrate online adaptation.
- [ ] Measure latency.
- [ ] Measure plasticity.
- [ ] Measure throughput.
- [ ] Measure computations per second per watt.
- [ ] Measure total power utilization.
- [ ] Measure reaction speed.
- [ ] Test under representative RF contention.
- [ ] Test environmental constraints relevant to space use.
- [ ] Preserve audit/provenance chain through hardware learning cycles.
- [ ] Advance toward TRL 6.

---

## Phase 9 — Phase III / Transition

**Goal:** Move from prototype to a realistic system-level environment and dual-use product.

### Potential defense transition

- distributed sensing;
- adaptive RF systems;
- edge learning;
- contested-environment autonomy;
- spaceborne adaptive processing.

### Potential dual-use markets

- adaptive telecommunications;
- robotics;
- autonomous vehicles;
- industrial edge AI;
- resilient sensor networks;
- low-power continual-learning devices;
- aerospace signal processing.

### Checklist

- [ ] Identify transition partner/program of record.
- [ ] Define realistic testbed.
- [ ] Define SWaP envelope.
- [ ] Verify all technical parameters in representative environment.
- [ ] Develop manufacturing/package pathway.
- [ ] Establish commercial product variant.
- [ ] Preserve SBIR data/IP strategy.
- [ ] Pursue Phase III non-SBIR procurement, licensing, or production opportunities.

---

# 4. Proposal Story

A defensible proposal framing could be:

> NeuroCognica is developing an auditable continual-learning control architecture in which active learning and consolidation occur in separate operational regimes. Candidate cognitive states are generated, directly observed, validated against protected prior capability, cryptographically traced, and rejected or promoted through deterministic evidence gates. Phase I will establish the feasibility of mapping this lifecycle onto neuromorphic processing, quantify latency/plasticity/energy/throughput requirements, and produce the hardware/software/materials and DTE roadmap required for a TRL-6 prototype. The longer-term objective is an adaptive neuromorphic processor capable of real-time learning in RF- and cyber-contested missile-defense environments.

Do **not** claim that the current software stack already demonstrates neuromorphic hardware.

The strongest Phase I story is:

**validated learning lifecycle → quantitative hardware requirements → neuromorphic emulator → TRL-6 prototype roadmap.**

---

# 5. Proposal Assembly Package

## One-sentence innovation

NeuroCognica will develop an auditable continual-learning control layer for neuromorphic processors that separates active learning, consolidation, validation, and promotion so adaptive RF systems can learn in contested environments without silent regression or untraceable state mutation.

## MDA mission problem

MDA needs low-latency, high-throughput adaptive processing for distributed sensing and arbitrary waveform generation in RF- and cyber-contested terrestrial and space environments. Conventional AI retraining pipelines are poorly matched to this need because they usually depend on offline retraining, opaque model-state changes, weak rollback, and limited substrate-level plasticity. The Phase I proposal should argue that neuromorphic hardware can only be credible in this mission context if the learning lifecycle is measurable, auditable, and bounded by protected-task regression checks.

## Technical hypothesis

If an adaptive learning system separates wake-state acquisition from controlled consolidation, freezes training/evaluation manifests, benchmarks candidate states against the protected parent, and cryptographically binds candidate promotion to evidence, then Phase I can convert that software lifecycle into measurable neuromorphic hardware requirements and a credible TRL-6 prototype roadmap for adaptive RF processing.

## Phase I technical objectives

1. Establish a claim/evidence baseline for the current Primus/CCF/Chronos continual-learning stack.
2. Demonstrate an auditable shadow-learning loop that can generate, benchmark, reject, and preserve candidate states without mutating the canonical parent.
3. Run a controlled continual-learning experiment comparing ordinary adaptation against the auditable circadian lifecycle.
4. Translate the observed lifecycle into neuromorphic substrate requirements: latency, plasticity, throughput, energy per adaptation, retention, survivability, and measurable physical-state telemetry.
5. Build a substrate-independent neuromorphic emulator that models the intended hardware behavior before fabrication.
6. Produce the Phase I MDA deliverable package: challenge assessment, hardware/software/materials requirements, DTE plan, Phase II prototype architecture, and TRL-6 roadmap.

## Six-month work plan

| Month | Work package | Output |
| --- | --- | --- |
| 1 | Compliance lock, official DSIP package review, repo/source audit, claim/evidence matrix | Submission-ready compliance register and baseline truth matrix |
| 2 | Primus shadow integration and immutable training/evaluation manifests | Repeatable candidate-generation and observation pipeline |
| 3 | Continual-learning control experiment | Retention, forgetting, adaptation, latency, resource, and provenance metrics |
| 4 | Neuromorphic translation study | Hardware operation map, telemetry needs, substrate requirements, packaging/survivability risks |
| 5 | Neuromorphic emulator and RF-interface concept | Emulator package, resource/latency model, adaptive waveform experiment interface |
| 6 | MDA deliverable assembly | TRL-6 roadmap, DTE plan, Phase II architecture, risk/transition package |

## Quantitative success criteria

- At least three complete shadow cycles run from frozen manifests with candidate hashes recorded before and after evaluation.
- Canonical parent state remains unchanged during all shadow cycles unless an explicit atomic promotion test is being run.
- Every candidate receives per-case and aggregate benchmark scores against the same parent/candidate test set.
- Retention, catastrophic-forgetting magnitude, new-task learning rate, latency, memory growth, GPU/CPU utilization, and provenance overhead are reported from raw result artifacts.
- The neuromorphic emulator exposes explicit assumptions for time constants, energy estimates, plasticity model, topology/conductance changes, and resource constraints.
- The TRL-6 roadmap names hardware classes, materials needs, software interfaces, packaging/survivability risks, partner/test-facility needs, and DTE milestones.
- The final proposal claim matrix marks every claim as `verified`, `experimental hypothesis`, or `future work`.

## Risk table

| Risk | Severity | Mitigation | Evidence gate |
| --- | --- | --- | --- |
| Current stack is software, not neuromorphic hardware | High | Position Phase I as risk reduction, requirements derivation, and emulator work | Proposal language audit removes hardware-completion claims |
| No verified shadow-learning cycles yet | High | Make the first Phase I work package a baseline and shadow-cycle proof | Three-cycle run log with hashes and benchmark outputs |
| RF waveform expertise gap | High | Add RF/waveform partner or advisor before final submission | Partner letter, SOW, or named subcontract plan |
| Hardware substrate expertise gap | High | Identify neuromorphic semiconductor/memristive/spiking hardware partner | Partner capability matrix and Phase II resource list |
| Export-control or foreign-national restrictions | High | DSIP/MDA instruction review before team finalization | Compliance checklist and disclosure decision |
| Cybersecurity/CMMC obligations underestimated | Medium | Treat component instructions as controlling | `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` |
| Energy/power claims become speculative | Medium | Use measured power only where instrumented; otherwise label as estimates | Instrumentation notes and model assumptions |
| Proposal overclaims current Primus maturity | High | Maintain claim/evidence matrix and proposal red-team pass | Final review rejects unsupported claims |

## Phase II pathway

Phase II should not be framed as "more software." The target should be an adaptive RF neuromorphic prototype path:

1. Select a neuromorphic hardware class and partner.
2. Implement a physical or hardware-in-the-loop plasticity substrate.
3. Integrate adaptive waveform-generation/control workload.
4. Demonstrate online adaptation under representative RF contention.
5. Measure latency, plasticity, throughput, computations per second per watt, power utilization, and action/reaction speed.
6. Preserve the audit/provenance chain through hardware learning cycles.
7. Advance the prototype toward a relevant-environment TRL-6 demonstration.

## Phase III / dual-use commercialization

Defense transition paths:

- Missile-defense distributed sensing and adaptive RF systems.
- Spaceborne low-SWaP adaptive processing.
- Contested-environment edge learning and resilient autonomous sensing.

Commercial dual-use paths:

- Adaptive telecommunications and spectrum management.
- Robotics and autonomous edge systems.
- Industrial low-power continual-learning devices.
- Aerospace signal processing and resilient sensor networks.

## Team and partner needs

- [ ] Principal investigator and proposal owner.
- [ ] RF waveform / electronic-warfare technical advisor.
- [ ] Neuromorphic hardware partner or lab.
- [ ] Space/radiation/survivability test advisor.
- [ ] Defense SBIR/STTR contracting and compliance reviewer.
- [ ] Cost/budget reviewer familiar with DSIP submissions.

## Budget framework

Do not finalize the budget until the actual DSIP Cost Volume, indirect rates, allowable costs, and TABA decision are complete. The official MDA package confirms a `$307,500` base Phase I cap, or `$314,000` if TABA is included, so use this as a planning skeleton only:

| Category | Planning intent |
| --- | --- |
| NeuroCognica labor | Baseline audit, shadow integration, experiment design, emulator, proposal deliverables |
| Subcontract/consultant | RF waveform expertise, neuromorphic hardware mapping, survivability/space assessment |
| Equipment/software/materials | Instrumentation, hardware-emulation support, test fixtures, data management |
| Travel/meetings | Only if allowed and justified by partner/test-facility coordination |
| Indirect/fee | Reconcile with accounting and DSIP instructions |

## No-go language

Remove or avoid these in the technical proposal unless separately proved:

- "sentient"
- "conscious hardware"
- "finished neuromorphic system"
- "flawless integration"
- "zero resistance"
- "autonomous self-replacement"
- "hardware demonstrated" before a physical or hardware-in-the-loop witness exists

---

# 6. Eligibility / Program Notes

General SBIR eligibility includes a U.S. for-profit small business, generally more than 50% U.S. citizen/permanent-resident ownership/control under the SBA rules (subject to specific VC provisions), and no more than 500 employees including affiliates.

For SBIR Phase I, the small business normally must perform at least **two-thirds of the research and/or analytical effort**. Phase II normally requires the small business to perform at least one-half.

All applicants must register in the SBIR/STTR Company Registry. The registry uses Login.gov and requests company information including the UEI.

Defense SBIR/STTR proposal submission is handled through the **Defense SBIR/STTR Innovation Portal (DSIP)**. Always use the current DSIP 26.BZ announcement and MDA component instructions as the controlling submission documents.

The official DSIP/MDA package confirms this topic is subject to ITAR/EAR restrictions and CMMC Level 1. Treat export-control, foreign-national, DD Form 2345, and cybersecurity readiness as active compliance work before team finalization.

---

# 7. Immediate Proposal Checklist

## Administrative

- [x] Pull official DSIP topic package.
- [x] Confirm exact funding ceiling in official component instructions.
- [x] Confirm exact deadline time.
- [x] Confirm Phase I period of performance.
- [ ] Verify UEI.
- [ ] Verify SAM registration.
- [ ] Verify SBIR Company Registry / SBC Control ID.
- [ ] Verify DSIP access.
- [x] Review MDA-specific cybersecurity/CMMC language.
- [x] Review ITAR/EAR/foreign-national language.
- [x] Establish compliance folder in repo.
- [x] Establish pivot/evidence-package plan because administrative readiness is
  currently blocked.
- [ ] If pursuing August 19 as prime, clear every reopened August 19 gate in
  Section 0A before final proposal sprint.

## Technical

- [ ] Freeze current `chronos_circadian` audit baseline.
- [ ] Finish v0.5 Primus shadow integration.
- [ ] Execute three real shadow cycles.
- [ ] Create real continual-learning control experiment.
- [ ] Capture retention/forgetting/latency/resource results.
- [x] Define neuromorphic mapping.
- [x] Define MDA-relevant performance targets.
- [x] Draft TRL-6 roadmap.
- [x] Draft Phase II hardware/software/material list.
- [x] Draft DTE plan.
- [ ] Create non-confidential defense evidence package structure.
- [ ] Define first shadow-cycle manifest and parent/candidate benchmark schema.
- [ ] Preserve raw failure reports instead of polishing them away.

## Proposal

- [x] Technical Volume outline.
- [x] One-sentence innovation.
- [x] MDA mission problem.
- [x] Technical hypothesis.
- [x] Existing evidence.
- [x] Claim/evidence matrix.
- [x] Phase I technical objectives.
- [x] Work plan / milestones.
- [x] Quantitative success criteria.
- [x] Risk table.
- [x] Phase II pathway.
- [x] Phase III / dual-use commercialization.
- [x] Team/partners.
- [x] Budget framework.
- [ ] Final compliance review.
- [ ] Submit before final-day traffic.

---

# 8. Sources and Links

## Primary / government

- SBIR.gov topic page — MDA26BZ04-NV006:
  <https://www.sbir.gov/topics/12804>

- Defense SBIR/STTR Innovation Portal (DSIP):
  <https://www.dodsbirsttr.mil/submissions/login>

- Defense SBIR/STTR Opportunities portal:
  <https://www.defensesbirsttr.mil/SBIR-STTR/Opportunities/>

- DSIP public topic search endpoint:
  <https://www.dodsbirsttr.mil/topics/api/public/topics/search>

- DSIP Release 4 BAA preface download endpoint:
  <https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation=DOD_SBIR_2026_P1_CBZ&release=4&documentType=RELEASE_PREFACE>

- DSIP MDA Release 4 component instructions download endpoint:
  <https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation=DOD_SBIR_2026_P1_CBZ&documentType=INSTRUCTIONS&component=MDA&release=4>

- SBIR.gov Company Registration:
  <https://app.www.sbir.gov/company-registration/overview>

- SBIR.gov FAQ / eligibility / subcontracting / data ownership:
  <https://www.sbir.gov/faq/all>

## Current secondary reproduction / analysis of topic

- BW&CO — Neuromorphic Hardware, MDA26BZ04-NV006:
  <https://www.bwcoconsulting.com/fod/mda26bz04-nv006>

This secondary source reproduced useful topic details during the first pass, but it is no longer controlling for proposal requirements. Use the official DSIP package and `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md`.

---

# 9. Source Confidence

| Item | Confidence | Basis |
| --- | --- | --- |
| Topic exists and is open | High | Official SBIR.gov |
| Topic number MDA26BZ04-NV006 | High | Official SBIR.gov |
| Release July 1, 2026 | High | Official SBIR.gov |
| Open July 22, 2026 | High | Official SBIR.gov |
| Due August 19, 2026 | High | Official SBIR.gov |
| MDA need: distributed sensing / real-time learning / low latency / high throughput | High | Official SBIR.gov |
| Phase I amount `$307,500` base / `$314,000` with TABA | High | Official MDA Release 4 component instructions |
| Detailed Phase I/II/III deliverables | High | Official DSIP topic detail and MDA Release 4 component instructions |
| SBIR eligibility basics | High | SBIR.gov/SBA |
| SBIR Phase I two-thirds workshare | High | SBIR.gov FAQ |
| Exact MDA proposal format/page limits/cyber requirements | High for public-package facts; operator action still required | Official DoW BAA preface and MDA Release 4 component instructions |

---

## Bottom Line

This topic is unusually aligned with a NeuroCognica research path because MDA is explicitly asking for **continuous adaptation, self-optimization, real-time learning, low latency, high throughput, plasticity, and efficient processing**.

The proposal should not sell wetware mysticism or claim a finished hardware system.

While company readiness remains blocked, it should guide a disciplined
engineering progression and evidence package:

**auditable continual learning → falsifiable software proof → neuromorphic translation → quantitative emulator → TRL-6 hardware roadmap → adaptive RF neuromorphic prototype.**

The next concrete work is measured shadow integration and a non-confidential
capability/evidence package, not submission theater.
