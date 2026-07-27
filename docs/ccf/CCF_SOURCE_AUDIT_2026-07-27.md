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

## Evidence Boundary

`test_mvp.py` proves that several components instantiate and can execute a small
forward path: config, tokenizer, STEB buffer, holographic memory, custom Mamba
substrate, and circadian controller initialization.

It does not prove product readiness. The test catches substrate and circadian
exceptions, prints skipped warnings, and still prints `CORE TESTS PASSED - MVP
IS READY` at the end. Treat it as a weak smoke test until assertions and failure
paths are hardened.

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
  ACCOMPLISHED`, and `System is LIVE` style framing.
- `CCF_Sovereign/README_MVP.md` correctly admits `Generative replay stubbed`.
- `CCF_Sovereign/src/lifecycles/circadian_controller.py` has a placeholder GPU
  load implementation: `_get_gpu_load()` returns `0.05`.
- The same controller prints `galore_torch not installed, using standard Adam`
  on import failure, but no Adam fallback optimizer is created in that exception
  branch.
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

- Replace `test_mvp.py` print-only success with assertions and hard failures.
- Add a real optimizer fallback or remove the Adam fallback message.
- Add real GPU/load telemetry or mark the circadian trigger as simulated.
- Build a nonblocking runtime harness that can prove idle transition and sleep
  consolidation behavior.
- Produce a scored inference/persona benchmark with saved prompts, outputs, and
  acceptance criteria.
- Create the SBIR claim/evidence matrix using this file as the CCF source
  baseline.
