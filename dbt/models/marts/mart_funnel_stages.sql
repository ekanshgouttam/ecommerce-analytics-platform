select 'Sessions with View' as stage, 1 as stage_order, sessions_with_view as session_count
from {{ ref('mart_session_funnel') }}
union all
select 'Sessions to Cart', 2, sessions_view_to_cart
from {{ ref('mart_session_funnel') }}
union all
select 'Sessions to Purchase', 3, sessions_view_to_cart_to_purchase
from {{ ref('mart_session_funnel') }}
order by stage_order