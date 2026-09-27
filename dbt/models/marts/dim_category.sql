select distinct
    category_id,
    category_code
from {{ ref('stg_events') }}
where category_code is not null