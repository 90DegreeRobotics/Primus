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

## Evidence Boundary

The original `test_mvp.py` was weak smoke evidence because it caught substrate
and circadian exceptions, printed skipped warnings, and still printed
`CORE TESTS PASSED - MVP IS READY` at the end.

The hardened `test_mvp.py` is now fail-hard component evidence. It proves that a
tiny CPU configuration can instantiate and exercise selected components without
silent skip-success behavior. It still does not prove product readiness,
autonomous continual learning, reliable daemon behavior, RF waveform adaptation,
neuromorphic hardware behavior, or learned Council persona quality.

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

- Generate the first real shadow-cycle manifest from live artifacts.
- Add a parent/candidate benchmark runner that consumes the manifest.
- Add real GPU/load telemetry or mark the circadian trigger as simulated.
- Build a nonblocking runtime harness that can prove idle transition and sleep
  consolidation behavior.
- Produce a scored inference/persona benchmark with saved prompts, outputs, and
  acceptance criteria.
- Create the SBIR claim/evidence matrix using this file as the CCF source
  baseline.
