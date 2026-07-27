import time
import psutil
import torch
import torch.nn.functional as F
from core.config import SovereignConfig, SystemState

class CircadianController:
    """
    Manages the Day/Night cycle of the Sovereign Mind.
    Decides when to Acquire (Inference) and when to Consolidate (Train).
    """
    def __init__(self, config: SovereignConfig):
        self.config = config
        self.current_state = SystemState.AWAKE
        self.last_activity_time = time.time()
        self.mind = None  # Attached externally
        self.steb = None  # Attached externally

    def heartbeat(self):
        """
        Called periodically to check system status and transition states.
        """
        gpu_load = self._get_gpu_load()
        user_active = self._check_user_activity()

        if self.current_state == SystemState.AWAKE:
            if not user_active and gpu_load < 0.1:
                time_since_active = time.time() - self.last_activity_time
                if time_since_active > (self.config.IDLE_TIMEOUT_MINUTES * 60):
                    self.transition_to(SystemState.DEEP_SLEEP)

        elif self.current_state == SystemState.DEEP_SLEEP:
            if user_active:
                self.transition_to(SystemState.AWAKE)

    def transition_to(self, new_state: SystemState):
        print(f"[Circadian] Transitioning from {self.current_state.value} to {new_state.value}")

        if new_state == SystemState.DEEP_SLEEP:
            self._initiate_sleep_protocol()
        elif new_state == SystemState.AWAKE:
            self._initiate_wake_protocol()

        self.current_state = new_state

    def _get_gpu_load(self):
        return 0.05

    def _check_user_activity(self):
        """Check if user was recently active (within idle timeout)"""
        time_since_active = time.time() - self.last_activity_time
        return time_since_active < (self.config.IDLE_TIMEOUT_MINUTES * 60)

    def register_activity(self):
        """Called externally when user provides input"""
        self.last_activity_time = time.time()

    def _initiate_sleep_protocol(self):
        """Enter Deep Sleep: Consolidate STEB via GaLore"""
        print("[Circadian] Entering DEEP SLEEP...")

        if self.mind is None:
            print("[Circadian] No mind attached, skipping consolidation")
            return False

        if not hasattr(self, 'steb') or self.steb is None:
            print("[Circadian] No STEB buffer, skipping consolidation")
            return False

        if len(self.steb) == 0:
            print("[Circadian] STEB empty, skipping consolidation")
            return False

        print(f"[Circadian] Consolidating {len(self.steb)} episodes...")

        try:
            optimizer, optimizer_name = self._build_sleep_optimizer()
            print(f"[Circadian] Sleep optimizer: {optimizer_name}")
            device = next(self.mind.parameters()).device

            num_sleep_epochs = 3
            optimized_steps = 0
            for epoch in range(num_sleep_epochs):
                episodes = self.steb.sample_batch(batch_size=8)

                for ep in episodes:
                    token_ids = ep.token_ids.to(device=device, dtype=torch.long)
                    if token_ids.numel() < 2:
                        continue

                    optimizer.zero_grad()
                    logits, _, _ = self.mind(token_ids.unsqueeze(0), compute_surprise=False)
                    loss = F.cross_entropy(
                        logits[:, :-1, :].reshape(-1, logits.size(-1)),
                        token_ids[1:].reshape(-1)
                    )
                    loss.backward()
                    optimizer.step()
                    optimized_steps += 1

                print(f"[Circadian] Sleep epoch {epoch+1}/{num_sleep_epochs} complete")

            if optimized_steps == 0:
                print("[Circadian] No valid sleep episodes, skipping buffer clear")
                return False

            self.steb.clear()
            print("[Circadian] Consolidation complete")
            return True
        except Exception as e:
            print(f"[Circadian] Error during consolidation: {e}")
            return False

    def _build_sleep_optimizer(self):
        """Build the sleep optimizer with a real AdamW fallback."""
        try:
            from galore_torch import GaLoreAdamW
            return (
                GaLoreAdamW(
                    self.mind.backbone.parameters(),
                    lr=self.config.SLEEP_LEARNING_RATE,
                    rank=self.config.GALORE_RANK
                ),
                "GaLoreAdamW",
            )
        except ImportError:
            return (
                torch.optim.AdamW(
                    self.mind.backbone.parameters(),
                    lr=self.config.SLEEP_LEARNING_RATE,
                    weight_decay=0.0,
                ),
                "AdamW fallback",
            )

    def _initiate_wake_protocol(self):
        """Wake up and resume inference"""
        print("[Circadian] System Waking Up...")
        self.last_activity_time = time.time()
