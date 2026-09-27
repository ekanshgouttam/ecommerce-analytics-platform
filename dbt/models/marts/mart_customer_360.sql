with session_stats as (
    select
        user_id,
        count(*) as total_sessions,
        avg(event_count) as avg_events_per_session,
        sum(purchase_count) as total_purchase_events,
        sum(session_revenue) as total_revenue,
        count(*) filter (where had_purchase) as converting_sessions
    from {{ ref('int_sessions') }}
    group by user_id
),

recency as (
    select
        user_id,
        max(event_timestamp) as last_seen_at,
        min(event_timestamp) as first_seen_at
    from {{ ref('stg_events') }}
    group by user_id
)

select
    r.user_id,
    r.first_seen_at,
    r.last_seen_at,
    date_part('day', r.last_seen_at - r.first_seen_at) as customer_lifespan_days,
    s.total_sessions,
    round(s.avg_events_per_session::numeric, 2) as avg_events_per_session,
    s.converting_sessions,
    case when s.total_sessions > 0
        then round(s.converting_sessions::numeric / s.total_sessions, 4)
        else 0
    end as session_conversion_rate,
    coalesce(s.total_revenue, 0) as lifetime_value,
    case when s.converting_sessions > 0
        then round((coalesce(s.total_revenue, 0) / s.converting_sessions)::numeric, 2)
        else 0
    end as avg_order_value
from recency r
join session_stats s on r.user_id = s.user_id
order by lifetime_value desc