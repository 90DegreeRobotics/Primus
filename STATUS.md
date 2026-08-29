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
- Stage 2 now has a deterministic synthetic world-trajectory generator. Seven
  fail-hard generator tests pass for byte-identical regeneration, schema and 4K
  codec validation, lossless S³V round trips, whole object-class and operation-
  family holdouts, held-out compositions, structural coverage, output hashes,
  canonical JSONL, and refusal to overwrite an existing destination.
- The first ignored local Stage 2 smoke dataset used seed `20260826` and produced
  21 validated three-frame programs: 12 train, three held-out-object, three
  held-out-operation, and three held-out-composition trajectories. Structural
  coverage was 21/21 unique with zero duplicates. The JSONL SHA-256 is
  `3a0b5e79bd592dffb2731131f83ce1d1db93a583dd7aed0bdbe6718e4beb3a28`;
  the manifest SHA-256 is
  `6af0b09145aa680e527db98e33b6bf10bcd5752bef7e523e1180301b00d7f607`.
  Token sequences ranged from 7,391 to 7,494 IDs, which is a measured workload
  shape for later batching and throughput work rather than a training result.

## Bounded BridgeData real transition result — 2026-08-27

A separate manifest-bound real-data one-step transition experiment completed after the historical entries above. The Git-excluded frozen intake was a bounded BridgeData V2 LeRobot state/action Parquet shard, manifest SHA-256 `a3e4a457c497fa6d36ac38725829ea7492c6e479e2868ea2e7ba43b66f75bd2a`. The task was **7D state[t] plus 7D action[t] to 7D state[t+1]**, and emitted records only after same-episode, consecutive frame/global-index, finite-vector, and expected timestamp checks.

The one isolated, from-scratch 19,591-parameter candidate trained on 11,999 transitions and was scored separately on 1,998 held-out-episode and 1,996 strict held-out-task transitions. With exact prediction coverage, it reduced aggregate RMSE from the strongest declared nearest-neighbor baseline's `0.039995863776179044` to `0.024990440151625777` on held-out episodes and from `0.11245507024109873` to `0.10875451870665652` on held-out task identities. The candidate's checkpoint restore smoke passed. Both protected Council parent copies retained SHA-256 `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`; no candidate process remained active after inspection.

An independently allocated replication then reserved all 453 complete episodes selected by the first candidate before allocating fresh task and episode groups. Its 476 selected complete episodes had zero measured overlap with the first selection. On exact-coverage evaluation, the fresh candidate achieved `0.026467942605055767` aggregate RMSE versus `0.040291279340085966` on 1,999 held-out-episode transitions and `0.027343755051333143` versus `0.04047397797087077` on 1,997 strict held-out-task transitions. The same predeclared comparison passed a second time. The replication candidate was also terminally `rejected`; its local evidence and non-claims are recorded in `handoff_manus_2026-08-27_bridgedata-independent-replication.md`.

A subsequent evaluation-only rollout gate loaded both terminally rejected checkpoints read-only, re-verified their artifact/source/split bindings, and measured recursively predicted states under observed action sequences. On deterministic 256-case samples per candidate/partition/horizon, both candidates had exact finite coverage and beat their strongest explicit baseline at horizons 1, 2, and 5 on their held-out-episode and strict held-out-task partitions. Candidate `001` grew from strict-task RMSE `0.02560269186609154` at horizon 1 to `0.2579618763146602` at horizon 5; candidate `002` grew from `0.028138646642514857` to `0.07452113239630093`. Horizon 10 was measured descriptively only. The full curve, failure correction, and local-evidence hashes are recorded in `handoff_manus_2026-08-28_bridgedata-rollout-stability.md`.

Codex amended the explicit comparator set on August 28, 2026 with a train-only ordinary least-squares state/action delta baseline and reran the rollout gate into `CCF_Sovereign\evaluation\bridgedata_rollouts\rollout-20260828-linear-001\rollout_stability.json`, 1,598,206 bytes, SHA-256 `177fc39adecd5c86d12d029cfcb3feb3787e49f935065c249cbba758d0ce8ed5`, payload SHA-256 `daf0e64091ba4112c8f8474688a05d4f254567434bc22466383b9e84a574b536`. The stronger comparator became the strongest baseline in every protected acceptance row. Both candidates still passed h1/h2/h5 on their own protected partitions, but candidate `001`'s strict-task h5 margin narrowed to `0.00591893773242147` RMSE (`0.2579618763146602` versus linear `0.2638808140470817`), and candidate `002`'s strict-task h5 margin was `0.014248920008081478` (`0.07452113239630093` versus linear `0.08877005240438241`).

