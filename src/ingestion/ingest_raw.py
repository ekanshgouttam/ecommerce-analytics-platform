from __future__ import annotations

import argparse
import logging
import sys
import zipfile
from pathlib import Path

import polars as pl

from src.utils.config import BRONZE_DIR, RAW_DIR, RAW_FILENAMES
from src.validation.polars_checks import SchemaValidationError, validate_raw_events

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s")
log = logging.getLogger("ingest_raw")

EXTRACTED_DIR = RAW_DIR / "_extracted"
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)


def _extract_csv_from_zip(zip_path: Path) -> Path:
    extracted_path = EXTRACTED_DIR / f"{zip_path.stem}.csv"
    if extracted_path.exists():
        return extracted_path

    with zipfile.ZipFile(zip_path) as zf:
        csv_members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_members:
            raise SchemaValidationError(f"{zip_path.name}: no .csv file found inside zip")
        if len(csv_members) > 1:
            log.warning("%s: zip contains %d CSVs, using the first: %s",
                        zip_path.name, len(csv_members), csv_members[0])
        member = csv_members[0]
        log.info("Extracting %s from %s ...", member, zip_path.name)
        with zf.open(member) as src, open(extracted_path, "wb") as dst:
            dst.write(src.read())

    return extracted_path


def _read_raw_csv(path: Path) -> pl.DataFrame:
    return pl.read_csv(
        path,
        schema_overrides={
            "event_time": pl.Utf8,
            "event_type": pl.Utf8,
            "product_id": pl.Int64,
            "category_id": pl.Int64,
            "category_code": pl.Utf8,
            "brand": pl.Utf8,
            "price": pl.Float64,
            "user_id": pl.Int64,
            "user_session": pl.Utf8,
        },
        try_parse_dates=False,
        null_values=["", "NULL", "null"],
    )

def _year_month_from_filename(file_name: str) -> tuple[int, str]:
    stem = file_name.split(".")[0]  # "2019-Oct.csv.zip" -> "2019-Oct"
    year_str, month_str = stem.split("-")
    return int(year_str), month_str


def ingest_file(file_name: str) -> bool:
    src_path = RAW_DIR / file_name

    if not src_path.exists():
        log.error("MISSING raw file: %s (expected at %s)", file_name, src_path)
        return False
    if src_path.stat().st_size == 0:
        log.error("EMPTY raw file: %s", file_name)
        return False
    if not zipfile.is_zipfile(src_path):
        log.error("%s does not look like a valid zip archive", file_name)
        return False

    try:
        csv_path = _extract_csv_from_zip(src_path)
    except SchemaValidationError as exc:
        log.error(str(exc))
        return False

    log.info("Reading %s ...", csv_path.name)
    df = _read_raw_csv(csv_path)
    log.info("%s: %s rows read", file_name, f"{df.height:,}")

    report = validate_raw_events(df, file_name=file_name)
    for warning in report.warnings:
        log.warning("%s: %s", file_name, warning)

    try:
        report.raise_if_failed()
    except SchemaValidationError as exc:
        log.error(str(exc))
        return False

    year, month = _year_month_from_filename(file_name)
    out_dir = BRONZE_DIR / f"year={year}" / f"month={month}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "events.parquet"

    df.write_parquet(out_path, compression="zstd")
    log.info("%s -> %s (%.1f MB)", file_name, out_path, out_path.stat().st_size / 1e6)
    return True


def main(files: list[str]) -> int:
    log.info("Ingesting %d file(s) into %s", len(files), BRONZE_DIR)
    results = {f: ingest_file(f) for f in files}

    n_ok = sum(results.values())
    n_fail = len(results) - n_ok
    log.info("Done: %d succeeded, %d failed", n_ok, n_fail)

    if n_fail > 0:
        log.error("Failed files: %s", [f for f, ok in results.items() if not ok])
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", action="append", dest="files",
                         help="Ingest a single named file (repeatable).")
    args = parser.parse_args()
    sys.exit(main(args.files or RAW_FILENAMES))