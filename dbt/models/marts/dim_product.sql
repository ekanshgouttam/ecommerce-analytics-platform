select distinct on (product_id)
    product_id,
    category_id,
    category_code,
    brand
from {{ ref('stg_events') }}
order by product_id, event_timestamp desc