The linear-amended cross-candidate audit then evaluated each source model on the other candidate's protected episode selections, with baselines fitted only from the source candidate's train partition. The local ignored evidence file is `CCF_Sovereign\evaluation\bridgedata_cross_rollouts\cross-rollout-20260828-linear-001\cross_rollout_stability.json`, 171,856 bytes, SHA-256 `2c8dd8c8930b968cebbac7c75403150a9ec1b861d14719171da6fbea088ac484`, payload SHA-256 `60b066d31bca385a28e9ae644d359e6c64470a50495dec5520c99afad8f7635e`. Candidate `001` scored on candidate `002` passed the predeclared h1/h2/h5 rule on both target protected partitions. Candidate `002` scored on candidate `001` passed target held-out episodes but had a target held-out-task h5 point deficit of `0.0006815841557626` RMSE (`0.26076428791202466` versus strongest nearest-neighbor baseline `0.26008270375626206`).

A follow-on, read-only uncertainty audit re-verified the signed cross-rollout evidence and frozen inputs, reconstructed the exact deterministic cases, and applied 10,000 episode-clustered paired bootstrap resamples. Its local ignored evidence is `CCF_Sovereign\evaluation\bridgedata_cross_rollout_uncertainty\cross-rollout-uncertainty-20260828-001\cross_rollout_uncertainty.json`, 1,142,125 bytes, SHA-256 `6cff7a762adf7e4e15da98ca1bee6a72e52f24bbf714d8e743fb0ae50bab2b04`, payload SHA-256 `16b92e45cd476bc260919bbd96cbd7342d5b29bbb36fb45f4ca462a013d38952`. All audited rows had exact finite 256-case coverage and 54–62 selected episode clusters. For the near-zero `002 -> 001` target held-out-task h5 deficit, the candidate-minus-nearest-neighbor MSE 95% interval was `[-0.005246492287060185, 0.009619483092465034]`, which includes zero; its uncertainty-aware label is therefore **indistinguishable**, not a statistically supported failure. Every other h1/h2/h5 cross row had a negative 95% upper MSE endpoint and received the predeclared pass label. All target split evaluations still had zero selected/train episode overlap but source-train task overlap, so these remain episode-disjoint robustness checks rather than strict unseen-task claims relative to the source model.

A distinct strict source-train task-disjoint cross-rollout evaluation then selected 128 complete source-specific target episodes for each frozen candidate. Before scoring, both selections had zero source-selected episode overlap and zero source-train task-ID overlap. At each of h1, h2, and h5, both frozen sources had exact finite 256-case coverage and passed the point-estimate and 10,000-resample episode-clustered paired-bootstrap criteria against their strongest source-train baseline. At h5, candidate `001` scored `0.0681601395924661` versus linear `0.0853185955056040` (paired MSE 95% interval `[-0.00363248166347317, -0.00173388340505353]`); candidate `002` scored `0.0679752241255209` versus linear `0.0802132038781987` (interval `[-0.00258723978344747, -0.00102852483738104]`). The 633,639-byte ignored evidence receipt is `CCF_Sovereign\evaluation\bridgedata_strict_task_cross_rollouts\strict-task-cross-rollout-20260828-001\strict_task_cross_rollout.json`, SHA-256 `218748de489ebc0b921566c21fd8a712898ba77efd1e2251e764c86f90d2ba1f`, payload SHA-256 `445caddf9fb884dae35499a59a856a175d90ff6fee2b03862da7f303c30d172c`. This is strict task-ID separation relative to the source train split on the frozen bounded intake, not semantic novelty or broad task generalization.

