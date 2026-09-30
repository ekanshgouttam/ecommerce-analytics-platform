with base as (
    select
        experiment_name,
        "group",
        converted,
        order_value
    from experiment_events
),

group_stats as (
    select
        experiment_name,
        "group",
        count(*) as n,
        sum(converted) as conversions,
        avg(converted::numeric) as conversion_rate,
        avg(order_value) filter (where converted = 1) as avg_order_value
    from base
    group by experiment_name, "group"
)

select
    experiment_name,
    "group",
    n,
    conversions,
    round(conversion_rate, 4) as conversion_rate,
    round(avg_order_value::numeric, 2) as avg_order_value
from group_stats
order by experiment_name, "group"