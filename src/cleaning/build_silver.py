from __future__ import annotations

import logging
import sys

import polars as pl

from src.utils.config import BRONZE_DIR, PROCESSED_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
log = logging.getLogger("build_silver")

SILVER_DIR = PROCESSED_DIR / "silver"
SILVER_DIR.mkdir(parents=True, exist_ok=True)


def load_all_bronze() -> pl.DataFrame:
    parquet_glob = str(BRONZE_DIR / "year=*" / "month=*" / "events.parquet")
    log.info("Scanning %s", parquet_glob)
    return pl.read_parquet(parquet_glob)


def build_silver(df: pl.DataFrame) -> pl.DataFrame:
    before = df.height

    df = df.unique()
    log.info("Dropped %s exact duplicate rows", f"{before - df.height:,}")

    before = df.height
    df = df.filter(pl.col("price") >= 0)
    log.info("Dropped %s negative-price rows", f"{before - df.height:,}")

    df = df.with_columns(
        pl.col("event_time")
        .str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S %Z")
        .alias("event_timestamp")
    )
    df = df.with_columns(
        pl.col("event_timestamp").dt.date().alias("event_date"),
        pl.col("event_timestamp").dt.strftime("%Y-%m").alias("event_month"),
    )
    df = df.with_row_index(name="event_id")

    return df


def main() -> int:
    df = load_all_bronze()
    log.info("Loaded %s bronze rows", f"{df.height:,}")

    silver = build_silver(df)
    log.info("Silver has %s rows", f"{silver.height:,}")

    out_path = SILVER_DIR / "events.parquet"
    silver.write_parquet(out_path, compression="zstd")
    log.info("Wrote %s (%.1f MB)", out_path, out_path.stat().st_size / 1e6)
    return 0


if __name__ == "__main__":
    sys.exit(main())