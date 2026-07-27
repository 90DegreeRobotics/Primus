import time
import torch
import sys
from core.config import SovereignConfig
from lifecycles.circadian_controller import CircadianController
from substrate.model import CCFSubstrate
from substrate.tokenizer import SimpleTokenizer
from memory.steb import STEB, Episode

def main():
    print("=" * 60)
    print("  SOVEREIGN TEXTUAL MIND: CCF ARCHITECTURE")
    print("  'It is not trained; it is grown.'")
    print("=" * 60)

    # Initialize components
    config = SovereignConfig()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mind = CCFSubstrate(config).to(device)
    tokenizer = SimpleTokenizer()
    steb = STEB(max_episodes=512, surprise_threshold=config.MIN_SURPRISE_THRESHOLD)

    heart = CircadianController(config)
    heart.mind = mind
    heart.steb = steb

    print(f"\n[Status] Device: {device.upper()}")
    print(f"[Status] Model Dimension: {config.MODEL_DIM}")
    print(f"[Status] STEB Capacity: {steb.max_episodes} episodes")
    print(f"[Status] Surprise Threshold: {config.MIN_SURPRISE_THRESHOLD}")

    print("\n[System] Sovereignty established. Entering homeostatic loop.")
    print("[System] Type text and press Enter. Ctrl+C to exit.\n")

    hidden_state = None

    try:
        while True:
            heart.heartbeat()

            if heart.current_state.name == "AWAKE":
                try:
                    user_input = input("[You] > ")

                    if user_input.strip():
                        heart.register_activity()
                        tokens = tokenizer.encode(user_input)
                        tokens = tokens.unsqueeze(0).to(device)

                        with torch.no_grad():
                            logits, hidden_state, surprise = mind(tokens, hidden_state)

                        # Generate multi-token response
                        response_tokens = []
                        gen_hidden = hidden_state
                        next_input = tokens[:, -1:]
                        for _ in range(50):  # Up to 50 tokens
                            gen_logits, gen_hidden, _ = mind(next_input, gen_hidden, compute_surprise=False)
                            next_logits = gen_logits[0, -1, :] / 0.8  # temperature
                            probs = torch.softmax(next_logits, dim=-1)
                            next_token = torch.multinomial(probs, num_samples=1)
                            token_id = next_token.item()
                            eos_id = tokenizer.tokenizer.eos_token_id if hasattr(tokenizer, 'tokenizer') and tokenizer.tokenizer else None
                            if eos_id and token_id == eos_id:
                                break
                            response_tokens.append(token_id)
                            next_input = next_token.unsqueeze(0)
                            if len(response_tokens) > 3 and len(set(response_tokens[-4:])) == 1:
                                break  # Stop degenerate repetition

                        response = tokenizer.decode(torch.tensor(response_tokens)) if response_tokens else "..."
                        avg_surprise = surprise[0].mean().item()
                        print(f"[Mind] {response} (surprise: {avg_surprise:.2f})")
                        hidden_state = gen_hidden

                        if avg_surprise > config.MIN_SURPRISE_THRESHOLD:
                            episode = Episode(
                                token_ids=tokens[0],
                                surprise=avg_surprise,
                                timestamp=time.time(),
                                hidden_state=hidden_state
                            )
                            steb.push(episode)

                except EOFError:
                    time.sleep(0.1)
            else:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[System] Shutting down gracefully...")
        print(f"[STEB] Final buffer size: {len(steb)} episodes")
        print("[System] Sovereignty preserved. Goodbye.")

if __name__ == "__main__":
    main()
