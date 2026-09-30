from __future__ import annotations

import logging
import sys

import polars as pl

from src.experimentation.config import EXPERIMENTS_DIR
from src.utils.db import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
log = logging.getLogger("load_experiment")

EXPERIMENT_NAME = "checkout_button_color_test"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS experiment_events (
    experiment_name TEXT,
    user_id TEXT,
    "group" TEXT,
    converted INTEGER,
    order_value DOUBLE PRECISION
);
"""


def main() -> int:
    path = EXPERIMENTS_DIR / f"{EXPERIMENT_NAME}.parquet"
    df = pl.read_parquet(path)
    df = df.with_columns(pl.lit(EXPERIMENT_NAME).alias("experiment_name"))
    df = df.select(["experiment_name", "user_id", "group", "converted", "order_value"])

    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
            cur.execute("DELETE FROM experiment_events WHERE experiment_name = %s", (EXPERIMENT_NAME,))
            cols = df.columns
            quoted_cols = ", ".join(f'"{c}"' for c in cols)
            copy_sql = f"COPY experiment_events ({quoted_cols}) FROM STDIN"
            with cur.copy(copy_sql) as copy:
                for row in df.iter_rows():
                    copy.write_row(row)
    conn.close()
    log.info("Loaded %s rows into experiment_events", f"{df.height:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())