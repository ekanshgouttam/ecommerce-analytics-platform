from __future__ import annotations

import numpy as np
import polars as pl

from src.experimentation.config import DEFAULT_RANDOM_SEED


def generate_ab_test(
    n_per_group: int,
    control_conversion_rate: float,
    treatment_conversion_rate: float,
    control_aov_mean: float = 50.0,
    control_aov_std: float = 15.0,
    treatment_aov_mean: float | None = None,
    treatment_aov_std: float | None = None,
    seed: int = DEFAULT_RANDOM_SEED,
) -> pl.DataFrame:
    """
    Simulate a simple two-arm A/B test: each simulated user is assigned to
    control or treatment, gets a Bernoulli-distributed conversion outcome
    at the specified rate, and — if converted — an order value drawn from
    a normal distribution (clipped at 0, since revenue can't be negative).

    This is synthetic data for testing the experimentation *pipeline*
    (stats, confidence intervals, dashboarding) — it is not derived from
    or mixed with the real REES46 observational data.
    """
    rng = np.random.default_rng(seed)

    if treatment_aov_mean is None:
        treatment_aov_mean = control_aov_mean
    if treatment_aov_std is None:
        treatment_aov_std = control_aov_std

    rows = []
    for group, conv_rate, aov_mean, aov_std in (
        ("control", control_conversion_rate, control_aov_mean, control_aov_std),
        ("treatment", treatment_conversion_rate, treatment_aov_mean, treatment_aov_std),
    ):
        converted = rng.binomial(1, conv_rate, size=n_per_group)
        order_value = np.where(
            converted == 1,
            np.clip(rng.normal(aov_mean, aov_std, size=n_per_group), 0, None),
            0.0,
        )
        for i in range(n_per_group):
            rows.append({
                "user_id": f"{group}_{i}",
                "group": group,
                "converted": int(converted[i]),
                "order_value": round(float(order_value[i]), 2),
            })

    return pl.DataFrame(rows)


if __name__ == "__main__":
    df = generate_ab_test(
        n_per_group=5000,
        control_conversion_rate=0.03,
        treatment_conversion_rate=0.035,
    )
    print(df.head())
    print(df.group_by("group").agg(
        pl.col("converted").sum().alias("conversions"),
        pl.col("converted").mean().alias("conversion_rate"),
        pl.col("order_value").filter(pl.col("converted") == 1).mean().alias("avg_order_value_among_converters"),
    ))