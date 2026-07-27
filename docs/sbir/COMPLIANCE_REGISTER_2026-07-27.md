# MDA26BZ04-NV006 Compliance Register

**Audit date:** 2026-07-27
**Topic:** `MDA26BZ04-NV006 - Neuromorphic Hardware`
**Solicitation:** `26.BZ` / `DoW SBIR 2026 BAA` / Release 4
**Component:** Missile Defense Agency (`MDA`)
**DSIP topic ID:** `bc100089f0ce48e18faee7f93caeff25_86561`

## Status

Official public DSIP package access is confirmed for this topic. The controlling
package is not the SBIR.gov copy or a secondary funding-opportunity mirror. The
controlling sources for this pass are:

1. SBIR.gov topic copy for public topic identity and date sanity check.
2. Defense SBIR/STTR Opportunities page for the requirement to follow both the
   program BAA/CSO and Component-specific instructions.
3. DSIP public topic API for the exact topic record and metadata.
4. DSIP public solicitation-document download endpoint for the Release 4 DoW
   SBIR BAA preface and MDA component instructions PDFs.

The raw DSIP upload endpoints returned `401 Unauthorized`; use the public
`/public/download/solicitationDocuments` URLs below for current public access.

## Official Source Package

| Source | Verified result | Fingerprint / note |
| --- | --- | --- |
| `https://www.sbir.gov/topics/12804` | Topic exists, status Open, release date 2026-07-01, open date 2026-07-22, close date 2026-08-19. SBIR.gov warns topic pages are copies. | Checked 2026-07-27. |
| `https://www.defensesbirsttr.mil/SBIR-STTR/Opportunities/` | Proposers must read both the DoW-wide BAA/CSO and Component-specific instructions, and proposals are submitted electronically through DSIP. | Checked 2026-07-27. |
| `https://www.dodsbirsttr.mil/topics/api/public/topics/search` | `searchParam={"searchText":"MDA26BZ04-NV006","solicitationCycleNames":["openTopics"],"sortBy":"finalTopicCode,asc"}` returned exactly one topic. | Status `200`; topic ID `bc100089f0ce48e18faee7f93caeff25_86561`. |
| `https://www.dodsbirsttr.mil/topics/api/public/topics/bc100089f0ce48e18faee7f93caeff25_86561/details` | Returned official topic text, including CMMC Level 1, ITAR true, Phase I/II/III descriptions, and references. | Status `200`; JSON length 4,712 bytes. |
| `https://www.dodsbirsttr.mil/topics/api/public/topics/bc100089f0ce48e18faee7f93caeff25_86561/questions` | Public Q&A endpoint returned an empty list. | Status `200`; body `[]`. Recheck before submission. |
| `https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation=DOD_SBIR_2026_P1_CBZ&release=4&documentType=RELEASE_PREFACE` | Downloaded `DoW 2026 SBIR BAA Preface_07152026.pdf`. | 50 pages; 683,868 bytes; SHA-256 `A3E3ACB63AAD8A6DB04251E991D2F9E428340088FD0FD11DDD8AB0097BF80A75`. |
| `https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation=DOD_SBIR_2026_P1_CBZ&documentType=INSTRUCTIONS&component=MDA&release=4` | Downloaded `MDA_SBIR_26BZ_R4_v2.pdf`. | 26 pages; 324,066 bytes; SHA-256 `5752089DFD463BC9F17C99C1E581C1947F576F1AF10181BEC1492A1F26289335`. |

## Confirmed Submission Facts

- [x] Topic identity confirmed: `MDA26BZ04-NV006`, `Neuromorphic Hardware`,
  MDA, SBIR, solicitation `26.BZ`, release 4.
- [x] Topic status confirmed Open in the official public DSIP search result.
- [x] Release 4 dates confirmed:
  - Pre-release: 2026-07-01.
  - Open / DSIP proposal acceptance: 2026-07-22.
  - DSIP Topic Q&A closes to new questions: 2026-08-12 at 12:00 p.m. ET.
  - Proposal receipt deadline: 2026-08-19 at 12:00 p.m. ET.
- [x] Submission channel confirmed: DSIP is the official portal; proposals by
  other means are disregarded.
- [x] Final submission requires electronic corporate official certification in
  DSIP before the deadline.
- [x] One proposal per open topic is allowed; if more than one is submitted, the
  most recent certified proposal before the deadline receives evaluation and
  prior submissions are nonresponsive.
- [x] The proposal structure uses seven DSIP volumes:
  1. Proposal Cover Sheet.
  2. Technical Volume.
  3. Cost Volume.
  4. Company Commercialization Report.
  5. Supporting Documents.
  6. Fraud, Waste and Abuse Training.
  7. Disclosures of Foreign Affiliations or Relationships to Foreign Countries.
- [x] MDA Technical Volume limit confirmed: Volume 2 must not exceed 15 pages;
  pages beyond the limit are not evaluated.
- [x] Technical Volume format confirmed from the DoW BAA: no type smaller than
  10 point, standard 8.5 x 11 inch paper, one-inch margins, consecutive page
  numbering, and header containing SBC name, topic number, and DSIP proposal
  number.