A broader read-only context robustness audit then used the same source-specific strict task-ID separation and examined 24 deterministic 128-case rows across h1/h2/h5 and early/late episode position plus low/high recorded action-energy context. All rows had exact finite coverage and zero source-train task overlap. Nineteen paired-bootstrap rows passed; candidate `001` lost to the linear baseline on early/high-energy h1 (`0.0220184868404273` versus `0.0203473497560560`), and four favorable point rows remained bootstrap-indistinguishable. Thus neither candidate has universal measured robustness across these contexts. Local evidence is `CCF_Sovereign\evaluation\bridgedata_context_robustness\context-robustness-20260828-001\context_robustness.json`, 1,289,065 bytes, SHA-256 `692c80dfe9b0f958677f98c333c39afd021f7ed78714d910a219e1e793149f42`, payload SHA-256 `41ec2ab48567ebd65ecf6bd01d1835c2df652c6b99a91d405d402060d40470b3`.

This is **not** a policy, control, safety, actuation, manufacturing, visual prediction, reliable long-horizon rollout, renderer, native Chronos, or product-readiness result. Both candidates are terminally `rejected` from promotion; no promotion occurred.

A schema-only Primus-to-Chronos transition-evidence contract was then implemented and exercised once against frozen candidate `bridge-real-20260827-002` strict h5 input. Its local ignored witness is `CCF_Sovereign\\evidence\\chronos_transition_contracts\\bridge-real-20260827-002-h5-witness.json`, SHA-256 `1a431b8b957ea9082795b4a202d781afa528144c76232997e9a7ac00c55043aa`, payload SHA-256 `e2195592ed0912cf76e21be011279b30df91a90857725c57b50d70b2a10b65e2`. It binds the source candidate/evidence/parent/intake and carries five finite 7D observed actions/predicted states, but it requires `unknown_not_a_chronos_scene_transform`, `control_permitted: false`, and `promotion_performed: false`. No Chronos code or runtime was invoked; this is a non-executable consumer contract, not native Chronos integration or visible world evidence.

A raw-lineage-verified deterministic visual diagnostic was accepted for one candidate `002` strict h5 witness. It is local at `CCF_Sovereign\\evidence\\transition_diagnostics\\diagnostic-20260828-002-complete\\opaque_state_trajectory_diagnostic.png`, 1600x1050, SHA-256 `7f1eaac33b74d6b463921159981dab81017d2b1cdd582101072047a06f2a4af8`; receipt SHA-256 `685616efdc605d65b9bab322e6f4cde282253faa32f2c40a5f378cc890bf542f`. It charts observed versus recursively predicted opaque 7D coordinates and absolute error over five observed actions only. The accepted chart visibly states it is not a Chronos scene, render, policy, or control signal; it is a deterministic data chart, not direct-Blender or native Chronos renderer evidence.

A local mechanical offline-artifact safety receipt then verified that the frozen contract plus accepted diagnostic retain offline-only semantics. The receipt is `CCF_Sovereign\\evidence\\offline_artifact_safety\\safety-20260828-001\\offline_artifact_safety_receipt.json`, SHA-256 `be26dd831518a070d0c939f62b0dab513a2d411ac63bd88f08b4a6934d8c5511`, payload SHA-256 `056b14ef1d400362a273f9e4f676e094f486815c842e4e85e7c22af5afb719ab`. It records execution/control/renderer/Chronos-execution/promotion false and refuses changed flags, schema, digest, witness binding, label, or unsafe consumer intent. This is artifact-schema refusal only; it is not runtime or physical safety certification.

A local static buyer evidence packet then passed its own safety/provenance gate. Its accepted root is `CCF_Sovereign\\evidence\\buyer_demo_packets\\buyer-evidence-20260828-002-complete`, 65,657 bytes. It binds strict evidence SHA-256 `218748de489ebc0b921566c21fd8a712898ba77efd1e2251e764c86f90d2ba1f`, safety receipt SHA-256 `be26dd831518a070d0c939f62b0dab513a2d411ac63bd88f08b4a6934d8c5511`, and copied-chart SHA-256 `7f1eaac33b74d6b463921159981dab81017d2b1cdd582101072047a06f2a4af8`. It is unserved offline evidence presentation only, with execution/control/renderer/Chronos-execution/promotion false; it is not a product, robot, renderer, or native Chronos demonstration. Local ignored raw predictions, checkpoints, metrics, split receipts, lifecycle manifests, and rollout receipts are enumerated in the dated handoffs.

