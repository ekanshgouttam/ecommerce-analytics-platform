import polars as pl
import pytest

from src.validation.polars_checks import SchemaValidationError, validate_raw_events

GOOD_ROW = {
    "event_time": "2019-10-01 00:00:00 UTC",
    "event_type": "view",
    "product_id": 1,
    "category_id": 100,
    "category_code": "electronics.smartphone",
    "brand": "apple",
    "price": 999.0,
    "user_id": 42,
    "user_session": "abc-123",
}


def make_df(**overrides) -> pl.DataFrame:
    row = {**GOOD_ROW, **overrides}
    return pl.DataFrame([row])


def test_valid_row_passes():
    report = validate_raw_events(make_df(), file_name="test.csv")
    assert report.passed
    report.raise_if_failed()


def test_missing_columns_is_hard_failure():
    df = make_df().drop("price")
    report = validate_raw_events(df, file_name="test.csv")
    assert not report.passed
    assert any("missing required columns" in f for f in report.hard_failures)


def test_bad_event_type_is_hard_failure():
    report = validate_raw_events(make_df(event_type="checkout"), file_name="test.csv")
    assert not report.passed
    with pytest.raises(SchemaValidationError):
        report.raise_if_failed()


def test_negative_price_is_soft_warning():
    report = validate_raw_events(make_df(price=-5.0), file_name="test.csv")
    assert report.passed
    assert any("negative price" in w for w in report.warnings)

def test_null_category_code_is_soft_warning_only():
    report = validate_raw_events(make_df(category_code=None), file_name="test.csv")
    assert report.passed
    assert any("category_code" in w for w in report.warnings)


def test_duplicate_rows_are_counted_not_failed():
    df = pl.concat([make_df(), make_df()])
    report = validate_raw_events(df, file_name="test.csv")
    assert report.passed
    assert report.duplicate_rows == 1