- [x] Technical Volume upload constraints confirmed: do not lock, password
  protect, encrypt, or embed active graphics/media.
- [x] Phase I period of performance confirmed as anticipated six months in the
  MDA instructions.
- [x] MDA Phase I funding ceiling confirmed: base amount must not exceed
  `$307,500`, or `$314,000` if TABA is included.
- [x] MDA does not use a Phase I Option.
- [x] TABA handling confirmed: MDA Phase I TABA uses the MDA form, belongs in
  Volume 5 under `Other`, and may add up to `$6,500` without burden, profit, or
  fee.
- [x] CMMC confirmed: the target topic and DSIP detail list `Level 1`.
- [x] MDA cybersecurity notice confirmed: prospective awardees should complete
  a CMMC Tier 1 / Foundational self-assessment and enter results in SPRS before
  award.
- [x] ITAR/EAR confirmed: DSIP detail marks `itar=true`; MDA instructions state
  all MDA SBIR topics are restricted under export control regulations.
- [x] Volume 5 export-control attachment confirmed: for MDA export-controlled
  topics, include certified DD Form 2345 or evidence of application submission
  under `Other`.
- [x] Foreign-national risk confirmed: proposed foreign nationals must be
  disclosed, and access to MDA CUI / legacy FOUO is limited to U.S. persons and
  permitted dual citizens unless a limited exception is granted.
- [x] Classified proposals confirmed not accepted for MDA SBIR Phase I.

## Confirmed Topic Technical Target

- [x] Objective: realize neuromorphic technology for continuous adaptation and
  self-optimization in EW and cyber-contested domains.
- [x] Mission context: terrestrial and space applications, distributed sensing,
  real-time learning, autonomously adaptive arbitrary waveform generation,
  contested RF operation, low latency, high throughput, and efficient edge
  processing.
- [x] Phase I deliverables:
  - assess performance, packaging, and survivability challenges;
  - roadmap a TRL 6 product;
  - identify hardware, software, and material required in Phase II;
  - produce a Development, Test, and Evaluation plan for a TRL 6 prototype.
- [x] Phase II target: demonstrate autonomously adaptive arbitrary waveform
  generation using neuromorphic processing.
- [x] Phase II evaluation categories include neuromorphic technology, RF-
  contested operation, space-environment operation, high throughput, efficient
  processing, and real-time latency.
- [x] Performance categories include latency, plasticity, mathematical
  computation complexity, computations per second per watt, throughput, power
  utilization, and action/reaction speed.

## Operator / Company Readiness Gates

These are not repo-verifiable until the operator or company admin provides
evidence or completes DSIP/SAM/SBIR.gov account actions.

- [ ] Confirm applicant is a U.S. for-profit small business.
- [ ] Confirm ownership/control eligibility and employee count including
  affiliates.
- [ ] Confirm Login.gov access.
- [ ] Confirm active SAM registration and UEI.
- [ ] Confirm SBIR.gov Company Registry registration.
- [ ] Confirm valid SBC Control ID and proof of registration/certification.
- [ ] Confirm DSIP account access for the proposal owner.
- [ ] Confirm corporate official can certify in DSIP before submission.
- [ ] Confirm DD Form 2345 certification or evidence of application.
- [ ] Complete/record CMMC Level 1 self-assessment and SPRS entry plan.
- [ ] Complete Volume 7 foreign-affiliation disclosures.
- [ ] Decide whether TABA is requested and, if yes, complete the MDA Phase I
  TABA form.
- [ ] Decide whether any letters of support are available and upload them only
  under DSIP Volume 5 `Letter of Support`.
- [ ] Recheck public Topic Q&A before final submission; the endpoint returned
  `[]` in this pass despite topic metadata showing a nonzero question count.

## Proposal No-Go Rules

- [ ] Do not submit until the final DSIP package is rechecked on submission day.
- [ ] Do not exceed the 15-page MDA Technical Volume limit.
- [ ] Do not place technical-volume content in other volumes to evade page
  limits.
- [ ] Do not claim current Primus/CCF/Chronos software is neuromorphic hardware.
- [ ] Do not claim adaptive RF waveform demonstration exists without a real
  witness artifact.
- [ ] Do not use foreign-national team members for MDA CUI / legacy FOUO work
  without explicit MDA-approved exception handling.
- [ ] Do not include classified information in the proposal.
- [ ] Do not mark Phase I Option budget lines; MDA does not use the Phase I
  Option.
- [ ] Do not treat DSIP upload success as compliance; the BAA states completed
  DSIP submission does not prove each volume meets Component instructions.

## Current Planning Consequence

The `$314,000` Phase I amount is no longer merely secondary-source evidence.
It is confirmed from the official MDA Release 4 component instructions as the
maximum Phase I amount only when TABA is included. The base cap is `$307,500`.

The old "must verify DSIP" blocker is closed for public package access, cutoff
time, page limit, funding ceiling, period of performance, CMMC level, ITAR/EAR,
and required DD Form 2345/evidence. Company readiness and actual DSIP proposal
submission remain operator/action blocked.
