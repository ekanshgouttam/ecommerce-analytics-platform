select
    brand,
    sum(purchases) as purchases,
    round(sum(revenue)::numeric, 2) as revenue
from {{ ref('mart_product_performance') }}
where brand is not null
group by brand
order by revenue desc
limit 10