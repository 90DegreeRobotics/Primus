# Chrono-Compressive Field + NeuroCognica Sleep Architecture v0.1

Sovereign textual mind with an auditable cognitive metabolism:

```
WAKE → accumulate episodes → SATURATE → seal T0
  → NREM (replay / weaken / consolidate / prune)
  → REM (recombine / hypothesize)
  → VALIDATE (evidence check; dreams are candidates only)
  → seal T1 → WAKE
```

## Founder / operator path

Double-click:

`C:\Primus\CCF_Sovereign\start_operator.bat`

Then use the desktop controls:

- **Send** — wake acquisition (Hebbian fast weights + Forever Law episode when surprise is high)
- **Sleep Now** — force T0 → NREM → REM → VALIDATE → T1
- **Status** — saturation / STEB / tip hash
- **Verify Ledger** — full Forever Law integrity report

## What is real

- Custom PyTorch Mamba substrate (`src/substrate/`)
- STEB episodic buffer + wake Hebbian fast-weight plasticity
- Measurable saturation (`src/memory/saturation.py`)
- Full sleep cycle orchestrator (`src/lifecycles/sleep_architecture.py`)
- Forever Law ledger: BLAKE3 hash-chain + Merkle boundary seals (`src/memory/forever_law.py`)
  - Algorithmically aligned with `C:\Chronos\crates\chronos_forever_law`
- Canonical memory for promoted/uncertain beliefs only after validation
- Continual-learning benchmark: baseline overwrite vs lifecycle learner
- Desktop operator UI (`src/operator_ui.py`)

## What is not claimed

- Not AgNW / PEDOT:PSS wetware
- Not proof of sentience
- Not “zero resistance” cognition
- Sleep can fail; failures are sealed into Forever Law and shown in the UI

## Developer harness

```bat
cd C:\Primus\CCF_Sovereign
python -m pip install -r requirements.txt
python -m unittest tests.test_sleep_architecture -v
python tests\smoke_sleep_cycle.py
python -m src.benchmarks.continual_learning
```

## Data layout

```
data/
  operator/                 # desktop UI ledger
    forever_law/
    canonical/
  forever_law/              # optional CLI harness ledger
  canonical/
  benchmarks/
    continual_learning_latest.json
```

## Sacred engineering constraints

1. Topology / lifecycle changes through controlled consolidation — not endless overwrite.
2. Episodic truth is append-only.
3. Dream output is a candidate mutation until validation against source events.
4. Every sleep boundary emits Merkle roots T0 and T1.
