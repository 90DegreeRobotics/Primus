# Technical Volume Outline - MDA26BZ04-NV006

**Audit date:** 2026-07-27
**Purpose:** Compliance-bound outline for DSIP Volume 2, not a final proposal.
**Topic:** `MDA26BZ04-NV006 - Neuromorphic Hardware`
**Solicitation:** `26.BZ` / `DoW SBIR 2026 BAA` / Release 4
**Component:** MDA

## Control Rules

- [x] Use the official DoW BAA Volume 2 section order.
- [x] Keep the MDA Technical Volume to 15 pages maximum.
- [x] Treat all current Primus/CCF evidence as software prototype evidence only.
- [x] Do not claim existing neuromorphic hardware.
- [x] Do not claim existing adaptive RF waveform demonstration.
- [x] Do not include classified information.
- [x] Do not include a Phase I Option; MDA does not use one.
- [ ] Recheck Topic Q&A before final submission.
- [ ] Verify company/operator readiness before final submission.

## Formatting Constraints

From the official package summarized in
`docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md`:

- 15-page MDA Technical Volume limit.
- Standard 8.5 x 11 inch paper.
- One-inch margins.
- No type smaller than 10 point.
- Consecutive page numbering.
- Header should include SBC name, topic number, and DSIP proposal number.
- Do not lock, password protect, encrypt, or embed active media.
- Resumes and any Technical Volume figures/tables count toward the page limit.

## Proposed Page Budget

| Section | Target pages | Notes |
| --- | ---: | --- |
| Title / restriction legend if used | 0.25 | Include only if proprietary data is asserted. |
| 1. Problem or opportunity | 1.00 | MDA mission need and neuromorphic gap. |
| 2. Phase I technical objectives | 1.00 | Six clear objectives, each testable. |
| 3. Phase I Statement of Work | 5.00 | Substantial portion of Volume 2. |
| 4. Related work | 1.25 | Current software prototype, state of art, limits. |
| 5. Future R&D relationship | 1.25 | Phase II/TRL-6 bridge, approvals, test path. |
| 6. Commercialization strategy | 1.00 | Defense and dual-use markets; needs operator input. |
| 7. Key personnel | 1.00 | PI/team resumes count here. |
| 8. Foreign citizens | 0.50 | Use `None` only if verified true. |
| 9. Facilities/equipment | 0.75 | Forge/local resources plus needed partner facilities. |
| 10. Subcontractors/consultants | 0.75 | RF/hardware/survivability gaps and workshare. |
| 11. Prior/current/pending support | 0.25 | Operator/company fact required. |
| 12. Data/software restrictions | 0.75 | SBIR data-rights assertions and software provenance. |
| Margin reserve | 0.25 | Prevent accidental overrun. |

Total: 15.00 pages.

## Claim Tags

Use these tags in draft notes until final copy is red-teamed:

| Tag | Meaning |
| --- | --- |
| `[VERIFIED]` | May be written in present tense, with exact boundary. |
| `[WEAK]` | Prototype/smoke/local-only evidence; must be called preliminary. |
| `[HYPOTHESIS]` | Phase I thesis to test. |
| `[FUTURE]` | Planned work or deliverable. |
| `[BLOCKED]` | Requires operator/company/partner/external fact. |
| `[NO-GO]` | Must not appear as a claim. |

## Section 1 - Identification And Significance Of The Problem

Draft thesis:

MDA needs neuromorphic technology that can enable continuous adaptation,
self-optimization, distributed sensing, real-time learning, and autonomously
adaptive arbitrary waveform generation in RF- and cyber-contested terrestrial
and space environments. The technical problem is not only raw learning speed; it
is whether an adaptive processor can learn under mission constraints without
silent regression, untraceable state mutation, or unverifiable promotion of a
worse candidate state.

Allowed current-evidence claims:

- `[VERIFIED]` Official DSIP/MDA topic need includes continuous adaptation,
  self-optimization, distributed sensing, real-time learning, adaptive waveform
  generation, contested RF context, low latency, high throughput, and efficient
  edge processing.
- `[WEAK]` Primus/CCF provides local software prototype context for an auditable
  learning/consolidation lifecycle.

No-go:

- `[NO-GO]` Do not say Primus, CCF, or Chronos already solves MDA's hardware
  topic.
- `[NO-GO]` Do not imply current software has been tested in RF-contested or
  space environments.

## Section 2 - Phase I Technical Objectives

Use objective language that can survive an audit:

1. Establish a verified baseline of the current Primus/CCF continual-learning
   software prototype and its claim limits.
2. Design and demonstrate an auditable shadow-learning workflow that generates
   candidate states without mutating the protected parent.
