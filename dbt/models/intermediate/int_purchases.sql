select
    event_id,
    event_timestamp,
    event_date,
    event_month,
    user_id,
    user_session,
    product_id,
    category_id,
    category_code,
    brand,
    price
from {{ ref('stg_events') }}
where event_type = 'purchase'