select
    date_trunc('month', event_date)::date as month_start,
    count(*) as purchases,
    count(distinct user_id) as buyers,
    round(sum(price)::numeric, 2) as revenue
from {{ ref('fact_events') }}
where event_type = 'purchase'
group by date_trunc('month', event_date)::date
order by month_start