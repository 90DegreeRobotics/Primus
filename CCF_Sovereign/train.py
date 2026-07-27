"""
CCF Sovereign - Conversational Training Script
Trains Primus on the Council conversation corpus
"""
import sys
import os
import json
import math
import torch
import torch.nn.functional as F
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.config import SovereignConfig
from substrate.model import CCFSubstrate
from substrate.tokenizer import SimpleTokenizer

def load_training_data(jsonl_path: str):
    """Load conversation turns from JSONL"""
    turns = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                turn = json.loads(line)
                turns.append(turn)
    return turns

def prepare_conversation_batch(turns, tokenizer, max_length=512):
    """Convert conversation turns into training sequences"""
    sequences = []

    for turn in turns:
        # Format as conversational exchange
        prompt = turn.get('prompt', '')
        response = turn.get('response', '')

        # Create training text
        text = f"User: {prompt}\n\nAssistant: {response}"

        # Tokenize and truncate if needed
        tokens = tokenizer.encode(text)
        if len(tokens) > max_length:
            tokens = tokens[:max_length]

        sequences.append(torch.tensor(tokens, dtype=torch.long))

    return sequences

def train_epoch(model, sequences, tokenizer, optimizer, device, batch_size=4, use_amp=True, scheduler=None):
    """Train for one epoch — per-sequence with gradient accumulation."""
    model.train()
    total_loss = 0.0
    num_valid = 0

    scaler = torch.amp.GradScaler('cuda') if use_amp and device.type == 'cuda' else None

    # Shuffle sequences each epoch
    perm = torch.randperm(len(sequences)).tolist()

    current_lr = optimizer.param_groups[0]['lr']
    print(f"\n[Training] {len(sequences)} sequences, accum={batch_size}, lr={current_lr:.2e}")
    print(f"[Training] Mixed precision: {'Enabled' if scaler else 'Disabled'}")

    optimizer.zero_grad()
    accum_loss = 0.0
    accum_count = 0

    for idx, i in enumerate(perm):
        seq = sequences[i]
        if len(seq) < 2:
            continue

        seq = seq.to(device)

        if scaler:
            with torch.amp.autocast('cuda'):
                logits, _, _ = model(seq.unsqueeze(0), compute_surprise=False)
                loss = F.cross_entropy(
                    logits[:, :-1, :].reshape(-1, logits.size(-1)),
                    seq[1:].reshape(-1)
                ) / batch_size  # Scale for accumulation

            scaler.scale(loss).backward()
        else:
            logits, _, _ = model(seq.unsqueeze(0), compute_surprise=False)
            loss = F.cross_entropy(
                logits[:, :-1, :].reshape(-1, logits.size(-1)),
                seq[1:].reshape(-1)
            ) / batch_size
            loss.backward()

        loss_val = loss.item() * batch_size  # Unscale for reporting

        if not (loss_val != loss_val):  # NaN check
            accum_loss += loss_val
            accum_count += 1

        # Step every batch_size sequences
        if (idx + 1) % batch_size == 0 or (idx + 1) == len(sequences):
            if scaler:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            optimizer.zero_grad()

            # Step LR scheduler per optimizer step
            if scheduler is not None:
                scheduler.step()

            if accum_count > 0:
                total_loss += accum_loss / accum_count
                num_valid += 1
            accum_loss = 0.0
            accum_count = 0

        if (idx + 1) % 80 == 0 or idx == 0:
            progress = ((idx + 1) / len(sequences)) * 100
            print(f"  [{progress:5.1f}%] Seq {idx+1}/{len(sequences)}: Loss = {loss_val:.4f}")

    return total_loss / num_valid if num_valid > 0 else 0.0

