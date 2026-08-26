# Primus Status

Last updated: 2026-08-26

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
- `CCF_Sovereign\src\evaluation\live_parent_baseline.py` now runs a live
  no-training parent baseline against the ignored local checkpoint while keeping
  raw responses in ignored local evidence storage.
- The first live parent baseline ran on July 27, 2026 with
  `python -m src.evaluation.live_parent_baseline --max-new-tokens 64 --device auto`.
  It loaded the ignored checkpoint with `weights_only`, used CUDA, used the
  local GPT-2 tokenizer cache, and produced 0 passed / 3 failed protected cases
  with 0 execution errors. Raw JSON remains under ignored
  `docs/defense_evidence/local_runs/shadow-001-parent-baseline/`; committed
  summaries exist under `docs/defense_evidence/benchmarks/` and
  `docs/defense_evidence/failures/`.
- `CCF_Sovereign\src\evaluation\shadow_compare.py` now provides a
  parent/candidate comparison gate for manifest-bound result artifacts, and
  `python test_shadow_compare.py` exited 0 after testing candidate improvement,
  protected-task regression rejection, new-error rejection, manifest mismatch
  rejection, case-set mismatch rejection, and comparison artifact writing.
- The candidate-generation path was audited on July 27, 2026. Candidate 001 was
  not created because `CCF_Sovereign\train.py` has no candidate output override
  and writes checkpoint saves to the frozen parent path
  `CCF_Sovereign\checkpoints\primus_council_trained.pt`.
- `docs/defense_evidence/README.md` now defines the non-confidential defense
  evidence package structure and exclusions for private, controlled, checkpoint,
  and raw-corpus material.
- `python test_inference.py` ran from `C:\Primus\CCF_Sovereign` and exited 0 in
  34.7 seconds before whitespace normalization and 23.4 seconds after final
  whitespace normalization against the ignored local checkpoint
  `CCF_Sovereign\checkpoints\primus_council_trained.pt`. It proves checkpoint
  load and text generation only; output quality was mixed, unscored, and not
  persona-certified.
- Candidate training is now fail-closed and isolated. Four candidate-safety
  tests and the six inherited MVP tests pass. Training cannot target the frozen
  parent path, each run is commit/hash bound, and promotion is a separate atomic
  command.
- The August 26 scaling ladder ran from clean commit `eb560c0` on the RTX 3060.
  The 5.34M, 16.21M, and 53.93M rungs each completed 3,940 steps. The 155.35M
  rung completed one logged step and then hit an asynchronous CUDA out-of-memory
  RuntimeError. Its initially interrupted manifest was atomically reconciled to
  `failed`; no promotion occurred and the parent hash remained
  `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.
- `src/world_schema` now defines object-agnostic entities, relations, cameras,
  materials, compiler-owned operations, evidence, uncertainty, typed holdouts,
  a 4K codec, and structural unique-program coverage. Eight focused tests pass,
  including exact schema/token/S3V round trips. A generated fixture was also
  accepted by ChronoSophia's real Rust S3V v1 parser.
- The production Mamba path now uses a chunked associative selective scan while
  retaining the former full-state scan only as a differential oracle. Seven
  focused tests pass across output, final state, nonzero initial state, complete
  gradients, long sequence, multiple `d_state`/`d_conv` values, and full Mamba
  blocks.

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
- The defense evidence package has its first live parent-baseline failure
  record and a parent/candidate comparison gate, but it still needs real
  candidate benchmark results, richer benchmark scoring, retention/forgetting
  measurements, resource/cost measurements, and a non-confidential capability
  statement before outreach can lead with data.
- Candidate 001 still does not exist as a quality candidate. Four isolated
  scaling candidates did run on August 26, 2026: three completed harness passes
  and the 155.35M rung failed at the measured CUDA limit. These runs measure
  hardware and training-path behavior only; they were not parent/candidate
  quality comparisons and none was promoted.

- `CCF_Sovereign\src\evaluation\shadow_manifest.py`,
  `CCF_Sovereign\src\evaluation\shadow_baseline.py`, and the new candidate-run
  safety layer are evidence primitives, not proof of candidate quality. Training
  subprocess observation, live parent/candidate comparison, rich scoring, and a
  verified promotion event remain unproven. `promote_candidate.py` is a separate
  hash-gated atomic command and has not been executed.
- Public Topic Q&A should be rechecked before final submission. The public DSIP
  Q&A endpoint returned `[]` on July 27, 2026 despite topic metadata reporting
  a nonzero topic question count.

## GPU scaling ladder results — 2026-08-26

`CCF_Sovereign\src\benchmarks\scaling_ladder.py` ran isolated 5M/15M/50M/150M
configurations using a local 2,048-token byte-level BPE, tied embedding/output
weights, an equal-width Mamba backbone, batch 1, sequence length 256, and seed
base 20260826. The corpus contains 845 turns and 1,012,661 tokens; therefore loss
is a harness sanity signal, not capability or scaling-law evidence.

| Rung | Actual parameters | Steps | Tokens/s | Peak reserved VRAM | Mean loss | Outcome |
|---|---:|---:|---:|---:|---:|---|
| 5M | 5,342,720 | 3,940 | 1,194.65 | 2.28 GB | 7.58 | Completed |
| 15M | 16,214,400 | 3,940 | 623.40 | 4.09 GB | 6.92 | Completed |
| 50M | 53,932,160 | 3,940 | 308.84 | 8.73 GB | 6.84 | Completed |
| 150M | 155,347,584 | 1 | Not recoverable | Not recoverable | 783.02 | CUDA OOM |

The 150M asynchronous OOM originally surfaced as a generic `RuntimeError`, so
its exact peak VRAM and throughput were not recoverable. The ignored summary and
candidate manifest were reconciled from hashed stdout/stderr evidence, and the
harness now recognizes both typed and asynchronous RuntimeError CUDA OOM forms.
Three focused ladder tests pass. No candidate was promoted.

## Chunked selective-scan result — 2026-08-26

At batch 4, sequence 2,048, width 1,024, and state 16, the old full-state scan's
reported allocator demand reached 16.23 GB during forward/backward on the 12.88
GB RTX 3060 and throughput fell to 1,121.88 tokens/s. The chunked scan completed
at 8.50 GB peak reserved and 9,507.04 tokens/s. That is a 1.91x reserved-memory
reduction and an 8.47x throughput increase for this stress shape. At small shapes
the chunked path is slower because launch/loop overhead dominates; this is a
measured tradeoff, not a universal speedup claim.

## Typed world-schema result — 2026-08-26

`CCF_Sovereign\docs\WORLD_SCHEMA_V1.md` documents the domain-general contract.
The schema does not encode object recipes as model architecture. It represents
persistent state and compiler-owned actions, preserves explicit camera pose and
evidence metadata, labels uncertainty and unavailable capabilities, and defines
whole-object-class, whole-operation-family, and composition holdouts. The current
implementation proves representation and round-trip behavior only; it does not
prove learned world dynamics or a shipped world-builder.
