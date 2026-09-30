from src.experimentation.generate_experiment import generate_ab_test
from src.experimentation.analyze_experiment import analyze_conversion_rate


def test_no_true_difference_is_not_significant():
    df = generate_ab_test(
        n_per_group=5000,
        control_conversion_rate=0.03,
        treatment_conversion_rate=0.03,
        seed=1,
    )
    result = analyze_conversion_rate(df)
    assert not result.is_significant
    assert result.ci_low < 0 < result.ci_high


def test_large_true_difference_is_significant():
    df = generate_ab_test(
        n_per_group=5000,
        control_conversion_rate=0.03,
        treatment_conversion_rate=0.06,
        seed=1,
    )
    result = analyze_conversion_rate(df)
    assert result.is_significant
    assert result.ci_low > 0
    assert result.treatment_rate > result.control_rate


def test_sample_sizes_match_input():
    df = generate_ab_test(n_per_group=1000, control_conversion_rate=0.05, treatment_conversion_rate=0.05, seed=1)
    result = analyze_conversion_rate(df)
    assert result.control_n == 1000
    assert result.treatment_n == 1000
    