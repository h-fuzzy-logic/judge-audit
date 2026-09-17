"""Agreement metrics between human labels and judge scores."""
from functools import partial

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix


def compute_cohen_kappa(human_scores, judge_scores) -> float:
    return cohen_kappa_score(human_scores, judge_scores)


def compute_quadratic_weighted_kappa(human_scores, judge_scores) -> float:
    return cohen_kappa_score(human_scores, judge_scores, weights="quadratic")


def compute_exact_agreement_rate(human_scores, judge_scores) -> float:
    return float(np.mean([h == j for h, j in zip(human_scores, judge_scores, strict=True)]))


def compute_recall_for_class(human_scores, judge_scores, label: int):
    """Of items whose human label is `label`, what fraction did the judge
    also score as `label`. None (not 0.0) if that class doesn't appear in
    human_scores at all, since recall is undefined with no denominator, not
    zero.
    """
    human = np.asarray(human_scores)
    judge = np.asarray(judge_scores)
    mask = human == label
    if not mask.any():
        return None
    return float(np.mean(judge[mask] == label))


def compute_precision_for_class(human_scores, judge_scores, label: int):
    """Of items the judge scored as `label`, what fraction actually have
    that human label. None (not 0.0) if the judge never predicted that
    class, since precision is undefined with no denominator, not zero.
    """
    human = np.asarray(human_scores)
    judge = np.asarray(judge_scores)
    mask = judge == label
    if not mask.any():
        return None
    return float(np.mean(human[mask] == label))


# Scalar agreement metrics: name -> (human_scores, judge_scores) -> float.
# Add a new metric by adding one entry here - summarize_calibration picks it
# up automatically, no other code needs to change. Metrics that don't fit
# this (human, judge) -> float shape, like the confusion matrix below, stay
# as their own standalone functions instead of being forced into the registry.
#
# recall_class_0 / precision_class_0 are registered here rather than a task-
# specific "ungrounded_recall" name, since this module stays task-agnostic;
# what class 0 *means* (e.g. "Ungrounded") is defined per-experiment, not
# here. For a hallucination-detection task specifically, class 0 recall is
# the safety-critical number: a miss there means the judge waved through a
# fabricated or contradictory response as acceptable.
METRICS = {
    "cohen_kappa": compute_cohen_kappa,
    "quadratic_weighted_kappa": compute_quadratic_weighted_kappa,
    "exact_agreement_rate": compute_exact_agreement_rate,
    "recall_class_0": partial(compute_recall_for_class, label=0),
    "precision_class_0": partial(compute_precision_for_class, label=0),
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
    valid_human = [h for h, v in zip(human_scores, valid_mask, strict=True) if v]
    valid_judge = [int(j) for j, v in zip(judge_scores, valid_mask, strict=True) if v]
    n_valid = len(valid_human)

    summary = {
        "n_items": n_items,
        "n_valid": n_valid,
        "n_parse_failures": n_items - n_valid,
    }
    for name, metric_fn in METRICS.items():
        summary[name] = metric_fn(valid_human, valid_judge) if n_valid else None

    return summary