Before the strict task-disjoint comparison, Codex measured strict source-train-task-disjoint feasibility. The metadata-only receipt is `CCF_Sovereign\evaluation\bridgedata_task_disjoint_feasibility\task-disjoint-feasibility-20260828-001\task_disjoint_feasibility.json`, 6,844 bytes, SHA-256 `c56fb16e1fa6a45691af1d95240721c949d0bdcf3641a951315538fad8bcff54`, payload SHA-256 `cef9aa4e3ce14dd8ea6883d8e373a332dc570537218a990727de6851f18bd62a`. After excluding all source-selected episodes and all source-train task IDs, candidate `001` had 23,124 strict target episode clusters, 14,480 target task IDs, and 715,495 h5 rollout-case capacity; candidate `002` had 23,973 clusters, 14,462 target task IDs, and 732,461 h5 capacity. Both source reports had zero selected-episode overlap and zero source-train task overlap. This was feasibility evidence only; the later strict task-disjoint comparison is recorded above as a distinct scored evaluation.

## Not Yet Verified

- No product capability is marked live from this root status file.
- `CCF_Sovereign` runtime behavior is not product-verified. The current evidence boundary is local prototype plus smoke/inference witness.
- `CCF_Sovereign` does not currently prove autonomous continual learning,
  reliable sleep consolidation, a learned Council persona, or neuromorphic
  hardware behavior.
- The Stage 2 trajectories are deterministic synthetic fixtures labeled as
  `generated` and `inferred`. They have not been compiled and rendered as a
  dataset, visually reviewed, ingested by the model trainer, evaluated as model
  predictions, or used for parent/candidate comparison. No training was started,
  no checkpoint was modified, and no candidate was promoted by this work.

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

## Executable `extrude_face` contract result — 2026-08-28

The typed S3V geometry payload previously carried `{extent_mm, bevel_q, variant}`.
The native consumer in Chronos2 requires exactly `{selector, axis, distance_mm}`
and refuses unknown keys, so the two sets were disjoint and every Primus emission
was refused before dispatch. This was measured by emitting from the then-current
commit and reading the payload, not inferred from the source.

`GeometryInvocation.parameters` is now the executable macro contract only. The
declared trajectory knobs moved, unchanged in value, onto the operation itself,
and `temporal_witness` reads them from there. No learning feature value changed
and no new RNG draw was introduced, so the generator stream is untouched. The
extrusion axis is derived from the existing declared direction and variant, so
nothing is invented per macro. `GENERATOR_VERSION` moved to `1.2.0` because the
emitted program shape changed; regenerated synthetic programs hash differently.

Gates: `python -m compileall` on both touched sources, and 80 focused tests
passing across world schema, trajectory generator, temporal witness, compiler,
ingestion, transition metrics, and the temporal candidate suites.

This is a data-contract result. It is not learned world dynamics, a shipped
world-builder, candidate promotion, or renderer evidence in this repo.

## Primus-to-Chronos native witness — 2026-08-28

A Primus-emitted typed S3V `extrude_face` operation was consumed by Chronos2 and
executed through sealed native Dreamer/BlenderMCP, producing a real render.
Input SHA-256 `30ed34ef5dae11477f3771891d1b42214de2ef23ef3bbe66d1d7eae01ae96cb9`,
action `8fc2b4bc-9b4d-5fcf-9311-625e573cc16b`, payload
`{selector: face_by_normal, axis: positive_x, distance_mm: 656}`. The run exited
`0`, the Codex chain verified over 26 events, exactly one sealed `execute_code`
dispatch carried the typed arguments, and the `world_core_v1` notes marker
appeared nowhere in the Codex. The target mesh spans X `-0.5 .. 1.156` where every
other entity spans `-0.5 .. 0.5`: the declared 656 mm landed in the geometry.

The render, the four Chronos2 defects that had to be fixed to reach it, and the
Dreamer verb-coverage limit are recorded in `C:\chronos2`, commit `d97c7a58`, in
`handoff_claude_2026-08-28_native-extrude-face-witness.md`. The witness ran
against a Primus program reduced to its single geometry operation, because the
Dreamer cannot yet execute the relation, observation, transform, camera, or
narrative verbs a full trajectory program contains.

This is renderer-integration evidence produced in Chronos2. It is not a Primus
model result, learned world modelling, BridgeData state semantics, robot policy,
control, safety, or candidate promotion.

## Synthetic trajectory generator — SCAFFOLDING, RETIRING — 2026-08-29

`CCF_Sovereign/src/world_schema/trajectory_generator.py` is declared scaffolding
under `AGENTS.md` rule 9, and it is being retired. It is not a world generator.

