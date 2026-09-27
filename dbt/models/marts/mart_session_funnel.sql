with funnel_base as (
    select
        had_view,
        had_cart,
        had_purchase
    from {{ ref('int_sessions') }}
),

totals as (
    select
        count(*) as total_sessions,
        count(*) filter (where had_view) as sessions_with_view,
        count(*) filter (where had_view and had_cart) as sessions_view_to_cart,
        count(*) filter (where had_view and had_cart and had_purchase) as sessions_view_to_cart_to_purchase,
        count(*) filter (where had_purchase) as sessions_with_purchase
    from funnel_base
)

select
    total_sessions,
    sessions_with_view,
    sessions_view_to_cart,
    sessions_view_to_cart_to_purchase,
    sessions_with_purchase,
    round(sessions_with_view::numeric / nullif(total_sessions, 0), 4) as pct_view,
    round(sessions_view_to_cart::numeric / nullif(sessions_with_view, 0), 4) as pct_view_to_cart,
    round(sessions_view_to_cart_to_purchase::numeric / nullif(sessions_view_to_cart, 0), 4) as pct_cart_to_purchase,
    round(sessions_with_purchase::numeric / nullif(total_sessions, 0), 4) as overall_conversion_rate
from totals