3. Run a controlled continual-learning experiment measuring retention,
   forgetting, adaptation, latency, resource use, and provenance overhead.
4. Translate measured software lifecycle requirements into neuromorphic
   substrate requirements for latency, plasticity, energy, throughput,
   retention, telemetry, packaging, and survivability.
5. Build a substrate-independent neuromorphic emulator or model to test
   hardware behavior assumptions before fabrication.
6. Produce the MDA Phase I deliverable package: performance/packaging/
   survivability challenge assessment, hardware/software/materials list, DTE
   plan, Phase II prototype architecture, and TRL-6 roadmap.

Claim boundary:

- These are `[HYPOTHESIS]` or `[FUTURE]` until Phase I work produces artifacts.

## Section 3 - Phase I Statement Of Work

This should be the largest section. Do not include a Phase I Option.

### Work Package 1 - Compliance Lock And Technical Baseline

Tasks:

- Freeze proposal source register and compliance package fingerprints.
- Create baseline source/capability manifest for Primus/CCF.
- Record current commands, smoke-test limits, checkpoint provenance gaps, and
  no-go claims.

Deliverables:

- Compliance-bound claim matrix.
- Baseline manifest.
- Updated no-go list.

Acceptance:

- No present-tense claim lacks a verified or weak-evidence row.

### Work Package 2 - Shadow Learning Observation Path

Tasks:

- Define parent/candidate state boundaries.
- Freeze training/evaluation manifests before a candidate run.
- Hash input traces, candidate output, benchmark set, and decision records.
- Run observed child process without canonical parent mutation.

Deliverables:

- Shadow-cycle manifest schema.
- At least three complete shadow-cycle logs if feasible during Phase I.
- Candidate acceptance/rejection records.

Acceptance:

- Candidate hashes before and after evaluation match.
- Parent hash remains unchanged unless an explicit promotion test is run.

### Work Package 3 - Continual-Learning Control Experiment

Tasks:

- Define ordinary adaptation control and auditable circadian experimental arm.
- Run both arms on the same parent, traces, and benchmark manifest.
- Measure retention, catastrophic forgetting, new-task learning, per-case
  regression, runtime, memory growth, CPU/GPU utilization, and provenance
  overhead.

Deliverables:

- Raw benchmark artifacts.
- Comparative metric table.
- Failure log preserving negative results.

Acceptance:

- Result can show success or failure; unscored anecdotes are not enough.

### Work Package 4 - Neuromorphic Translation Study

Tasks:

- Identify which lifecycle functions should remain conventional software.
- Identify candidate functions for neuromorphic plasticity.
- Map software events to substrate operations and telemetry.
- Define requirements for latency, plasticity, energy, throughput, retention,
  recovery, environmental survivability, and physical-state measurement.

Deliverables:

- Hardware operation map.
- Telemetry/provenance interface.
- Substrate requirement table.
- Packaging and survivability risk assessment.

Acceptance:

- Each hardware requirement is linked to a measured software need or a clearly
  labeled MDA mission requirement.

### Work Package 5 - Emulator And RF Interface Concept

Tasks:

- Build or specify a substrate-independent emulator for plasticity assumptions.
- Model time constants, energy estimates, conductance/topology changes, and
  resource constraints.
- Define interface requirements for future adaptive waveform generation.

Deliverables:

- Emulator specification or prototype.
- RF-contested-environment test concept.
- Space-environment test concept.

Acceptance:

- Emulator assumptions are explicit; it is not presented as hardware proof.

### Work Package 6 - TRL-6 Roadmap And DTE Plan

Tasks:

- Identify hardware, software, and material classes required in Phase II.
- Define DTE milestones for a TRL-6 prototype path.
- Identify partner/test-facility needs for RF, neuromorphic hardware, and
  space/survivability constraints.

Deliverables:

- TRL-6 roadmap.
- Phase II prototype architecture.
- DTE plan.
- Partner gap matrix.

Acceptance:

- Roadmap names unknowns and partner dependencies instead of burying them.

## Section 4 - Related Work

Use this section to show awareness of the state of the art and NeuroCognica's
current boundary.

Allowed structure:

- MDA topic references and neuromorphic hardware context.
- Primus/CCF source baseline as `[WEAK]` prototype context.
- Charter/Forever Law/Sentinel governance as design doctrine for auditability,
  not as proof of technical performance.
- Related Chronos/continual-learning concepts only if backed by actual source
  audit history or clearly marked as inherited design context.

No-go:

- Do not cite root research prose as engineering proof without an artifact,
  command, or test.

## Section 5 - Relationship With Future R&D

Phase I should produce the evidence needed for Phase II:

- A validated learning lifecycle and measurement package.
- Neuromorphic substrate requirements.
- Hardware/software/materials list.
- RF waveform workload interface definition.
- Space/RF/survivability test concept.
- TRL-6 DTE roadmap.

