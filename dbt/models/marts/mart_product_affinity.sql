with session_purchases as (
    select distinct
        user_session,
        product_id
    from {{ ref('int_purchases') }}
    where user_session is not null
),

pairs as (
    select
        a.product_id as product_id_a,
        b.product_id as product_id_b,
        a.user_session
    from session_purchases a
    join session_purchases b
        on a.user_session = b.user_session
        and a.product_id < b.product_id
)

select
    product_id_a,
    product_id_b,
    count(distinct user_session) as co_purchase_count
from pairs
group by product_id_a, product_id_b
having count(distinct user_session) >= 2
order by co_purchase_count desc