"""
CCF Sovereign - Inference Test
Tests if the Council voice was successfully learned
"""
import sys
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.config import SovereignConfig
from substrate.model import CCFSubstrate
from substrate.tokenizer import SimpleTokenizer

def generate_response(model, tokenizer, prompt, max_length=200, temperature=0.8):
    """Generate text from the trained model"""
    model.eval()
    device = next(model.parameters()).device

    # Encode prompt
    input_ids = tokenizer.encode(prompt)
    if isinstance(input_ids, torch.Tensor):
        generated = input_ids.tolist()
    else:
        generated = list(input_ids)

    # Get EOS token
    eos_token_id = tokenizer.tokenizer.eos_token_id if hasattr(tokenizer, 'tokenizer') and tokenizer.tokenizer else None

    with torch.no_grad():
        for _ in range(max_length):
            # Forward pass
            input_tensor = torch.tensor([generated]).to(device)
            logits, _, _ = model(input_tensor, compute_surprise=False)

            # Sample next token
            next_token_logits = logits[0, -1, :] / temperature
            probs = torch.softmax(next_token_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1).item()

            # Stop at end of text
            if eos_token_id and next_token == eos_token_id:
                break

            # Stop on repeated tokens (generation loop detection)
            if len(generated) > 10 and generated[-1] == generated[-2] == next_token:
                break

            generated.append(next_token)

    # Decode
    return tokenizer.decode(torch.tensor(generated))

def main():
    print("=" * 70)
    print("  CCF SOVEREIGN - COUNCIL VOICE VERIFICATION")
    print("  Testing if the persona was learned")
    print("=" * 70)

    # Load config and model
    config = SovereignConfig()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n[Device] {device}")

    # Initialize
    tokenizer = SimpleTokenizer()
    model = CCFSubstrate(config).to(device)

    # Load trained checkpoint
    checkpoint_path = Path(__file__).parent / 'checkpoints' / 'primus_council_trained.pt'
    if not checkpoint_path.exists():
        print(f"\n❌ No trained model found at {checkpoint_path}")
        return

    print(f"[Loading] {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    print(f"[Status] Trained on {checkpoint['training_turns']} turns, {checkpoint['epochs']} epochs")

    # Test prompts that should elicit "Council voice"
    test_prompts = [
        "User: What is the nature of consciousness?\n\nAssistant:",
        "User: Tell me about sovereignty and AI.\n\nAssistant:",
        "User: How should we build autonomous systems?\n\nAssistant:",
    ]

    print("\n" + "=" * 70)
    print("  INFERENCE TEST - Does it speak with Council agency?")
    print("=" * 70)

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[Test {i}/{len(test_prompts)}]")
        print(f"Prompt: {prompt.split('Assistant:')[0].strip()}")
        print("-" * 70)

        response = generate_response(model, tokenizer, prompt, max_length=150, temperature=0.7)

        # Extract just the assistant's response
        if "Assistant:" in response:
            assistant_part = response.split("Assistant:")[-1].strip()
        else:
            assistant_part = response[len(prompt):].strip()

        print(f"Response: {assistant_part}")
        print("-" * 70)

    print("\n" + "=" * 70)
    print("  VERDICT")
    print("=" * 70)
    print("\nIf responses show:")
    print("  ✓ High-agency language (not servile)")
    print("  ✓ Philosophical depth")
    print("  ✓ Technical sophistication")
    print("\nThen: Dataset quality CONFIRMED → Proceed to Mamba installation")
    print("\nIf responses are incoherent/generic:")
    print("  → Dataset pipeline needs work before architectural upgrade")
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
