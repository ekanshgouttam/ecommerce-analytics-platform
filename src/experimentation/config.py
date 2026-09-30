from pathlib import Path

from src.utils.config import PROJECT_ROOT

EXPERIMENTS_DIR = PROJECT_ROOT / "data" / "experiments"
EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)

# Default simulation parameters — override per experiment run.
DEFAULT_N_PER_GROUP = 5000
DEFAULT_BASELINE_CONVERSION_RATE = 0.03   # matches the real ~3% observed rate
DEFAULT_RANDOM_SEED = 42