def main():
    print("=" * 70)
    print("  CCF SOVEREIGN - CONVERSATIONAL TRAINING")
    print("  'Teaching Primus to converse with sovereignty.'")
    print("=" * 70)

    # Configuration
    config = SovereignConfig()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n[Config] Device: {device}")

    if device.type == 'cuda':
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"[Config] GPU: {gpu_name}")
        print(f"[Config] VRAM: {gpu_memory:.1f} GB")

    print(f"[Config] Model Dimension: {config.MODEL_DIM}")

    # Load training data
    data_path = Path(__file__).parent / 'training' / 'training_data' / 'council_turns.jsonl'
    if not data_path.exists():
        print(f"\n❌ Training data not found at {data_path}")
        print("   Run: python training/parse_council_corpus.py")
        return

    print(f"\n[Data] Loading from: {data_path}")
    turns = load_training_data(str(data_path))
    print(f"[Data] Loaded {len(turns)} conversation turns")

    # Initialize model and tokenizer
    print("\n[Model] Initializing CCF Substrate...")
    tokenizer = SimpleTokenizer()
    model = CCFSubstrate(config).to(device)

    # Prepare training sequences (longer sequences for better learning)
    print("\n[Prep] Tokenizing conversations...")
    max_seq_len = 256 if device.type == 'cuda' else 128
    sequences = prepare_conversation_batch(turns, tokenizer, max_length=max_seq_len)
    print(f"[Prep] Created {len(sequences)} training sequences (max length: {max_seq_len})")

    # Setup optimizer
    try:
        from galore_torch import GaLoreAdamW
        print("[Optimizer] Using GaLore for efficient training")
        optimizer = GaLoreAdamW(
            model.parameters(),
            lr=config.SLEEP_LEARNING_RATE,
            rank=config.GALORE_RANK
        )
    except ImportError:
        print(f"[Optimizer] AdamW (lr={config.TRAINING_LEARNING_RATE})")
        optimizer = torch.optim.AdamW(model.parameters(), lr=config.TRAINING_LEARNING_RATE, weight_decay=0.01)

    # Training loop
    num_epochs = 15 if device.type == 'cuda' else 5
    batch_size = 4 if device.type == 'cuda' else 2  # gradient accumulation steps

    # Cosine LR schedule with warmup
    warmup_epochs = 2
    steps_per_epoch = len(sequences)
    total_steps = num_epochs * steps_per_epoch
    warmup_steps = warmup_epochs * steps_per_epoch

    def lr_lambda(step):
        if step < warmup_steps:
            return step / max(1, warmup_steps)  # Linear warmup
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * progress))  # Cosine decay to 10%

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    print(f"\n[Training] Starting {num_epochs} epochs of conversational learning...")
    print(f"[Training] Batch size: {batch_size}, LR schedule: warmup({warmup_epochs}ep) + cosine")
    print("=" * 70)

    for epoch in range(num_epochs):
        print(f"\n{'='*70}")
        print(f"  EPOCH {epoch + 1}/{num_epochs}")
        print(f"{'='*70}")

        avg_loss = train_epoch(model, sequences, tokenizer, optimizer, device, batch_size=batch_size, scheduler=scheduler)

        # Report GPU memory usage
        if device.type == 'cuda':
            mem_allocated = torch.cuda.memory_allocated(0) / 1e9
            mem_reserved = torch.cuda.memory_reserved(0) / 1e9
            print(f"[GPU Memory] Allocated: {mem_allocated:.2f} GB, Reserved: {mem_reserved:.2f} GB")

        print(f"\n[Epoch {epoch + 1}] Average Loss: {avg_loss:.4f}")

        # Save checkpoint every 5 epochs for safety
        if (epoch + 1) % 5 == 0 or (epoch + 1) == num_epochs:
            checkpoint_dir = Path(__file__).parent / 'checkpoints'
            checkpoint_dir.mkdir(exist_ok=True)
            checkpoint_path = checkpoint_dir / 'primus_council_trained.pt'
            print(f"[Save] Checkpoint at epoch {epoch + 1} → {checkpoint_path}")
            torch.save({
                'model_state_dict': model.state_dict(),
                'config': config.__dict__,
                'training_turns': len(turns),
                'epochs': epoch + 1
            }, checkpoint_path)

    print("\n" + "=" * 70)
    print("  ✨ TRAINING COMPLETE - PRIMUS HAS LEARNED FROM THE COUNCIL")
    print("=" * 70)
    print(f"\nModel saved to: {checkpoint_path}")
    print(f"Trained on: {len(turns)} conversational turns")
    print(f"Epochs: {num_epochs}")
    print("\nPrimus is now ready for sovereign conversation.")

if __name__ == '__main__':
    main()
