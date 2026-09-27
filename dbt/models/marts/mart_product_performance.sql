with product_attrs as (
    -- product_id can have multiple category/brand values in raw data
    -- (miscategorized or changed listings) — pick the most recent one
    -- per product rather than joining dim_product directly, which could
    -- fan out on duplicate product_id rows.
    select distinct on (product_id)
        product_id,
        category_id,
        category_code,
        brand
    from {{ ref('stg_events') }}
    order by product_id, event_timestamp desc
),

product_events as (
    select
        product_id,
        count(*) filter (where event_type = 'view') as views,
        count(*) filter (where event_type = 'cart') as carts,
        count(*) filter (where event_type = 'remove_from_cart') as removes_from_cart,
        count(*) filter (where event_type = 'purchase') as purchases,
        coalesce(sum(price) filter (where event_type = 'purchase'), 0) as revenue
    from {{ ref('fact_events') }}
    group by product_id
)

select
    a.product_id,
    a.category_id,
    a.category_code,
    a.brand,
    pe.views,
    pe.carts,
    pe.removes_from_cart,
    pe.purchases,
    pe.revenue,
    case when pe.views > 0 then round(pe.purchases::numeric / pe.views, 4) else 0 end as view_to_purchase_rate,
    case when pe.carts > 0 then round(pe.purchases::numeric / pe.carts, 4) else 0 end as cart_to_purchase_rate
from product_attrs a
join product_events pe on a.product_id = pe.product_id
order by pe.revenue desc