from __future__ import annotations

import logging
import sys

from src.experimentation.analyze_experiment import analyze_conversion_rate
from src.experimentation.config import EXPERIMENTS_DIR
from src.experimentation.generate_experiment import generate_ab_test

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
log = logging.getLogger("run_experiment")

EXPERIMENT_NAME = "checkout_button_color_test"


def main() -> int:
    df = generate_ab_test(
        n_per_group=8000,
        control_conversion_rate=0.031,       # close to the real ~3.1% observed rate
        treatment_conversion_rate=0.036,      # a plausible, modest real-world lift
        control_aov_mean=48.0,
        control_aov_std=14.0,
        seed=7,
    )

    out_path = EXPERIMENTS_DIR / f"{EXPERIMENT_NAME}.parquet"
    df.write_parquet(out_path, compression="zstd")
    log.info("Wrote %s rows to %s", f"{df.height:,}", out_path)

    result = analyze_conversion_rate(df)
    log.info(
        "control=%.4f treatment=%.4f lift=%.2f%% p=%.4f significant=%s ci=[%.4f, %.4f]",
        result.control_rate, result.treatment_rate, result.relative_lift * 100,
        result.p_value, result.is_significant, result.ci_low, result.ci_high,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
    