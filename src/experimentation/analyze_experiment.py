from __future__ import annotations

from dataclasses import dataclass

import polars as pl
from scipy import stats


@dataclass
class ExperimentResult:
    control_n: int
    treatment_n: int
    control_conversions: int
    treatment_conversions: int
    control_rate: float
    treatment_rate: float
    relative_lift: float
    p_value: float
    is_significant: bool
    ci_low: float
    ci_high: float


def analyze_conversion_rate(df: pl.DataFrame, alpha: float = 0.05) -> ExperimentResult:
    """
    Two-proportion z-test on conversion rate between control and treatment,
    with a Wald confidence interval on the difference in proportions.
    """
    control = df.filter(pl.col("group") == "control")
    treatment = df.filter(pl.col("group") == "treatment")

    n_c, n_t = control.height, treatment.height
    x_c = control["converted"].sum()
    x_t = treatment["converted"].sum()

    p_c = x_c / n_c
    p_t = x_t / n_t

    # Pooled proportion for the z-test under H0: p_c == p_t
    p_pool = (x_c + x_t) / (n_c + n_t)
    se_pool = (p_pool * (1 - p_pool) * (1 / n_c + 1 / n_t)) ** 0.5
    z = (p_t - p_c) / se_pool if se_pool > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Unpooled standard error for the confidence interval on the difference
    se_diff = (p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t) ** 0.5
    z_crit = stats.norm.ppf(1 - alpha / 2)
    diff = p_t - p_c
    ci_low = diff - z_crit * se_diff
    ci_high = diff + z_crit * se_diff

    relative_lift = (p_t - p_c) / p_c if p_c > 0 else float("nan")

    return ExperimentResult(
        control_n=n_c,
        treatment_n=n_t,
        control_conversions=x_c,
        treatment_conversions=x_t,
        control_rate=p_c,
        treatment_rate=p_t,
        relative_lift=relative_lift,
        p_value=p_value,
        is_significant=p_value < alpha,
        ci_low=ci_low,
        ci_high=ci_high,
    )


if __name__ == "__main__":
    from src.experimentation.generate_experiment import generate_ab_test

    df = generate_ab_test(
        n_per_group=5000,
        control_conversion_rate=0.03,
        treatment_conversion_rate=0.035,
    )
    result = analyze_conversion_rate(df)
    print(result)