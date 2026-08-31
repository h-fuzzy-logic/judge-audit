# Agreement Metrics

Background reference on the statistics used to measure agreement between two raters (a human label and an LLM judge) on an ordinal scale, and on alternatives that were considered but aren't used in this repo yet.

## Judgment structure determines metric choice, not the dimension

Nothing on this page is specific to groundedness. It's specific to a *structure* of judgment: one absolute score per item, on a fixed ordinal scale. Which of the [criteria in `llm-as-judge.md`](llm-as-judge.md#common-criteria-an-llm-judge-is-asked-to-score) is being scored, helpfulness, harmlessness, groundedness, doesn't decide which metrics apply; how that criterion gets turned into an actual judgment does. The same criterion can even use different structures in different setups (helpfulness is the clearest example below).

Three structures cover most of what's in that list:

| Judgment structure | What it looks like | Metrics that fit | Criteria that typically use it |
|---|---|---|---|
| **Absolute ordinal score** (this project's structure) | One score per item on a fixed scale (e.g. 0-2, 1-5) | Cohen's κ, weighted κ, exact agreement rate, per-class recall/precision, all covered below | Source-groundedness, General factuality, Summarization quality, Dialogue/persona consistency, Translation adequacy/fluency, and Helpfulness *when scored absolutely rather than by preference* |
| **Binary classification** | Item is one of two classes (pass/fail, harmful/not) rather than a point on a multi-point scale | Precision, recall, F1, AUC; κ is technically still valid for two-class agreement but is rarely the headline metric here | Harmlessness/safety, Instruction-following (per constraint), Reasoning/math correctness, Code correctness |
| **Pairwise preference** | The judge picks A, B, or tie between two items, there's no score on either item alone | Percent agreement on which side wins; rank correlation (Spearman, Kendall's tau, or correlation between two Elo/Bradley-Terry ratings) once many pairwise picks get aggregated into a leaderboard; prediction accuracy/AUC if the judge outputs a continuous preference score | Pairwise preference/reward modeling, and Helpfulness *when scored via A/B comparison, actually the more common real-world setup: Chatbot Arena, MT-Bench, and most RLHF preference data all work this way* |

This project's task, source-groundedness scored 0-2 per response, is the first row, so everything below is built for that structure. A future experiment on a different criterion only needs different metrics if it also uses a different *structure*: scoring helpfulness on the same 0-2-style absolute scale would reuse this exact toolkit unchanged, but scoring it by pairwise preference would not, see the pairwise entry under Alternatives below.

## Metrics used in this project

### Cohen's κ

Measures agreement between two raters corrected for the agreement you'd expect by chance alone. Raw percent agreement can look good even when two raters are barely doing better than guessing, especially when one class is common; κ discounts for that. Treats every disagreement equally: an off-by-one and an off-by-two error count the same.

**Watch out for:** κ is known to behave erratically when the raters' class distributions are very skewed (the "kappa paradox", high raw agreement can still produce a low or unstable κ). Stratified/balanced sampling, rather than scoring the raw class distribution directly, keeps this from being a problem.

**Implementation:** [`compute_cohen_kappa`](../src/metrics.py)
**Used by:** [Experiment 1](../experiments/ragtruth/01-strict-vs-cot-rubric/README.md)

### Quadratic Weighted κ (QWK)

Same chance-correction as Cohen's κ, but for ordinal scales where distance matters: an error is penalized proportional to the *square* of how far off it is, so mistaking a 0 for a 2 is penalized four times as heavily as mistaking a 0 for a 1. This is the standard metric for automated-grader-vs-human agreement on an ordinal quality scale (it's what the Kaggle Automated Essay Scoring benchmark uses).

**Implementation:** [`compute_quadratic_weighted_kappa`](../src/metrics.py)
**Used by:** [Experiment 1](../experiments/ragtruth/01-strict-vs-cot-rubric/README.md)

### Exact agreement rate

The plain fraction of items where the two raters gave the identical score. No chance-correction, no distance-sensitivity, just the most literal, human-readable number: "how often did they match exactly." Useful as an intuitive companion number, not as the primary scientific metric, since it doesn't adjust for how easy agreement would be by chance.

