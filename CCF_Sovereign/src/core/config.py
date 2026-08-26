from dataclasses import dataclass
from enum import Enum


class SystemState(Enum):
    AWAKE = "AWAKE"
    NREM = "NREM"
    REM = "REM"
    VALIDATE = "VALIDATE"
    # Legacy aliases kept for older call sites / docs.
    DEEP_SLEEP = "NREM"
    DREAMING = "REM"


@dataclass
class SovereignConfig:
    # Hardware Constraints
    MAX_VRAM_GB: int = 24
    USE_QUANTIZATION_NF4: bool = True

    # Model Architecture
    MODEL_DIM: int = 4096
    STATE_DIM: int = 512
    NUM_LAYERS: int = 8
    VOCAB_SIZE: int = 50257

    # Mamba SSM Parameters
    MAMBA_D_STATE: int = 16
    MAMBA_D_CONV: int = 4
    MAMBA_EXPAND: int = 2
    MAMBA_DROPOUT: float = 0.1

    # Holographic Memory
    HRR_DIM: int = 4096
    ORTHOGONALITY_THRESHOLD: float = 0.05

    # Plasticity & Learning
    HEBBIAN_LEARNING_RATE: float = 0.001
    SLEEP_LEARNING_RATE: float = 1e-5
    TRAINING_LEARNING_RATE: float = 3e-4
    GALORE_RANK: int = 128
    GRADIENT_CLIP_NORM: float = 1.0

    # Circadian Rhythm / Sleep Architecture v0.1
    IDLE_TIMEOUT_MINUTES: float = 5.0
    MIN_SURPRISE_THRESHOLD: float = 2.5
    MAX_DREAM_LENGTH: int = 2048
    FORCE_SLEEP_ON_HARD_SATURATION: bool = True

    # Saturation (measurable sleep pressure)
    SATURATION_SOFT_THRESHOLD: float = 0.55
    SATURATION_HARD_THRESHOLD: float = 0.85
    SATURATION_STEB_SOFT_FILL: float = 0.50
    SATURATION_STEB_HARD_FILL: float = 0.90
    SATURATION_DRIFT_NORM: float = 5.0
    SATURATION_DRIFT_SOFT: float = 1.5
    SATURATION_CONFLICT_NORM: float = 2.0
    SATURATION_CONFLICT_SOFT: float = 0.8
    SATURATION_NOVELTY_SOFT: float = 0.40
    SATURATION_SURPRISE_WINDOW: int = 128
    SATURATION_W_FILL: float = 0.30
    SATURATION_W_SURPRISE: float = 0.15
    SATURATION_W_ENTROPY: float = 0.10
    SATURATION_W_DRIFT: float = 0.20
    SATURATION_W_NOVELTY: float = 0.15
    SATURATION_W_CONFLICT: float = 0.10

    # NREM
    NREM_EPOCHS: int = 3
    NREM_KEEP_FRACTION: float = 0.7
    NREM_FAST_WEIGHT_DECAY: float = 0.5

    # REM
    REM_MAX_CANDIDATES: int = 4
    REM_GENERATE_TOKENS: int = 24
    REM_MAX_SEED_TOKENS: int = 64
    REM_TEMPERATURE: float = 0.9

    # Validate
    VALIDATE_PROMOTE_THRESHOLD: float = 0.55
    VALIDATE_REJECT_THRESHOLD: float = 0.35
    VALIDATE_CONDITION_PREFIX: int = 16
    VALIDATE_SCORE_SCALE: float = 2.0
    VALIDATE_MAX_DREAM_NLL: float = 12.0
    VALIDATE_TRAIN_PROMOTED: bool = True

    # Persistence
    DATA_ROOT: str = "data"
    CODEX_DIRNAME: str = "forever_law"
    CANONICAL_DIRNAME: str = "canonical"

    # Buffer
    STEB_CAPACITY_MB: int = 512
    STEB_MAX_EPISODES: int = 512

    @classmethod
    def operator(cls) -> "SovereignConfig":
        """
        Interactive / operator profile.

        Full 4096-D growth configs remain the research default; this profile is
        what the desktop operator surface boots so Sleep Now is usable on a
        single workstation without pretending a hyperscale model is present.
        """
        return cls(
            MODEL_DIM=256,
            STATE_DIM=128,
            NUM_LAYERS=2,
            VOCAB_SIZE=50257,
            MAMBA_D_STATE=16,
            MAMBA_D_CONV=4,
            MAMBA_EXPAND=2,
            MAMBA_DROPOUT=0.0,
            HRR_DIM=256,
            GALORE_RANK=32,
            SLEEP_LEARNING_RATE=1e-4,
            HEBBIAN_LEARNING_RATE=1e-3,
            MIN_SURPRISE_THRESHOLD=2.0,
            IDLE_TIMEOUT_MINUTES=5.0,
            NREM_EPOCHS=2,
            REM_MAX_CANDIDATES=3,
            REM_GENERATE_TOKENS=16,
            STEB_MAX_EPISODES=128,
            DATA_ROOT="data",
        )
