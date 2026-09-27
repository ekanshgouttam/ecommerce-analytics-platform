from __future__ import annotations

import logging
import sys

import polars as pl

from src.utils.config import PROCESSED_DIR
from src.utils.db import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
log = logging.getLogger("load_warehouse")

SILVER_PATH = PROCESSED_DIR / "silver" / "events.parquet"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS staging_events (
    event_id BIGINT PRIMARY KEY,
    event_time TEXT,
    event_type TEXT,
    product_id BIGINT,
    category_id BIGINT,
    category_code TEXT,
    brand TEXT,
    price DOUBLE PRECISION,
    user_id BIGINT,
    user_session TEXT,
    event_timestamp TIMESTAMP,
    event_date DATE,
    event_month TEXT
);
"""


def main() -> int:
    log.info("Reading %s", SILVER_PATH)
    df = pl.read_parquet(SILVER_PATH)
    log.info("Loaded %s rows from silver", f"{df.height:,}")

    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            log.info("Creating staging_events table if not exists")
            cur.execute(CREATE_TABLE_SQL)
            cur.execute("TRUNCATE staging_events")

            cols = df.columns
            copy_sql = f"COPY staging_events ({', '.join(cols)}) FROM STDIN"
            log.info("Copying %s rows into staging_events ...", f"{df.height:,}")
            with cur.copy(copy_sql) as copy:
                for row in df.iter_rows():
                    copy.write_row(row)

    conn.close()
    log.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())