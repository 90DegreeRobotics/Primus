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
- `docs/sbir/README.md` now exists as the SBIR source/compliance register for
  this pursuit.
- `CCF_Sovereign` source import audit completed on July 27, 2026. The Python
  source/tests/training scripts compiled with exit code 0.
- `python test_mvp.py` ran from `C:\Primus\CCF_Sovereign` and exited 0 in 43.2
  seconds before whitespace normalization and 16.3 seconds after final
  whitespace normalization. Treat this as a component smoke test, not product
  readiness, because the script can skip failures and still print a success
  banner.
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
- SBIR administrative readiness remains operator/DSIP-blocked: UEI, SAM,
  SBIR.gov Company Registry, SBC Control ID, DSIP account, exact cutoff time,
  page limits, funding ceiling, and component-specific cybersecurity/export
  language are not yet confirmed in this repo.
