select
    event_id,
    event_timestamp,
    event_date,
    user_id,
    user_session,
    product_id,
    category_id,
    price
from {{ ref('int_purchases') }}