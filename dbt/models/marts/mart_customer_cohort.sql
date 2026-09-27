with first_purchase as (
    select
        user_id,
        date_trunc('month', min(event_timestamp)) as cohort_month
    from {{ ref('int_purchases') }}
    group by user_id
),

purchase_months as (
    select
        user_id,
        date_trunc('month', event_timestamp) as activity_month
    from {{ ref('int_purchases') }}
    group by user_id, date_trunc('month', event_timestamp)
),

cohort_activity as (
    select
        fp.cohort_month,
        pm.user_id,
        (date_part('year', pm.activity_month) - date_part('year', fp.cohort_month)) * 12
            + (date_part('month', pm.activity_month) - date_part('month', fp.cohort_month)) as month_number
    from purchase_months pm
    join first_purchase fp on pm.user_id = fp.user_id
),

cohort_sizes as (
    select cohort_month, count(distinct user_id) as cohort_size
    from first_purchase
    group by cohort_month
)

select
    ca.cohort_month,
    ca.month_number,
    count(distinct ca.user_id) as active_customers,
    cs.cohort_size,
    round(count(distinct ca.user_id)::numeric / nullif(cs.cohort_size, 0), 4) as retention_rate
from cohort_activity ca
join cohort_sizes cs on ca.cohort_month = cs.cohort_month
group by ca.cohort_month, ca.month_number, cs.cohort_size
order by ca.cohort_month, ca.month_number