Approvals/certifications to mention as `[BLOCKED]` until operator-confirmed:

- DD Form 2345 or application evidence.
- CMMC Level 1 self-assessment and SPRS entry.
- Any facility clearance needs if Phase II work becomes classified.
- Export-control handling for team members, partners, and universities.

## Section 6 - Commercialization Strategy

Draft lanes:

- Defense: missile-defense distributed sensing, adaptive RF systems, edge
  learning, contested-environment autonomy, spaceborne low-SWaP processing.
- Dual-use: adaptive telecommunications, spectrum management, robotics,
  industrial edge AI, aerospace signal processing, low-power continual-learning
  devices.

Blocked facts:

- `[BLOCKED]` Company commercialization history.
- `[BLOCKED]` Existing customers/letters of support.
- `[BLOCKED]` Quantitative market claims requiring sourced market data.
- `[BLOCKED]` TABA decision and provider.

## Section 7 - Key Personnel

Do not invent resumes.

Required placeholders:

- `[BLOCKED]` Principal Investigator.
- `[BLOCKED]` Proposal owner.
- `[BLOCKED]` RF waveform / electronic-warfare advisor.
- `[BLOCKED]` Neuromorphic hardware partner or lab.
- `[BLOCKED]` Space/radiation/survivability advisor.
- `[BLOCKED]` Cost/compliance reviewer.

Current allowable statement:

- `[VERIFIED]` Current repo evidence is maintained by NeuroCognica in the
  Primus repository under direct-main governance.

## Section 8 - Foreign Citizens

Use `None` only if the operator confirms no foreign citizens or dual citizens
will work as employees, subcontractors, or consultants on the project.

Until then:

- `[BLOCKED]` Foreign-citizen table requires team facts.
- `[VERIFIED]` MDA instructions require disclosure and warn that missing
  information may make a proposal nonresponsive.

## Section 9 - Facilities / Equipment

Current known facilities:

- `[WEAK]` Forge workstation is a local development environment, not an RF,
  space, survivability, or neuromorphic hardware lab.

Required facility claims:

- `[BLOCKED]` RF test facility or partner.
- `[BLOCKED]` Neuromorphic hardware lab/partner.
- `[BLOCKED]` Environmental/survivability test advisor or facility.
- `[BLOCKED]` Final equipment purchases and pricing in Cost Volume.

## Section 10 - Subcontractors / Consultants

Known constraints:

- `[VERIFIED]` SBIR Phase I normally requires at least two-thirds of research
  and analytical work to be performed by the small business unless otherwise
  approved in writing.
- `[VERIFIED]` Universities cannot publicly release export-controlled/ITAR
  restricted topic information.

Needed decisions:

- `[BLOCKED]` Whether to include RF, hardware, survivability, compliance, or
  cost consultants.
- `[BLOCKED]` Whether any partner needs a letter of support or SOW.
- `[BLOCKED]` Workshare calculation after partner scope is known.

## Section 11 - Prior, Current, Or Pending Support

Do not guess.

- `[BLOCKED]` Operator/company must disclose substantially similar funded,
  pending, or expected proposals/awards, or state none if true.

## Section 12 - Data / Software Restrictions

Likely needed:

- Identify privately developed Primus/CCF/Chronos technical data or software
  that should be asserted with restrictions.
- Mark only supportable assertions.
- Move supporting detail that does not count against the Volume 2 table into
  Volume 5 if appropriate.

Claim boundary:

- `[VERIFIED]` Repo governance, source audit, and claim matrix exist.
- `[BLOCKED]` Final assertion table requires legal/business review.

## Final Red-Team Checklist

- [ ] Every current technical claim maps to the claim matrix.
- [ ] Every unsupported claim is converted to a Phase I task or removed.
- [ ] No `NO-GO` claim appears.
- [ ] Page count is 15 or fewer after rendering/export.
- [ ] No Phase I Option language appears.
- [ ] Q&A is rechecked before final submission.
- [ ] Company readiness gates are complete or plainly unresolved.
- [ ] Volume 5 items are not used to evade the Volume 2 page limit.
- [ ] Budget does not exceed `$307,500` base or `$314,000` with TABA.
- [ ] TABA, if requested, uses the MDA Phase I TABA form.

## Immediate Drafting Order

1. Fill Section 3 work packages with measurable tasks and deliverables.
2. Fill Section 1 and Section 2 from the official MDA need and Phase I
   objectives.
3. Insert only verified or weak-evidence current work in Section 4.
4. Add Phase II bridge and DTE roadmap in Section 5.
5. Leave Sections 6 through 12 visibly blocked until operator/team facts exist.
