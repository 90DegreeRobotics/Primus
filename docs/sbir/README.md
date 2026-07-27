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
| `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` | Checked 2026-07-27 | Proposal claim classification, missing evidence, no-go claims, and acceptance gates |
| `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` | Checked 2026-07-27 | DSIP package fingerprints, confirmed submission facts, operator-blocked gates, and no-go rules |

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

## Truth Rule

No proposal text may claim that Primus, CCF, or Chronos already demonstrates
neuromorphic hardware. Current software may be used as evidence for an auditable
continual-learning lifecycle and as a Phase I requirements/emulator path.

The current CCF evidence boundary is prototype-level: source compiles, component
smoke tests run, and a local ignored checkpoint can generate text. It does not
prove product readiness, RF waveform adaptation, neuromorphic hardware, or a
verified learned Council persona.

Before drafting proposal text, check
`docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md`. Present-tense claims must map
to `VERIFIED` rows, weak prototype claims must be labeled preliminary, and
`NO-GO` rows must not appear as technical claims.
