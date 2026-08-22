"""Agreement metrics between human labels and judge scores."""
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix


def compute_cohen_kappa(human_scores, judge_scores) -> float:
    return cohen_kappa_score(human_scores, judge_scores)


def compute_quadratic_weighted_kappa(human_scores, judge_scores) -> float:
    return cohen_kappa_score(human_scores, judge_scores, weights="quadratic")


def compute_exact_agreement_rate(human_scores, judge_scores) -> float:
    return float(np.mean([h == j for h, j in zip(human_scores, judge_scores)]))


# Scalar agreement metrics: name -> (human_scores, judge_scores) -> float.
# Add a new metric by adding one entry here - summarize_calibration picks it
# up automatically, no other code needs to change. Metrics that don't fit
# this (human, judge) -> float shape, like the confusion matrix below, stay
# as their own standalone functions instead of being forced into the registry.
METRICS = {
    "cohen_kappa": compute_cohen_kappa,
    "quadratic_weighted_kappa": compute_quadratic_weighted_kappa,
    "exact_agreement_rate": compute_exact_agreement_rate,
}


def compute_confusion_matrix(
    human_scores,
    judge_scores,
    labels=(0, 1, 2),
    row_name: str = "human",
    col_name: str = "judge",
    label_sep: str = "_",
) -> pd.DataFrame:
    matrix = confusion_matrix(human_scores, judge_scores, labels=list(labels))
    return pd.DataFrame(
        matrix,
        index=[f"{row_name}{label_sep}{label}" for label in labels],
        columns=[f"{col_name}{label_sep}{label}" for label in labels],
    )


def summarize_calibration(human_scores, judge_scores) -> dict:
    """Aggregate agreement metrics for one (provider, prompt) group.

    judge_scores may contain missing values (None/NaN) for rows the judge's
    output couldn't be parsed - those are excluded from the metric math but
    counted separately, since a judge's parse-failure rate is its own
    calibration signal, not something to silently drop.
    """
    n_items = len(human_scores)
    valid_mask = [not pd.isna(j) for j in judge_scores]
    valid_human = [h for h, v in zip(human_scores, valid_mask) if v]
    valid_judge = [int(j) for j, v in zip(judge_scores, valid_mask) if v]
    n_valid = len(valid_human)

    summary = {
        "n_items": n_items,
        "n_valid": n_valid,
        "n_parse_failures": n_items - n_valid,
    }
    for name, metric_fn in METRICS.items():
        summary[name] = metric_fn(valid_human, valid_judge) if n_valid else None

    return summary
