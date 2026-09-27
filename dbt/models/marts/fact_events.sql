select
    event_id,
    event_timestamp,
    event_date,
    event_type,
    user_id,
    user_session,
    product_id,
    category_id,
    price
from {{ ref('stg_events') }}