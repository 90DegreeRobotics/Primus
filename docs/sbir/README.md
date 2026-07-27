# SBIR Proposal Workspace

This folder holds source notes, compliance gates, and proposal assembly artifacts
for the MDA26BZ04-NV006 neuromorphic hardware SBIR pursuit.

## Scope

- Topic: `MDA26BZ04-NV006 - Neuromorphic Hardware`
- Solicitation: `26.BZ`
- Agency/component: Defense SBIR/STTR / Missile Defense Agency
- Current root plan: `..\..\SBIR_plan.md`

## Source Register

| Source | Status | Use |
| --- | --- | --- |
| `https://www.sbir.gov/topics/12804` | Checked 2026-07-27 | Official topic existence, status, dates, summary description |
| `https://www.defensesbirsttr.mil/SBIR-STTR/Opportunities/` | Checked 2026-07-27 | Defense SBIR/STTR submission rules and DSIP control warning |
| `https://www.dodsbirsttr.mil/topics/api/public/topics/search` | Checked 2026-07-27 | Official DSIP topic record for `MDA26BZ04-NV006` |
| `https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation=DOD_SBIR_2026_P1_CBZ&release=4&documentType=RELEASE_PREFACE` | Downloaded/hashed 2026-07-27 | Official DoW SBIR 2026 BAA Release 4 preface |
| `https://www.dodsbirsttr.mil/submissions/api/public/download/solicitationDocuments?solicitation=DOD_SBIR_2026_P1_CBZ&documentType=INSTRUCTIONS&component=MDA&release=4` | Downloaded/hashed 2026-07-27 | Official MDA Release 4 component-specific instructions |
| `https://www.sbir.gov/faq/all` | Checked 2026-07-27 | SBIR eligibility, company registry, subcontract/workshare basics |
| `https://www.bwcoconsulting.com/fod/mda26bz04-nv006` | Secondary, checked 2026-07-27 | Non-controlling mirror only; DSIP/MDA package now controls |
| `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md` | Checked 2026-07-27 | Current Primus/CCF technical source baseline and claim limits |
| `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` | Updated 2026-07-27 | Proposal claim classification, missing evidence, no-go claims, and acceptance gates |
| `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` | Checked 2026-07-27 | DSIP package fingerprints, confirmed submission facts, operator-blocked gates, and no-go rules |
| `docs/sbir/TECHNICAL_VOLUME_OUTLINE_2026-07-27.md` | Created 2026-07-27 | 15-page Volume 2 outline in the official section order with claim tags and no-go boundaries |
| `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md` | Created 2026-07-27 | Source-audited pivot from August 19 proposal race to defense evidence package while company/admin readiness is blocked |
| `docs/defense_evidence/README.md` | Created 2026-07-27 | Non-confidential defense evidence package structure and exclusions |
| `CCF_Sovereign/src/evaluation/shadow_manifest.py` | Created 2026-07-27 | Shadow-cycle manifest primitives for file hashes, benchmark cases, canonical JSON, manifest hashes, and train/eval source-overlap rejection |
| `CCF_Sovereign/test_shadow_manifest.py` | Created 2026-07-27 | Tests for shadow manifest hashing, deterministic save/load, duplicate case rejection, and leakage rejection |
| `CCF_Sovereign/test_mvp.py` | Hardened 2026-07-27 | Assertion-backed fail-hard component tests replacing print-only success behavior |
| `https://www.mda.mil/business/SBIR/SBIR_STTR_programs.html` | Checked 2026-07-27 | MDA SBIR/STTR program focus, technology transition framing, Phase I/II/III overview |
| `https://www.mda.mil/business/SBIR/resources.html` | Checked 2026-07-27 | MDA SBIR/STTR contacts and capability-briefing email |
| `https://www.mda.mil/business/smallbus_programs.html` | Checked 2026-07-27 | MDA OSBP mission, SAM opportunity guidance, outreach email |
| `https://www.mda.mil/business/bus_areasopp.html` | Checked 2026-07-27 | MDA prime/subcontracting path and SBIR/STTR contact guidance |
| `https://www.mda.mil/business/bus_mdasbac.html` | Checked 2026-07-27 | MDA Small Business Advocacy Council and prime liaison contacts |
| `https://www.acquisition.gov/far/15.603` | Checked 2026-07-27 | Unsolicited-proposal no-go for previously published agency requirements |
| `https://www.diu.mil/work-with-us` | Checked 2026-07-27 | DIU solicitation, prototype, and adoption path |
| `https://www.diu.mil/solution-brief-guidance` | Checked 2026-07-27 | DIU solution brief guidance |
| `https://www.darpa.mil/about/offices/mxo` | Checked 2026-07-27 | DARPA MXO scope and current office-wide BAA deadline |
| `https://smdsymposium.org/` | Checked 2026-07-27 | 2026 Space & Missile Defense Symposium date/location |
| `https://smdsymposium.org/technology-track/` | Checked 2026-07-27 | SMD technology-track relevance to AI/ML validation and space/missile defense |

## Blocking Gates

- [x] Download official DSIP 26.BZ BAA package.
- [x] Download MDA component-specific instructions for this topic.
- [x] Confirm exact proposal cutoff time.
- [x] Confirm Phase I funding ceiling.
- [x] Confirm Phase I period of performance.
- [x] Confirm proposal page limits, forms, and attachments.
- [x] Confirm cybersecurity/CMMC language.
- [x] Confirm ITAR/EAR and foreign-national disclosure language.
- [ ] Confirm UEI, SAM, SBIR.gov Company Registry, SBC Control ID, and DSIP access.
- [x] Record strategic pivot: August 19 is a conditional/admin-gated track, not
  the expiration date for the technology program.
- [x] Create non-confidential defense evidence package structure.
- [x] Add deterministic shadow-manifest primitives and tests.

## Truth Rule

No proposal text may claim that Primus, CCF, or Chronos already demonstrates
neuromorphic hardware. Current software may be used as evidence for an auditable
continual-learning lifecycle and as a Phase I requirements/emulator path.

While company readiness is blocked, the default SBIR-adjacent deliverable is the
defense evidence package in
`docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md`, not a cosmetic late-stage
proposal sprint.

The current CCF evidence boundary is prototype-level: source compiles,
assertion-backed component tests run, shadow-manifest primitives are tested, and
a local ignored checkpoint can generate text. It does not prove product
readiness, RF waveform adaptation, neuromorphic hardware, or a verified learned
Council persona.

Before drafting proposal text, check
`docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` and
`docs/sbir/TECHNICAL_VOLUME_OUTLINE_2026-07-27.md`. Present-tense claims must
map to `VERIFIED` rows, weak prototype claims must be labeled preliminary, and
`NO-GO` rows must not appear as technical claims.
