select
    user_id,
    min(event_timestamp) as first_seen_at,
    max(event_timestamp) as last_seen_at,
    count(distinct user_session) as total_sessions,
    count(*) filter (where event_type = 'purchase') as total_purchases,
    sum(price) filter (where event_type = 'purchase') as lifetime_value
from {{ ref('stg_events') }}
group by user_id