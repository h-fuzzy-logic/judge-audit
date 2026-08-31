import numpy as np
import pytest

from src.metrics import compute_cohen_kappa
from src.significance import paired_bootstrap_test


def _exact_match_rate(human, judge):
    return float(np.mean(np.asarray(human) == np.asarray(judge)))


def test_identical_conditions_give_zero_diff_and_p_value_one():
    human = [0, 1, 2] * 20
    judge_a = list(human)
    judge_b = list(human)

    result = paired_bootstrap_test(human, judge_a, judge_b, _exact_match_rate, n_bootstrap=200)

    assert result["observed_diff"] == 0.0
    assert result["ci_lower"] == 0.0
    assert result["ci_upper"] == 0.0
    assert result["p_value"] == 1.0
    assert result["significant_at_0.05"] is False


def test_large_true_difference_is_detected_as_significant():
    human = [0] * 50 + [1] * 50 + [2] * 50
    judge_b = list(human)  # always correct
    judge_a = [(h + 1) % 3 for h in human]  # always wrong

    result = paired_bootstrap_test(human, judge_a, judge_b, _exact_match_rate, n_bootstrap=200)

    assert result["observed_diff"] == pytest.approx(1.0)
    assert result["p_value"] == 0.0
    assert result["significant_at_0.05"] is True
    assert result["ci_lower"] > 0.0


def test_ci_lower_never_exceeds_ci_upper():
    rng = np.random.default_rng(0)
    human = rng.integers(0, 3, size=60).tolist()
    judge_a = rng.integers(0, 3, size=60).tolist()
    judge_b = rng.integers(0, 3, size=60).tolist()

    result = paired_bootstrap_test(human, judge_a, judge_b, _exact_match_rate, n_bootstrap=200)

    assert result["ci_lower"] <= result["ci_upper"]


def test_same_seed_is_reproducible():
    rng = np.random.default_rng(1)
    human = rng.integers(0, 3, size=60).tolist()
    judge_a = rng.integers(0, 3, size=60).tolist()
    judge_b = rng.integers(0, 3, size=60).tolist()

    result_1 = paired_bootstrap_test(human, judge_a, judge_b, _exact_match_rate, n_bootstrap=200, seed=7)
    result_2 = paired_bootstrap_test(human, judge_a, judge_b, _exact_match_rate, n_bootstrap=200, seed=7)

    assert result_1 == result_2


def test_mismatched_lengths_raise():
    with pytest.raises(ValueError):
        paired_bootstrap_test([0, 1, 2], [0, 1], [0, 1, 2], _exact_match_rate, n_bootstrap=10)


def test_empty_input_raises():
    with pytest.raises(ValueError):
        paired_bootstrap_test([], [], [], _exact_match_rate, n_bootstrap=10)


def test_works_with_a_real_project_metric():
    # Smoke test that this composes with src.metrics functions directly,
    # not just a toy metric_fn - this is how it'll actually get used.
    rng = np.random.default_rng(2)
    human = rng.integers(0, 3, size=60).tolist()
    judge_a = rng.integers(0, 3, size=60).tolist()
    judge_b = rng.integers(0, 3, size=60).tolist()

    result = paired_bootstrap_test(human, judge_a, judge_b, compute_cohen_kappa, n_bootstrap=200)

    assert isinstance(result["observed_diff"], float)
    assert isinstance(result["p_value"], float)
    assert 0.0 <= result["p_value"] <= 1.0
