from __future__ import annotations

import logging
import sys

from src.experimentation.analyze_experiment import analyze_conversion_rate
from src.experimentation.config import EXPERIMENTS_DIR
from src.experimentation.load_experiment import EXPERIMENT_NAME
from src.utils.db import get_connection
import polars as pl

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
log = logging.getLogger("save_analysis")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS experiment_analysis (
    experiment_name TEXT PRIMARY KEY,
    control_n INTEGER,
    treatment_n INTEGER,
    control_rate DOUBLE PRECISION,
    treatment_rate DOUBLE PRECISION,
    relative_lift DOUBLE PRECISION,
    p_value DOUBLE PRECISION,
    is_significant BOOLEAN,
    ci_low DOUBLE PRECISION,
    ci_high DOUBLE PRECISION
);
"""


def main() -> int:
    path = EXPERIMENTS_DIR / f"{EXPERIMENT_NAME}.parquet"
    df = pl.read_parquet(path)
    result = analyze_conversion_rate(df)

    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            cur.execute(
                """
                INSERT INTO experiment_analysis
                    (experiment_name, control_n, treatment_n, control_rate, treatment_rate,
                     relative_lift, p_value, is_significant, ci_low, ci_high)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (experiment_name) DO UPDATE SET
                    control_n = EXCLUDED.control_n,
                    treatment_n = EXCLUDED.treatment_n,
                    control_rate = EXCLUDED.control_rate,
                    treatment_rate = EXCLUDED.treatment_rate,
                    relative_lift = EXCLUDED.relative_lift,
                    p_value = EXCLUDED.p_value,
                    is_significant = EXCLUDED.is_significant,
                    ci_low = EXCLUDED.ci_low,
                    ci_high = EXCLUDED.ci_high
                """,
                (
                    EXPERIMENT_NAME, result.control_n, result.treatment_n,
                    result.control_rate, result.treatment_rate, result.relative_lift,
                    result.p_value, result.is_significant, result.ci_low, result.ci_high,
                ),
            )
    conn.close()
    log.info("Saved analysis for %s", EXPERIMENT_NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main())