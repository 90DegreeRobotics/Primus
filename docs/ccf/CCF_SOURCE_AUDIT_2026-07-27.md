# CCF Source Import Audit - 2026-07-27

## Status

Source-import audit complete. `CCF_Sovereign` is importable as a local Python
prototype with smoke-test evidence. It is not product-live, not a verified
autonomous learner, and not neuromorphic hardware.

## Imported Scope

- First-party CCF source under `CCF_Sovereign/src`.
- CCF parser/training/test scripts:
  - `CCF_Sovereign/train.py`
  - `CCF_Sovereign/test_mvp.py`
  - `CCF_Sovereign/test_inference.py`
  - `CCF_Sovereign/training/analyze_data.py`
  - `CCF_Sovereign/training/execution_trace_logger.py`
  - `CCF_Sovereign/training/parse_council_corpus.py`
- CCF Markdown docs and launcher scripts as historical/source notes.
- Root research/planning Markdown docs as source notes:
  - `Sovereign Textual Mind Paradigm.md`
  - `Fascia and Mycelia Network Comparison.md`
  - `Organic Wetware AI Architecture.md`
  - `council_ideas.md`

## Excluded Scope

- `.venv/`
- `CCF_Sovereign/venv/`
- `CCF_Sovereign/checkpoints/`
- `CCF_Sovereign/training/training_data/`
- `CCF_Sovereign/training_log.txt`
- `CCF_Sovereign/training/parse_council_corpus_v2.py.bak`
- `NeuroCognica_Primus/convos/`
- `primus-map.txt`
- `primus-tree.txt`
- `__pycache__/`

The local checkpoint `CCF_Sovereign/checkpoints/primus_council_trained.pt` was
present during this audit, measured at 1,784,989,658 bytes, and correctly ignored
by `.gitignore`. It was used only for local witness inference and was not staged.

## Verification Run

Commands run from `C:\Primus` or `C:\Primus\CCF_Sovereign`:

```pwsh
python -m pip show torch transformers mamba-ssm galore-torch zstandard psutil einops
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\training CCF_Sovereign\train.py CCF_Sovereign\test_mvp.py CCF_Sovereign\test_inference.py
python test_mvp.py
python test_inference.py
```

Observed results:

- `torch` 2.5.1+cu121 installed.
- `transformers` 5.1.0 installed.
- `zstandard` 0.25.0 installed.
- `psutil` 7.2.2 installed.
- `einops` 0.8.2 installed.
- `mamba-ssm` not installed.
- `galore-torch` not installed.
- `compileall` passed with exit code 0.
- `test_mvp.py` passed with exit code 0 in 43.2 seconds before whitespace
  normalization and 16.3 seconds after final whitespace normalization.
- `test_inference.py` passed with exit code 0 in 34.7 seconds before whitespace
  normalization and 23.4 seconds after final whitespace normalization, using
  CUDA and the ignored local checkpoint.

## Hardening Update - 2026-07-27

Commands run from `C:\Primus` or `C:\Primus\CCF_Sovereign`:

```pwsh
python test_mvp.py
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_mvp.py CCF_Sovereign\test_shadow_manifest.py
python test_shadow_manifest.py
python test_mvp.py
```

Observed results:

- The pre-hardening `python test_mvp.py` baseline still exited 0 and printed
  `CORE TESTS PASSED - MVP IS READY`, confirming the false-green surface.
- `test_mvp.py` was replaced with six assertion-backed `unittest` component
  checks using a tiny CPU config.
- The hardened `python test_mvp.py` exited 0. It verified config sanity,
  tokenizer fallback without Hugging Face dependency, STEB high-surprise
  gating, deterministic HRR identity-key round trip, tiny substrate forward
  shapes/finite tensors, and real circadian sleep consolidation using the
  AdamW fallback path when `galore_torch` is absent.
- `CCF_Sovereign\src\lifecycles\circadian_controller.py` now creates a real
  AdamW sleep optimizer fallback instead of only printing a fallback message.
- `CCF_Sovereign\src\evaluation\shadow_manifest.py` and
  `CCF_Sovereign\test_shadow_manifest.py` now define and test deterministic
  shadow-cycle manifests, SHA-256 file evidence, duplicate benchmark-case
  rejection, and train/eval source-overlap rejection.
- `python test_shadow_manifest.py` exited 0 after correcting a deliberately
  exposed bad expected hash in the new test.
- `python -m compileall -q ...` exited 0.

## Shadow Baseline Update - 2026-07-27

Commands run from `C:\Primus` or `C:\Primus\CCF_Sovereign`:

```pwsh
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_shadow_baseline.py
python test_shadow_baseline.py
```

Observed results:

- `CCF_Sovereign\src\evaluation\shadow_baseline.py` now consumes a validated
  `ShadowCycleManifest` and a parent responder callable.
