# Data Dictionary

## Source: REES46 Cosmetics Shop events
Raw columns per event (one row per view/cart/remove_from_cart/purchase action):

| Column | Type | Notes |
|--------|------|-------|
| event_time | string → timestamp | Format: `YYYY-MM-DD HH:MM:SS UTC` |
| event_type | string | One of: view, cart, remove_from_cart, purchase |
| product_id | int | |
| category_id | int | |
| category_code | string, nullable | ~98% null in raw data |
| brand | string, nullable | ~40% null in raw data |
| price | float | A few rows (~124 total) had negative prices; filtered in Silver |
| user_id | int | |
| user_session | string, nullable | |

## Warehouse tables (PostgreSQL)

### staging_events
Raw Silver-layer load: deduped, negative prices removed, derived `event_id`, `event_date`, `event_month` added.

### Core dims/facts (dbt)
| Table | Grain | Key column(s) |
|-------|-------|---------------|
| dim_product | one row per product_id | product_id (most recent category/brand kept) |
| dim_category | one row per category_id | category_id |
| dim_customer | one row per user_id | user_id |
| dim_date | one row per calendar date in dataset | date_day |
| fact_events | one row per raw event | event_id |
| fact_purchases | one row per purchase event | event_id |

### Analytics marts
| Mart | Grain | Key metrics |
|------|-------|-------------|
| mart_product_performance | per product | views, carts, purchases, revenue, conversion rates |
| mart_customer_360 | per customer | lifetime_value, total_sessions, session_conversion_rate, avg_order_value |
| mart_session_funnel | single row (whole dataset) | stage counts and stage-to-stage % |
| mart_funnel_stages | one row per funnel stage (3 rows) | stage, session_count — long format for charting |
| mart_customer_cohort | per cohort_month × month_number | retention_rate |
| mart_product_affinity | per product pair | co_purchase_count (pairs co-purchased ≥2 times) |
| mart_brand_revenue | per brand (top 10) | purchases, revenue |
| mart_monthly_revenue | per calendar month | purchases, buyers, revenue |

### Experimentation tables
| Table | Grain | Notes |
|-------|-------|-------|
| experiment_events | one row per simulated user | Synthetic only — never mixed with REES46 data |
| experiment_analysis | one row per experiment | Stores p-value, CI, significance (computed in Python, not SQL) |
| mart_experiment_results | per experiment × group | conversion_rate, avg_order_value |
| mart_experiment_analysis | per experiment | Staged version of experiment_analysis |

## Known caveats
See `docs/BUILD_PLAN.md`, "Known data-quality caveats" section.