**Implementation:** [`compute_exact_agreement_rate`](../src/metrics.py)
**Used by:** [Experiment 1](../experiments/ragtruth/01-strict-vs-cot-rubric/README.md)

### Per-class recall / precision

Treats one specific class as its own binary detection problem. Recall for class *c*: of items actually labeled *c*, what fraction did the judge also score as *c*. Precision for class *c*: of items the judge scored as *c*, what fraction actually are. Useful when one class's errors matter more than others, an aggregate metric like κ or exact agreement treats every class symmetrically and can hide that one specific class is being missed badly.

**Implementation:** [`compute_recall_for_class`, `compute_precision_for_class`](../src/metrics.py)
**Used by:** [Experiment 1](../experiments/ragtruth/01-strict-vs-cot-rubric/README.md) (class 0, the safety-critical class for a hallucination-detection task)

## Alternatives considered but not used

### Linear weighted κ

Like QWK, but penalizes an error proportional to distance rather than distance squared (off-by-two counts twice as much as off-by-one, not four times). A legitimate alternative for ordinal data; QWK's steeper penalty on far misses was judged the better fit where the worst-case error (a confident, contradicted response scored as fully correct) is exactly the kind of far miss you want penalized hardest.

### Krippendorff's α

A more general reliability coefficient than kappa: handles missing data more cleanly, supports more than two raters, and works across nominal, ordinal, interval, or ratio data with an appropriate distance function. Less prone to the kappa paradox than plain Cohen's κ. A reasonable alternative or cross-check, particularly if data is ever scored without the kind of balanced stratified sampling that keeps κ well-behaved.

### Gwet's AC1 / AC2

Built specifically to fix the kappa paradox: stays stable under skewed class prevalence where kappa can become unreliable. AC2 extends this to ordinal, distance-weighted agreement, functionally a more prevalence-robust alternative to QWK. Worth switching to if a future experiment scores an unbalanced, non-stratified sample directly.

### Kendall's tau-b / Spearman correlation

Treats scores as ranks and asks whether the two raters order items similarly, without needing kappa's chance-correction machinery at all. A valid, simpler alternative for ordinal agreement, less standard for this kind of task, but a reasonable sanity check alongside kappa.

### Mean absolute error / RMSE (treating scores as literal numbers)

The simplest version: on average, how many points off is the judge. Mathematically related to QWK (which is essentially a chance-corrected, rescaled version of the same squared-error idea), but far more interpretable to a non-technical reader ("off by 0.3 points on average" versus "QWK = 0.60"). Requires being willing to treat an ordinal scale as literal numbers, which not everyone considers valid.

### Balanced accuracy / per-class F1

Balanced accuracy (the mean of each class's recall) matters most when class distributions are skewed; with a stratified, balanced sample it converges close to plain exact agreement rate, so it doesn't add much in that setting specifically. Per-class F1 would generalize the per-class recall/precision above into one combined number per class, at the cost of being one step less directly interpretable than reporting recall and precision separately.

### Precision / recall / F1 / AUC, for a binary classification structure

Different from the per-class recall/precision above, which carves one class out of a multi-point *ordinal* scale (this project's 0-2). A genuinely binary structure, like harmlessness/safety (harmful vs. not) or a pass/fail code-correctness check, never has an ordinal scale to carve up in the first place; it's two classes from the start. These are the standard classification metrics for that shape of judgment, and AUC additionally applies if the judge outputs a continuous score or probability rather than a hard pick.

### Pairwise preference metrics

For a judgment structure where the judge compares two items rather than scoring one (see the Pairwise preference row above): percent agreement on which side wins is the direct analog of this project's exact agreement rate. Rank correlation (Spearman, Kendall's tau, or comparing two Elo/Bradley-Terry ratings) applies once many pairwise picks get aggregated into a model leaderboard, asking whether the judge's induced ranking matches the human-induced one. Prediction accuracy or AUC applies when a reward model outputs a continuous preference score rather than a discrete A/B pick. None of this project's current metrics transfer to this structure; a pairwise-preference experiment would need its own toolkit.
