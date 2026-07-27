from dataclasses import dataclass
from enum import Enum

class SystemState(Enum):
    AWAKE = "AWAKE"
    DREAMING = "DREAMING"
    DEEP_SLEEP = "DEEP_SLEEP"
    REM = "REM"

@dataclass
class SovereignConfig:
    # Hardware Constraints
    MAX_VRAM_GB: int = 24
    USE_QUANTIZATION_NF4: bool = True

    # Model Architecture
    MODEL_DIM: int = 4096
    STATE_DIM: int = 512  # Working dimension for backbone processing
    NUM_LAYERS: int = 8   # Depth of the Mamba backbone (more layers = deeper comprehension)
    VOCAB_SIZE: int = 50257

    # Mamba SSM Parameters
    MAMBA_D_STATE: int = 16    # State expansion factor (memory capacity per channel)
    MAMBA_D_CONV: int = 4      # Causal convolution kernel width (local context)
    MAMBA_EXPAND: int = 2      # Block expansion factor (expressivity)
    MAMBA_DROPOUT: float = 0.1 # Inter-layer dropout

    # Holographic Memory
    HRR_DIM: int = 4096  # Must match model dim for superposition
    ORTHOGONALITY_THRESHOLD: float = 0.05

    # Plasticity & Learning
    HEBBIAN_LEARNING_RATE: float = 0.001
    SLEEP_LEARNING_RATE: float = 1e-5
    TRAINING_LEARNING_RATE: float = 3e-4  # Mamba-optimal: lower than LSTM to prevent divergence
    GALORE_RANK: int = 128
    GRADIENT_CLIP_NORM: float = 1.0  # Prevent LSTM gradient explosion

    # Circadian Rhythm
    IDLE_TIMEOUT_MINUTES: int = 5
    MIN_SURPRISE_THRESHOLD: float = 2.5  # Free Energy threshold for plasticity
    MAX_DREAM_LENGTH: int = 2048

    # Buffer
    STEB_CAPACITY_MB: int = 512
