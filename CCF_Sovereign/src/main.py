"""
Sovereign Textual Mind — NeuroCognica Sleep Architecture v0.1 runtime.

WAKE: sense / infer / Hebbian fast-weight update / append Forever Law episodes
SATURATE: measurable pressure
SLEEP: T0 seal → NREM → REM → VALIDATE → T1 seal
WAKE: resume with auditable identity trajectory
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import torch

from core.config import SovereignConfig
from lifecycles.circadian_controller import CircadianController
from lifecycles.sleep_architecture import SleepArchitecture
from memory.canonical import CanonicalMemory
from memory.forever_law import ForeverLawCodex
from memory.saturation import SaturationMonitor
from memory.steb import Episode, STEB
from substrate.model import CCFSubstrate
from substrate.tokenizer import SimpleTokenizer


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def build_runtime(config: SovereignConfig | None = None, data_root: Path | None = None):
    config = config or SovereignConfig()
    root = data_root or (_project_root() / config.DATA_ROOT)
    root.mkdir(parents=True, exist_ok=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    mind = CCFSubstrate(config).to(device)
    tokenizer = SimpleTokenizer()
    steb = STEB(
        max_episodes=int(config.STEB_MAX_EPISODES),
        surprise_threshold=config.MIN_SURPRISE_THRESHOLD,
    )
    codex = ForeverLawCodex(root / config.CODEX_DIRNAME)
    canonical = CanonicalMemory(root / config.CANONICAL_DIRNAME)
    saturation = SaturationMonitor(config)
    architecture = SleepArchitecture(
        config=config,
        mind=mind,
        steb=steb,
        codex=codex,
        canonical=canonical,
        saturation_monitor=saturation,
        tokenizer=tokenizer,
    )
    heart = CircadianController(config, architecture=architecture)
    heart.attach(architecture)

    integrity = codex.verify_full_chain()
    if len(codex) > 0 and not integrity.valid:
        raise RuntimeError(
            "Forever Law integrity check failed on boot: "
            + json.dumps(integrity.to_dict())
        )

    return {
        "config": config,
        "device": device,
        "mind": mind,
        "tokenizer": tokenizer,
        "steb": steb,
        "codex": codex,
        "canonical": canonical,
        "architecture": architecture,
        "heart": heart,
        "data_root": root,
    }


def _apply_wake_plasticity(mind, tokens, config, device):
    """Local Hebbian update on Fast Weights during wake acquisition."""
    if tokens.numel() < 2:
        return
    with torch.no_grad():
        embeds = mind.embeddings(tokens.unsqueeze(0).to(device))
        # Use consecutive token embeddings as pre/post activity.
        pre = embeds[:, :-1, :].reshape(-1, embeds.size(-1))
        post = embeds[:, 1:, :].reshape(-1, embeds.size(-1))
        if pre.size(0) == 0:
            return
        mind.apply_hebbian_update(
            pre,
            post,
            learning_rate=float(config.HEBBIAN_LEARNING_RATE),
        )


def main():
    print("=" * 60)
    print("  SOVEREIGN TEXTUAL MIND: CCF + SLEEP ARCHITECTURE v0.1")
    print("  WAKE → SATURATE → NREM → REM → VALIDATE → SEAL → WAKE")
    print("=" * 60)
    print("[Note] Founder/operator path: launch start_operator.bat (desktop UI).")
    print("[Note] This CLI is a developer harness only.\n")

    runtime = build_runtime(config=SovereignConfig.operator())
    config = runtime["config"]
    device = runtime["device"]
    mind = runtime["mind"]
    tokenizer = runtime["tokenizer"]
    steb = runtime["steb"]
    codex = runtime["codex"]
    canonical = runtime["canonical"]
    architecture = runtime["architecture"]
    heart = runtime["heart"]

    print(f"\n[Status] Device: {device.upper()}")
    print(f"[Status] Model Dimension: {config.MODEL_DIM}")
    print(f"[Status] STEB Capacity: {steb.max_episodes} episodes")
    print(f"[Status] Surprise Threshold: {config.MIN_SURPRISE_THRESHOLD}")
    print(f"[Status] Forever Law events: {len(codex)}")
    print(f"[Status] Canonical beliefs: {len(canonical)}")
    print(f"[Status] Data root: {runtime['data_root']}")
    print("\n[System] Commands: /sleep  /status  /verify  Ctrl+C to exit")
    print("[System] Sovereignty established. Entering homeostatic loop.\n")

    hidden_state = None
    mind.eval()

    try:
        while True:
            cycle = heart.heartbeat()
            if cycle is not None:
                print(
                    f"[Sleep] cycle={cycle.cycle_id[:8]}… "
                    f"promoted={cycle.validate.metrics.get('promoted')} "
                    f"rejected={cycle.validate.metrics.get('rejected')} "
                    f"uncertain={cycle.validate.metrics.get('uncertain')}"
                )

            if heart.current_state.name != "AWAKE":
                time.sleep(0.2)
                continue

            try:
                user_input = input("[You] > ")
            except EOFError:
                time.sleep(0.1)
                continue

            text = user_input.strip()
            if not text:
                continue

            heart.register_activity()

            if text == "/sleep":
                report = heart.run_sleep_cycle(force=True, reason="operator_command")
                print(json.dumps(report.to_dict(), indent=2)[:4000])
                continue
            if text == "/status":
                sat = architecture.measure_saturation()
                print(json.dumps({
                    "state": heart.current_state.value,
                    "steb": len(steb),
                    "forever_law_events": len(codex),
                    "canonical_beliefs": len(canonical),
                    "cycles_completed": heart.cycles_completed,
                    "saturation": sat.to_dict(),
                    "tip_hash": codex.tip_hash,
                }, indent=2))
                continue
            if text == "/verify":
                report = codex.verify_full_chain()
                print(json.dumps(report.to_dict(), indent=2))
                continue

            tokens = tokenizer.encode(text)
            if tokens.numel() == 0:
                continue
            tokens = tokens.to(device)

            with torch.no_grad():
                logits, hidden_state, surprise = mind(
                    tokens.unsqueeze(0),
                    hidden_state,
                    compute_surprise=True,
                )

            # Multi-token response
            response_tokens = []
            gen_hidden = hidden_state
            next_input = tokens[-1:].unsqueeze(0)
            for _ in range(50):
                gen_logits, gen_hidden, _ = mind(
                    next_input,
                    gen_hidden,
                    compute_surprise=False,
                )
                next_logits = gen_logits[0, -1, :] / 0.8
                probs = torch.softmax(next_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                token_id = int(next_token.item())
                eos_id = (
                    tokenizer.tokenizer.eos_token_id
                    if getattr(tokenizer, "tokenizer", None) is not None
                    else None
                )
                if eos_id is not None and token_id == eos_id:
                    break
                response_tokens.append(token_id)
                next_input = next_token.view(1, 1)
                if len(response_tokens) > 3 and len(set(response_tokens[-4:])) == 1:
                    break

            response = (
                tokenizer.decode(torch.tensor(response_tokens, dtype=torch.long))
                if response_tokens
                else "..."
            )
            avg_surprise = (
                float(surprise[0, 1:].mean().item())
                if surprise is not None and surprise.size(1) > 1
                else 0.0
            )
            print(f"[Mind] {response} (surprise: {avg_surprise:.2f})")
            hidden_state = gen_hidden

            architecture.saturation.observe_surprise(avg_surprise)
            _apply_wake_plasticity(mind, tokens.cpu(), config, device)

            if avg_surprise > config.MIN_SURPRISE_THRESHOLD:
                episode = Episode(
                    token_ids=tokens.detach().cpu(),
                    surprise=avg_surprise,
                    timestamp=time.time(),
                    hidden_state=None,
                    text=text,
                )
                if steb.push(episode):
                    event_id = architecture.record_wake_episode(episode, text=text)
                    episode.forever_law_event_id = event_id

    except KeyboardInterrupt:
        print("\n\n[System] Shutting down gracefully...")
        print(f"[STEB] Final buffer size: {len(steb)} episodes")
        print(f"[ForeverLaw] Events sealed: {len(codex)}")
        integrity = codex.verify_full_chain()
        print(f"[ForeverLaw] Integrity valid: {integrity.valid}")
        print("[System] Sovereignty preserved. Goodbye.")


if __name__ == "__main__":
    main()
