from dataclasses import dataclass, field

import polars as pl

from src.utils.config import RAW_EVENT_COLUMNS, VALID_EVENT_TYPES


class SchemaValidationError(Exception):
    pass


@dataclass
class ValidationReport:
    file_name: str
    row_count: int
    hard_failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duplicate_rows: int = 0
    null_counts: dict[str, int] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return len(self.hard_failures) == 0

    def raise_if_failed(self) -> None:
        if not self.passed:
            joined = "\n  - ".join(self.hard_failures)
            raise SchemaValidationError(f"{self.file_name} failed schema validation:\n  - {joined}")


def validate_raw_events(df: pl.DataFrame, file_name: str) -> ValidationReport:
    report = ValidationReport(file_name=file_name, row_count=df.height)

    missing_cols = set(RAW_EVENT_COLUMNS) - set(df.columns)
    if missing_cols:
        report.hard_failures.append(f"missing required columns: {sorted(missing_cols)}")
        return report

    bad_event_types = (
        df.filter(~pl.col("event_type").is_in(VALID_EVENT_TYPES))
        .select(pl.col("event_type").unique())
        .to_series()
        .to_list()
    )
    if bad_event_types:
        report.hard_failures.append(f"unexpected event_type values: {bad_event_types}")

    unparseable = df.filter(
        pl.col("event_time").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S %Z", strict=False).is_null()
    ).height
    if unparseable > 0:
        report.hard_failures.append(f"{unparseable} rows have unparseable event_time")

    negative_prices = df.filter(pl.col("price") < 0).height
    if negative_prices > 0:
        report.warnings.append(f"{negative_prices} rows have negative price (will be filtered in Silver)")

    for id_col in ("product_id", "category_id", "user_id"):
        n_null = df.filter(pl.col(id_col).is_null()).height
        if n_null > 0:
            report.hard_failures.append(f"{n_null} rows have null {id_col}")

    report.duplicate_rows = df.height - df.unique().height
    if report.duplicate_rows > 0:
        report.warnings.append(f"{report.duplicate_rows} exact duplicate rows")

    for col in ("category_code", "brand", "user_session"):
        n_null = df.filter(pl.col(col).is_null()).height
        report.null_counts[col] = n_null
        if n_null > 0:
            pct = 100 * n_null / max(df.height, 1)
            report.warnings.append(f"{col} is null in {n_null} rows ({pct:.1f}%)")

    return report