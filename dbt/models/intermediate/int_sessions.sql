with events as (
    select * from {{ ref('stg_events') }}
)

select
    user_session,
    user_id,
    min(event_timestamp) as session_start,
    max(event_timestamp) as session_end,
    count(*) as event_count,
    count(*) filter (where event_type = 'view') as view_count,
    count(*) filter (where event_type = 'cart') as cart_count,
    count(*) filter (where event_type = 'remove_from_cart') as remove_from_cart_count,
    count(*) filter (where event_type = 'purchase') as purchase_count,
    sum(price) filter (where event_type = 'purchase') as session_revenue,
    max(case when event_type = 'view' then 1 else 0 end) = 1 as had_view,
    max(case when event_type = 'cart' then 1 else 0 end) = 1 as had_cart,
    max(case when event_type = 'purchase' then 1 else 0 end) = 1 as had_purchase
from events
where user_session is not null
group by user_session, user_id