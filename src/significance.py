"""Paired bootstrap significance testing for comparing two judge conditions
(e.g. two rubrics) scored against the same human labels on the same items.

Point-estimate comparisons (e.g. "kappa was 0.53 vs 0.40") can't say whether
that gap is bigger than sampling noise. This resamples items with
replacement many times and recomputes the metric difference on each
resample, giving a confidence interval and an empirical p-value instead of
just eyeballing two numbers.
"""
import numpy as np


def paired_bootstrap_test(
    human_scores,
    judge_scores_a,
    judge_scores_b,
    metric_fn,
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> dict:
    """Tests whether metric_fn(human, judge_b) - metric_fn(human, judge_a) is
    significantly different from zero.

    human_scores, judge_scores_a, and judge_scores_b must be the same length
    and index-aligned: item i's human label, condition-A judge score, and
    condition-B judge score all refer to the same underlying item (e.g. the
    same 150 rows, scored once under each rubric).

    Returns a dict with the observed difference, a 95% bootstrap confidence
    interval, and a two-sided empirical p-value (the fraction of bootstrap
    differences that land on the opposite side of zero from the observed
    effect, doubled and capped at 1.0).
    """
    human = np.asarray(human_scores)
    judge_a = np.asarray(judge_scores_a)
    judge_b = np.asarray(judge_scores_b)

    if not (len(human) == len(judge_a) == len(judge_b)):
        raise ValueError("human_scores, judge_scores_a, and judge_scores_b must be the same length")
    if len(human) == 0:
        raise ValueError("cannot run a bootstrap test on zero items")

    n = len(human)
    observed_diff = metric_fn(human, judge_b) - metric_fn(human, judge_a)

    rng = np.random.default_rng(seed)
    boot_diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot_diffs[i] = metric_fn(human[idx], judge_b[idx]) - metric_fn(human[idx], judge_a[idx])

    ci_lower, ci_upper = np.percentile(boot_diffs, [2.5, 97.5])

    # Two-sided empirical p-value: how often the bootstrap distribution
    # crosses zero, counted from whichever side the observed effect isn't on.
    if observed_diff >= 0:
        p_value = 2 * np.mean(boot_diffs <= 0)
    else:
        p_value = 2 * np.mean(boot_diffs >= 0)
    p_value = min(float(p_value), 1.0)

    return {
        "observed_diff": float(observed_diff),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "p_value": p_value,
        "n_bootstrap": n_bootstrap,
        "significant_at_0.05": bool(p_value < 0.05),
    }
