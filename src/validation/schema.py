import pandera as pa
from pandera import Column, Check, DataFrameSchema

from src.utils.config import VALID_EVENT_TYPES

raw_event_schema = DataFrameSchema(
    {
        "event_time": Column(str, nullable=False),
        "event_type": Column(str, checks=Check.isin(VALID_EVENT_TYPES), nullable=False),
        "product_id": Column("int64", checks=Check.greater_than(0), nullable=False),
        "category_id": Column("int64", nullable=False),
        "category_code": Column(str, nullable=True),
        "brand": Column(str, nullable=True),
        "price": Column(float, checks=Check.greater_than_or_equal_to(0), nullable=False),
        "user_id": Column("int64", nullable=False),
        "user_session": Column(str, nullable=True),
    },
    strict=False,
    coerce=True,
)