- It writes a raw JSON result artifact containing the run ID, cycle ID,
  manifest SHA-256, parent file evidence, raw responses, response hashes,
  expected-string pass/fail checks, responder errors, latency, aggregate counts,
  and explicit no-mutation/no-promotion flags.
- `CCF_Sovereign\test_shadow_baseline.py` exited 0 with four tests covering
  pass/fail scoring, artifact hash fields, responder-exception capture,
  non-string responder rejection, and preservation of manifest hash/no-mutation
  semantics.
- This is still parent-only evidence plumbing. It has not run against the real
  ignored checkpoint and does not compare a candidate.

## Live Parent Baseline Update - 2026-07-27

Commands run from `C:\Primus` or `C:\Primus\CCF_Sovereign`:

```pwsh
Get-FileHash -Algorithm SHA256 CCF_Sovereign\checkpoints\primus_council_trained.pt
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_live_parent_baseline.py
python test_live_parent_baseline.py
python test_mvp.py
python -m src.evaluation.live_parent_baseline --max-new-tokens 64 --device auto
```

Observed results:

- The ignored local checkpoint existed at
  `CCF_Sovereign\checkpoints\primus_council_trained.pt`, measured
  `1784989658` bytes, and hashed to
  `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.
- `CCF_Sovereign\src\evaluation\live_parent_baseline.py` now builds a live
  manifest, loads the parent checkpoint with `weights_only`, uses deterministic
  greedy decoding, and writes raw JSON evidence under ignored
  `docs\defense_evidence\local_runs\shadow-001-parent-baseline\`.
- The final live command exited 0 on CUDA with torch `2.5.1+cu121`, GPT-2
  tokenizer loaded from local cache only, checkpoint metadata
  `training_turns=845`, `epochs=15`, manifest SHA-256
  `6aff06c9c16574b43f547d91984f517d27d0ed4a6eb8414f71cb8dee7a447ea4`, and
  result SHA-256
  `fba068afb8ae583cc04088461cbc99b88584937c9f47a509071b0adad2040608`.
- The baseline produced 0 passed / 3 failed protected cases, 0 execution errors,
  and mean latency `2255.469` ms. The missing expected strings were
  `sovereignty`, `risk`, and `audit`.
- Raw responses remain local/ignored. Committed summaries preserve hashes,
  missing criteria, and latency without publishing raw checkpoint outputs.

## Shadow Compare Gate Update - 2026-07-27

Commands run from `C:\Primus` or `C:\Primus\CCF_Sovereign`:

```pwsh
python -m compileall -q CCF_Sovereign\src CCF_Sovereign\test_shadow_compare.py
python test_shadow_compare.py
```

Observed results:

- `CCF_Sovereign\src\evaluation\shadow_compare.py` now compares
  manifest-bound parent and candidate result JSON artifacts.
- The gate rejects manifest SHA-256 mismatch, cycle ID mismatch, and case-set
  mismatch before computing a verdict.
- It computes pass delta, recovered failures, protected-task regressions, new
  errors, per-case latency deltas, and mean case-latency delta without emitting
  raw response text.
- `CCF_Sovereign\test_shadow_compare.py` exited 0 with six fixture tests
  covering candidate improvement, protected-regression rejection, new-error
  rejection, manifest mismatch rejection, case-set mismatch rejection, and
  comparison artifact writing.
- No real candidate result exists yet. This is a referee gate, not proof of
  candidate improvement.

## Candidate Generation Audit - 2026-07-27

Commands and read-only checks used:

```pwsh
rg -n "(argparse|checkpoint|torch\.save|training_data|candidate|parent)" CCF_Sovereign\train.py CCF_Sovereign\training CCF_Sovereign\src\evaluation
Get-ChildItem CCF_Sovereign\training\training_data -Force
Get-ChildItem CCF_Sovereign\checkpoints -Force
Get-FileHash -Algorithm SHA256 CCF_Sovereign\training\training_data\council_turns.jsonl
Get-FileHash -Algorithm SHA256 CCF_Sovereign\checkpoints\primus_council_trained.pt
git check-ignore -v CCF_Sovereign\training\training_data\council_turns.jsonl CCF_Sovereign\training\training_data\council_turns.manifest.json CCF_Sovereign\checkpoints\primus_council_trained.pt
```

Observed results:

- Local training data exists at
  `CCF_Sovereign\training\training_data\council_turns.jsonl`, measured
  `3399338` bytes, `845` lines, and SHA-256
  `8e07223c24ab9234a4b823905d73352eebcb681c04663a592ee7067b0309c556`.
- The local training manifest exists, reports parser version `3.0`, `845`
  turns, and `36` source files. It was inspected by metadata only.
- The frozen parent checkpoint remains
  `CCF_Sovereign\checkpoints\primus_council_trained.pt`, measured
  `1784989658` bytes, and SHA-256
  `5e36cc9a0804716944c92efa503428a1095894bce565ef0ff8bb9ae1ecd9550b`.
- `.gitignore` excludes the local training JSONL, training manifest,
  checkpoints, and `docs\defense_evidence\local_runs\`.
- `CCF_Sovereign\train.py` has no CLI output override, initializes a fresh
  substrate, and saves every checkpoint to
  `CCF_Sovereign\checkpoints\primus_council_trained.pt`.
- The current trainer was not run. Candidate 001 was not created because the
  audited path would mutate the frozen parent checkpoint filename.

Required repair before Candidate 001: add an explicit candidate-generation
entry point with candidate ID, isolated output path, parent hash pre/post guard,
training input hash, candidate hash, environment capture, and same-manifest
candidate evaluation before comparison.

## Evidence Boundary

The original `test_mvp.py` was weak smoke evidence because it caught substrate
and circadian exceptions, printed skipped warnings, and still printed
`CORE TESTS PASSED - MVP IS READY` at the end.

The hardened `test_mvp.py` is now fail-hard component evidence. The live parent
baseline proves the ignored checkpoint can be bound to a manifest and evaluated
without training or mutation. The failed checks mean it still does not prove
product readiness, autonomous continual learning, reliable daemon behavior, RF
waveform adaptation, neuromorphic hardware behavior, or learned Council persona
quality.

`test_inference.py` proves that the ignored checkpoint loads and produces text.
It does not prove that Council agency, robust persona learning, or general
capability has been learned. The witnessed outputs were mixed: fluent technical
and symbolic fragments, visible corpus echo, topic drift, a SQL fragment, a
box-drawing fragment, and no scored benchmark. It also loads the checkpoint with
`torch.load(..., weights_only=False)`, which emitted a PyTorch warning about
untrusted pickle execution risk.

## Bullshit Filter Findings

- `CCF_Sovereign/MVP_STATUS.md` contains historical overclaim language:
  `COMPLETE - ALL SYSTEMS OPERATIONAL`, `fully operational`, `MISSION
  ACCOMPLISHED`, and `System is LIVE` style framing. It now has a current audit
  warning at the top, but the historical language remains below it.
- `CCF_Sovereign/README_MVP.md` correctly admits `Generative replay stubbed`.
- `CCF_Sovereign/src/lifecycles/circadian_controller.py` has a placeholder GPU
  load implementation: `_get_gpu_load()` returns `0.05`.
- The prior circadian controller printed `galore_torch not installed, using
  standard Adam` on import failure, but did not create the fallback optimizer.
  This was fixed on 2026-07-27; the fallback is now real AdamW component
  behavior covered by `test_mvp.py`.
- `CCF_Sovereign/src/main.py` drives the loop through blocking `input()`, so the
  idle/sleep behavior is not yet proven as a reliable daemon loop.
- `CCF_Sovereign/requirements.txt` names `mamba-ssm` and `galore-torch`, but
  this workstation audit found both missing.
- Root research docs include speculative phrases such as `sentient`,
  `zero-resistance`, and `flawlessly integrated`. They are admissible as research
  notes, not as engineering proof.
- `council_ideas.md` is a planning/blueprint note with chat-style framing. It is
  source context, not a completed implementation.

## SBIR Use

For the MDA neuromorphic-hardware SBIR, CCF can support only these current
claims:

- A local first-party software prototype exists for a continual-learning style
  architecture.
- The prototype compiles.
- Component smoke tests and checkpoint inference can run on the Forge.
- There is a concrete source surface for deriving Phase I requirements,
  experiments, emulator design, and truth-matrix claims.

CCF cannot currently support claims that NeuroCognica has demonstrated
neuromorphic hardware, real adaptive RF waveform generation, autonomous
self-optimization in production, sentience, or a verified learned Council voice.

## Next Work

- Generate a candidate result artifact from the frozen manifest and run it
  through the comparison gate.
- Harden candidate generation so it cannot target
  `CCF_Sovereign\checkpoints\primus_council_trained.pt`.
- Add richer scoring that can judge quality without committing raw private
  responses.
- Add real GPU/load telemetry or mark the circadian trigger as simulated.
- Build a nonblocking runtime harness that can prove idle transition and sleep
  consolidation behavior.
- Produce a scored inference/persona benchmark with saved prompts, outputs, and
  acceptance criteria.
- Create the SBIR claim/evidence matrix using this file as the CCF source
  baseline.

## Candidate-generation safety update — 2026-08-26

The July blocker is closed at the code and regression-test level. `train.py` now
requires a unique candidate ID and delegates all output to
`training/candidate_run.py`. The run refuses parent or corpus-manifest hash drift,
writes only under the candidate directory, emits a run manifest, and checks the
parent again before every checkpoint. `promote_candidate.py` is a separate
hash-gated atomic operation. This update does not claim that Candidate 001 has
been trained, compared, or promoted.
