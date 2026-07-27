# Primus Status

Last updated: 2026-07-27

## Repository State

- `C:\Primus` began this pass as a non-git local tree.
- `https://github.com/90DegreeRobotics/Primus.git` returned no refs from
  `git ls-remote` during setup, so the remote appeared empty at that time.
- Initial git scope is governance only: repo rules, ignore policy, line-ending
  policy, root README, and this status ledger.

## Local Surfaces Present

- `CCF_Sovereign` - local Python prototype and training materials. Source is
  now imported as prototype evidence, with the current boundary recorded in
  `docs/ccf/CCF_SOURCE_AUDIT_2026-07-27.md`.
- `NeuroCognica_Primus` - local conversation/archive material.
- Root research documents - local Markdown architecture/philosophy docs,
  imported as source notes, not as verified engineering claims.
- Root `primus-map.txt` and `primus-tree.txt` - generated local maps, ignored by
  git.

These are not automatically certified as git-canonical source by the governance
seed. Import them only through an explicit audit plan with path-by-path staging.

## Verified

- Chronos governance template was read from `C:\chronos\AGENTS.md`,
  `C:\chronos\.gitignore`, and `C:\chronos\.gitattributes`.
- Charter files exist at `C:\corpus\THE_CHARTER_OF_COGNITIVE_SOVEREIGNTY.md`
  and `C:\corpus\THE_CHARTER_FOUNDATIONS_ANNEX.md`.
- Two orphaned Python processes from an interrupted audit run were stopped:
  `src\main.py` and `python -u src\main.py`.
- `SBIR_plan.md` was audited after the builder completed. It began as untracked
  builder residue containing a Python wrapper, stale local artifact path,
  broken sandbox download link, and chat-response tail. It has been converted
  into a direct Markdown planning document with source-confidence boundaries.
- The MDA neuromorphic hardware topic was rechecked against the official
  SBIR.gov topic page and Defense SBIR/STTR opportunity guidance on July 27,
  2026. DSIP and the MDA component-specific instructions remain controlling for
  final submission requirements.
- The public DSIP topic API and official solicitation-document endpoints were
  checked on July 27, 2026 for `MDA26BZ04-NV006`. The official DoW SBIR 2026
  BAA Release 4 preface and MDA Release 4 component instructions downloaded as
  PDFs, opened as valid PDFs, and were fingerprinted in
  `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md`.
- The official DSIP/MDA package confirms the August 19, 2026 12:00 p.m. ET
  proposal cutoff, August 12, 2026 12:00 p.m. ET Topic Q&A cutoff, 15-page MDA
  Technical Volume limit, six-month Phase I period, `$307,500` base Phase I cap
  or `$314,000` with TABA, no Phase I Option, CMMC Level 1, ITAR/EAR
  restriction, and DD Form 2345/evidence requirement.
- `docs/sbir/README.md` now exists as the SBIR source/compliance register for
  this pursuit.
- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` now classifies current SBIR
  proposal claims as verified, weak evidence, hypothesis, future work, blocked,
  or no-go.
- `docs/sbir/COMPLIANCE_REGISTER_2026-07-27.md` now records official package
  sources, fingerprints, confirmed submission facts, operator/company blockers,
  and proposal no-go rules.
- `docs/sbir/CLAIM_EVIDENCE_MATRIX_2026-07-27.md` has been reconciled with
  the official DSIP/MDA compliance register so package facts are no longer
  mislabeled as secondary, weak, or blocked.
- `docs/sbir/TECHNICAL_VOLUME_OUTLINE_2026-07-27.md` now provides a 15-page
  MDA Technical Volume outline in the official BAA section order, with claim
  tags, no-go boundaries, page budget, and blocked business/team placeholders.
- `docs/sbir/DEFENSE_EVIDENCE_PIVOT_2026-07-27.md` now source-audits the
  post-deadline strategy and records the strategic pivot: the August 19, 2026
  MDA submission remains a conditional/admin-gated track, while the default path
  is to build a defense evidence package around measured shadow-learning runs,
  raw benchmarks, failure records, and a non-confidential capability statement.
- The pivot source audit verified MDA OSBP/SBIR outreach surfaces, MDA
  prime/subcontracting and Small Business Advocacy Council paths, SBIR Phase III
  follow-on treatment for derived awardee technology, FAR 15.603 limits on
  unsolicited proposals for previously published requirements, DIU
  solution-brief/prototype paths, DARPA MXO BAA timing/scope, and the 2026 Space
  & Missile Defense Symposium date/location. It did not verify the pasted claim
  that the MDA SBIR/STTR Program Office will participate at the 2026 SMD
  Symposium.
- `CCF_Sovereign` source import audit completed on July 27, 2026. The Python
  source/tests/training scripts compiled with exit code 0.
- `python test_mvp.py` ran from `C:\Primus\CCF_Sovereign` and exited 0 in 43.2
  seconds before whitespace normalization and 16.3 seconds after final
  whitespace normalization. Treat this as a component smoke test, not product
  readiness, because the script can skip failures and still print a success
  banner.
- `CCF_Sovereign\test_mvp.py` was hardened on July 27, 2026 into six
  assertion-backed `unittest` component checks using a tiny CPU config. The
  hardened `python test_mvp.py` exited 0 and verified config sanity, tokenizer
  fallback, STEB high-surprise gating, deterministic HRR identity-key round
  trip, tiny substrate forward outputs, and real circadian sleep consolidation
  through the AdamW fallback path.
- `CCF_Sovereign\src\lifecycles\circadian_controller.py` now creates a real
  AdamW sleep optimizer fallback when `galore_torch` is absent, instead of only
  printing a fallback message.
- `CCF_Sovereign\src\evaluation\shadow_manifest.py` now provides deterministic
  JSON/SHA-256 shadow-cycle manifest primitives, and
  `python test_shadow_manifest.py` exited 0 after testing file hashing,
  manifest save/load hash stability, duplicate benchmark-case rejection, and
  train/eval source-overlap rejection.
- `CCF_Sovereign\src\evaluation\shadow_baseline.py` now provides a
  no-training parent baseline result writer bound to a validated shadow
  manifest hash, and `python test_shadow_baseline.py` exited 0 after testing
  pass/fail scoring, raw result artifact writing, responder-error capture,
  non-string response rejection, and explicit no-mutation/no-promotion flags.
- `docs/defense_evidence/README.md` now defines the non-confidential defense
  evidence package structure and exclusions for private, controlled, checkpoint,
  and raw-corpus material.
- `python test_inference.py` ran from `C:\Primus\CCF_Sovereign` and exited 0 in
  34.7 seconds before whitespace normalization and 23.4 seconds after final
  whitespace normalization against the ignored local checkpoint
  `CCF_Sovereign\checkpoints\primus_council_trained.pt`. It proves checkpoint
  load and text generation only; output quality was mixed, unscored, and not
  persona-certified.

## Not Yet Verified

- No product capability is marked live from this root status file.
- `CCF_Sovereign` runtime behavior is not product-verified. Its current
  evidence boundary is local prototype plus smoke/inference witness.
- `CCF_Sovereign` does not currently prove autonomous continual learning,
  reliable sleep consolidation, a learned Council persona, or neuromorphic
  hardware behavior.
- `mamba-ssm` and `galore-torch` were missing from the workstation environment
  during the July 27, 2026 audit, despite being listed in
  `CCF_Sovereign\requirements.txt`.
- Large/private local artifacts remain intentionally ignored: virtual
  environments, raw conversation exports, training data, generated maps, caches,
  and the local checkpoint.
- SBIR administrative readiness remains operator/company-blocked: UEI, SAM,
  SBIR.gov Company Registry, SBC Control ID, Login.gov, DSIP account access,
  ownership/control, employee count, corporate-official certification, DD Form
  2345 status, CMMC/SPRS completion, Volume 7 foreign-affiliation disclosures,
  TABA decision, letters of support, and actual DSIP submission are not yet
  confirmed in this repo.
- The August 19 prime-submission track should not be treated as active unless
  the reopened gate in `SBIR_plan.md` Section 0A clears with operator/company
  evidence.
- The defense evidence package is not built yet. The repo still needs measured
  shadow cycles from real artifacts, parent/candidate benchmark results, raw
  results, failure reports, latency and retention/forgetting measurements,
  resource/cost measurements, and a non-confidential capability statement before
  outreach can lead with data.
- `CCF_Sovereign\src\evaluation\shadow_manifest.py` and
  `CCF_Sovereign\src\evaluation\shadow_baseline.py` are manifest and
  parent-baseline evidence primitives, not a full shadow-learning runner. No
  live parent baseline against the ignored checkpoint, candidate generation,
  training subprocess observation, parent/candidate benchmark comparison, rich
  benchmark scoring, or atomic promotion is implemented yet.
- Public Topic Q&A should be rechecked before final submission. The public DSIP
  Q&A endpoint returned `[]` on July 27, 2026 despite topic metadata reporting
  a nonzero topic question count.