What it actually is: a fixed template. Every program it can emit has the same
four entities (`entity_subject`, `entity_actor`, `entity_support`,
`entity_room`), the same material, the same two cameras, the same three frames,
and operations drawn from one hardcoded list of nine. The only variation is
randomised numbers and two `if variant` branches, where `variant = index % 5`.

The declared transition it teaches is closed-form arithmetic:

```python
delta_x = direction * (160 + geometry_extent // 3 + bevel_q)
delta_y = (metallic_q8 - roughness_q8) // 2
delta_z = 60 + ((geometry_extent + bevel_q + metallic_q8 + variant * 73) % 220)
```

The 2026-08-27 positive control confirmed a linear model recovers that linear
function. That is the expected result, it has been recorded, and it cannot be
re-run for further information. Nothing further should be built on it.

The 2026-08-28 executable `extrude_face` contract also violates rule 9: the
extrusion axis is `'xyz'[variant % 3]` with the sign taken from a hardcoded
`variant` branch. Nothing decides which face to extrude. It is a recipe, it was
written by an agent that had no rule telling it not to, and it is retiring with
the generator rather than being polished.

**Correction, same day.** An earlier version of this section set the retirement
condition as "until the BridgeData lane can emit a geometry operation from
learned state." That is a category error and is withdrawn. BridgeData is a 7D
robot state/action to next-state predictor whose coordinate semantics this repo
explicitly records as unknown. It will never emit a geometry operation, and no
amount of growing it will make it do so.

The synthetic generator was a **fake bridge between two lanes that do not connect
that way**, and it was fake at both ends: not real physics, because the
transition it teaches is closed-form arithmetic; and not real shape-thinking,
because the program is a fixed template. Removing it loses nothing, because it
was never carrying anything.

The two real lanes, kept separate:

| Lane | Question | Where it lives |
|---|---|---|
| Observational dynamics | can a small model learn real physical state transitions from observation | `CCF_Sovereign/src/real_data`, this repo |
| Shape thinking | can a guided symbolic planner reach a shape through Blender operations rather than a noun lookup | `crates/chronos_geometry_plan`, including `shape_thinking.rs`, in `C:\chronos2` |

**Retirement condition:** the generator, its entry script
`generate_world_trajectories.py`, and the synthetic candidates that consume it
stay in the tree, unextended and uncited, until a decision is recorded on whether
any Primus-side world-program representation is needed at all once shape thinking
is driven from `chronos_geometry_plan`. If the answer is no, they are removed in
one audited commit. Until then: no new features, no new candidates, no new
evidence claims, and no citation as learned behaviour.

**Not affected:** `CCF_Sovereign/src/real_data`, the frozen BridgeData intake,
and the two rejected BridgeData candidates. That lane shares no code with this
one and is the lane being grown.

## No-recipe geometry understanding — PLANNED — 2026-08-29

Operator directive: **no recipes; the system will be able to learn or not
exist.** Encoded as `AGENTS.md` rule 9. Tandem-repo obligation encoded as rule 10.

Plan: `plan_2026-08-29_0552_no-recipe-geometry-understanding.md`, paired in
`C:\chronos2` at the same filename. Neither copy is in effect alone.

**The split.** Chronos2 is the world — operation space, executor, renderer,
scorer, sealed evidence, and the program sampler that does not yet exist. Primus
is the learner — frozen hash-pinned inputs, candidate lifecycle, declared
baselines, structural holdouts, promotion governance. That split exists because
the BridgeData work is the only genuinely non-recipe result in either repo, and
the governance that produced it is the asset being pointed at geometry.

**Ordering, which is the whole plan.** Learn what operations do before learning
which operations to choose. Learning what operations do needs no language, so it
needs no nouns, so a recipe is not merely forbidden — it is unrepresentable,
because the training data has nowhere to put one. Every previous attempt started
at brief-to-shape, where a dictionary is the path of least resistance.

**Primus obligations when Phase 0 is authorized:** consume the Chronos2 corpus as
a frozen hash-pinned input under the BridgeData intake discipline; hold out by
program structure and never by object class; declare baselines before training;
report which baselines were beaten on which structural holdout or report nothing.

**Not claimed:** no corpus, no model, no training, no result. This entry records
an authorized plan only.
