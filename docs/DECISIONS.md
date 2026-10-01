# Key decisions and fixes

Real judgment calls and bugs caught during the build — kept here because
they're more useful than a feature list for explaining how the project
actually works.

## Data quality
- **Negative prices**: 124 rows across all 5 months had negative prices.
  Decision: keep them in Bronze (raw fidelity), filter them in Silver
  (clean layer). Originally flagged as a hard validation failure, which
  would have blocked ingestion of real data entirely — downgraded to a
  warning once the real scale of the issue (20 out of 4.1M rows in one
  month) was seen.
- **dim_product duplicates**: `product_id` is not actually a stable key —
  the same product_id can carry different `category_id`/brand values
  across events (recategorized or corrected listings over time). A naive
  `SELECT DISTINCT` produced 13,552 duplicate product_ids, caught by a
  dbt `unique` test. Fixed with `DISTINCT ON (product_id) ... ORDER BY
  event_timestamp DESC` to take the most recent attributes per product.
- **category_code / brand nullness**: ~98% / ~40% null respectively in
  raw data. This is a real property of the source, not a pipeline bug.
  Revenue-by-category charts are explicitly filtered and labeled as
  "categorized products only" rather than silently hiding the gap.

## Dashboard integrity
- **Revenue-by-brand Top N**: Power BI's Top N filter, applied to the
  same field used for the "is not blank" filter, replaces rather than
  combines with it — brought the blank-brand bar back. Fixed by moving
  the blank-filtering logic into dbt instead (`mart_brand_revenue`,
  `WHERE brand IS NOT NULL ... LIMIT 10`), keeping that logic
  version-controlled rather than living inside report-level filter state.
- **Smoothed line chart misleading with 5 points**: a 5-month revenue
  trend rendered as a smoothed line implied peaks/dips between months
  that don't exist in the data. Switched to a clustered column chart,
  which doesn't imply interpolation.
- **Two different "conversion rate" definitions**: `mart_session_funnel.
  overall_conversion_rate` = purchases ÷ all sessions. The funnel's
  view→purchase rate = purchases ÷ sessions with a view. These
  legitimately differ (a small share of sessions have no view event) —
  documented on the Funnel dashboard rather than left as an apparent
  inconsistency.

## Experimentation module
- **Kept fully separate from REES46 data**: synthetic experiment data
  lives in its own tables (`experiment_events`, `experiment_analysis`)
  and its own marts, never joined against real observational data, to
  avoid any appearance of mixing simulated and real signals.
- **p-value/CI computed in Python, not SQL**: a two-proportion z-test
  isn't practical in plain SQL. `mart_experiment_results` (per-group
  aggregates) is pure dbt/SQL; the statistical test itself runs in
  `analyze_experiment.py` (SciPy) and its output is persisted to
  Postgres (`experiment_analysis`) so the dashboard can read a finished
  result rather than needing a live Python process.
- **Verified against both the null and true-effect case**: a 3% vs 3.5%
  simulated test correctly came back non-significant (underpowered at
  n=5000/group); a 3% vs 6% test correctly came back significant
  (p≈4.6e-9). Both cases are locked in as unit tests.