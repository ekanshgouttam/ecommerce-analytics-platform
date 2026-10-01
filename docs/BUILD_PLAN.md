# Build Plan — Status

## Pipeline (raw → warehouse)
| Step | Status |
|------|--------|
| Validate raw .zip sources | Done |
| Ingest + extract | Done |
| Bronze (partitioned Parquet) | Done |
| Silver (dedup, filter, derive columns) | Done |
| Load PostgreSQL warehouse | Done |

## dbt models
| Layer | Models | Status |
|-------|--------|--------|
| Staging | stg_events | Done |
| Intermediate | int_sessions, int_purchases | Done |
| Dimensions/Facts | dim_product, dim_category, dim_customer, dim_date, fact_events, fact_purchases | Done |
| Analytics marts | mart_product_performance, mart_customer_360, mart_session_funnel, mart_customer_cohort, mart_product_affinity, mart_brand_revenue, mart_monthly_revenue, mart_funnel_stages | Done |
| Experimentation marts | mart_experiment_results, mart_experiment_analysis | Done |
| dbt tests | unique/not_null/accepted_values/relationships on staging + marts | Done — 17 tests passing |

## Experimentation module
| Piece | Status |
|-------|--------|
| Synthetic A/B data generator | Done |
| Two-proportion z-test + confidence interval | Done |
| Unit tests (null case + true-effect case) | Done |
| Warehouse load + dbt summary models | Done |

## Power BI dashboards
| Dashboard | Status |
|-----------|--------|
| Executive Overview | Done |
| Product Performance | Done |
| Customer 360 | Done |
| Session Funnel | Done |
| Experiment Results | Done |

## Infrastructure
| Piece | Status |
|-------|--------|
| Docker Compose (PostgreSQL) | Done |
| GitHub Actions CI (pytest on push) | Done |
| Data dictionary | Done |
| Decisions log | Done |

## Known data-quality caveats (by design, not bugs)
- `category_code` is null in ~98% of raw rows; `brand` in ~40%. Revenue-by-category chart is filtered to categorized products only and labeled as such.
- A handful of rows (~124 total) had negative prices in the raw data — filtered out in Silver, not in Bronze (Bronze preserves raw data as-is).
- A few category codes (`furniture.living_room.cabinet`, `appliances.environment.vacuum`) appear in this cosmetics dataset — likely source-side taxonomy noise, not a pipeline bug.
- Later cohort months (Dec 2019 onward) show fewer populated retention columns simply due to less elapsed time in the 5-month dataset window, not because retention improved.