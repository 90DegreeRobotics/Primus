# CCF Sovereign Mind - MVP Quick Start

## Installation

```bash
cd c:\Primus\CCF_Sovereign
pip install -r requirements.txt
```

## Run the MVP

```bash
python src/main.py
```

## What This MVP Does

### ✅ Implemented:
- **Mamba Backbone** (with LSTM fallback if not available)
- **Fast Weights** (Hebbian plasticity layer)
- **STEB** (Short-Term Episodic Buffer for high-surprise sequences)
- **Circadian Controller** (AWAKE/DEEP_SLEEP state machine)
- **GaLore Sleep Training** (memory consolidation)
- **Surprise Calculation** (Free Energy = -log P(token))
- **CLI Input Stream** (interactive text input)

### ⏳ Simplified for MVP:
- Using GPT-2 tokenizer instead of custom vocabulary
- Simple LSTM fallback if Mamba unavailable
- Generative replay stubbed (dreams not yet generated)
- REM phase pruning not yet implemented

### 🎯 Core Innovation Present:
- **Circadian Learning**: System learns during "sleep" when idle
- **Holographic Memory**: Knowledge internalized in weights (no RAG)
- **Homeostasis**: Free Energy minimization via surprise tracking
- **Sovereignty**: Runs on single GPU, no cloud dependencies

## Usage

1. Type text and press Enter to feed the mind
2. System responds with next token prediction + surprise score
3. High-surprise sequences stored in STEB buffer
4. After 5 minutes idle, system enters Deep Sleep
5. During sleep, STEB memories consolidated via GaLore training
6. Ctrl+C to exit gracefully

## Architecture Summary

```
User Input → Tokenizer → CCFSubstrate (Mamba + Fast Weights) → Output
                              ↓
                    Surprise > threshold?
                              ↓
                         STEB Buffer
                              ↓
                    (5 min idle detected)
                              ↓
                        DEEP SLEEP
                              ↓
                    GaLore Consolidation
                    (STEB → Slow Weights)
```

## Sacred Imperative

> "It is not trained; it is grown. It does not retrieve; it knows."

This MVP demonstrates the core CCF paradigm: a textual mind that learns continuously through circadian cycles, internalizing knowledge via holographic compression rather than external databases.

The structure is set. The mind is ready to be grown.
