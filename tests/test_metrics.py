import numpy as np
import pandas as pd
import pytest

from src.metrics import (
    compute_cohen_kappa,
    compute_confusion_matrix,
    compute_quadratic_weighted_kappa,
    summarize_calibration,
)


def test_cohen_kappa_perfect_agreement():
    human = [0, 1, 2, 0, 1, 2]
    judge = [0, 1, 2, 0, 1, 2]
    assert compute_cohen_kappa(human, judge) == 1.0


def test_cohen_kappa_no_agreement_below_one():
    human = [0, 0, 1, 1, 2, 2]
    judge = [2, 1, 0, 2, 1, 0]
    assert compute_cohen_kappa(human, judge) < 1.0


def test_quadratic_weighted_kappa_penalizes_distance_more_than_plain_kappa():
    # Same number of errors in both cases (8 wrong out of 12), same
    # human/judge label balance - only the *distance* of the errors differs.
    human = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]
    judge_near_miss = [1] * 12  # every error is off by 1 (always predicts the middle class)
    judge_far_miss = [2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0]  # every error is off by 2 (extremes swapped)

    # Unweighted kappa can't see error distance, so it scores both patterns
    # identically - this is exactly the blind spot quadratic weighting fixes.
    assert compute_cohen_kappa(human, judge_near_miss) == pytest.approx(
        compute_cohen_kappa(human, judge_far_miss)
    )

    weighted_near = compute_quadratic_weighted_kappa(human, judge_near_miss)
    weighted_far = compute_quadratic_weighted_kappa(human, judge_far_miss)
    assert weighted_far < weighted_near


def test_confusion_matrix_shape_and_labels():
    human = [0, 1, 2]
    judge = [0, 1, 1]
    matrix = compute_confusion_matrix(human, judge)
    assert list(matrix.index) == ["human_0", "human_1", "human_2"]
    assert list(matrix.columns) == ["judge_0", "judge_1", "judge_2"]
    assert matrix.loc["human_0", "judge_0"] == 1
    assert matrix.loc["human_2", "judge_1"] == 1


def test_summarize_calibration_all_valid():
    human = [0, 1, 2, 0]
    judge = [0, 1, 2, 1]
    summary = summarize_calibration(human, judge)
    assert summary["n_items"] == 4
    assert summary["n_valid"] == 4
    assert summary["n_parse_failures"] == 0
    assert summary["exact_agreement_rate"] == 0.75
    assert summary["cohen_kappa"] is not None
    assert summary["quadratic_weighted_kappa"] is not None


def test_summarize_calibration_excludes_none_judge_scores():
    human = [0, 1, 2, 0]
    judge = [0, None, 2, 1]
    summary = summarize_calibration(human, judge)
    assert summary["n_items"] == 4
    assert summary["n_valid"] == 3
    assert summary["n_parse_failures"] == 1
    assert summary["exact_agreement_rate"] == pytest.approx(2 / 3)


def test_summarize_calibration_excludes_nan_judge_scores():
    # pandas represents missing numeric values as NaN (not None) after a CSV
    # round-trip - missing detection needs to handle both.
    human = pd.Series([0, 1, 2, 0])
    judge = pd.Series([0.0, np.nan, 2.0, 1.0])
    summary = summarize_calibration(human, judge)
    assert summary["n_valid"] == 3
    assert summary["n_parse_failures"] == 1


def test_summarize_calibration_all_missing_returns_none_metrics():
    human = [0, 1, 2]
    judge = [None, None, None]
    summary = summarize_calibration(human, judge)
    assert summary["n_valid"] == 0
    assert summary["n_parse_failures"] == 3
    assert summary["cohen_kappa"] is None
    assert summary["quadratic_weighted_kappa"] is None
    assert summary["exact_agreement_rate"] is None
