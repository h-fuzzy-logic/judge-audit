# Industry Relevance

Automated evaluation using an LLM-as-judge is critical for scaling AI products, usually because a human can't review everything at the volume the platform operates at. But static judges often introduce subtle biases into production workflows. 

This section demonstrates how evaluating your judge's reliability prevents silent failures in commercial platforms, framing this repository's benchmark design as a reusable blueprint for production teams.
- For background on the core techniques, see [`llm-as-judge.md`](llm-as-judge.md).
- For implementation details of this repo's tooling, see [`approaches.md`](approaches.md).

## Why judge evaluation matters for platforms and products

- **Content moderation and trust & safety.** A judge scoring harmlessness at scale is standing in for reviewers who can't look at every post or generation. A judge with a blind spot doesn't fail loudly, it fails silently, letting harmful content through or over-flagging legitimate content at whatever rate its blind spot occurs, with nobody watching to notice.
- **RLHF and reward modeling.** If a reward model or LLM judge is generating the training signal for a policy model, any systematic bias in that judge (position bias, verbosity bias, self-preference) gets baked into the trained model's behavior, not just into one bad score. The error compounds instead of staying contained to a single mis-scored item.
- **Automated QA and regression monitoring.** Teams increasingly use an LLM judge to catch quality regressions after a model or prompt change, instead of a human spot-check. If that judge's agreement with human judgment hasn't been measured, "the judge didn't flag anything" and "there's no regression" are not the same claim, and treating them as the same claim is exactly the gap this project is about.
- **Vendor and procurement risk.** A team adopting a third-party judge/eval API is trusting that vendor's own claims about accuracy. Meta-evaluation is how a team checks that claim against their own data and their own definition of a costly error, rather than accepting a vendor benchmark that may not reflect their actual traffic or their actual risk tolerance.
- **Cost pressure pushes toward LLM judges, which is exactly why validating them matters more, not less.** LLM-as-judge is popular because it's far cheaper than human review at scale. That cost advantage is also the reason a bad judge can go unnoticed longer: nobody's doing the expensive human review that would have caught it.

## Reusing this repo's approach

The pipeline this project builds, prepare a labeled sample → run one or more judge configurations against it → extract structured scores → compute agreement metrics → test whether a difference between configurations is real, is generic. Nothing about it is specific to RAGTruth or to source-groundedness. What changes for a different team's use case:

- **The dataset.** Swap [`data/processed/source_groundedness_150.csv`](../data/processed/source_groundedness_150.csv) for your own labeled sample: real production items your team already has human judgments for, not a public benchmark. See [`scripts/prepare_dataset.py`](../scripts/prepare_dataset.py) for the shape a dataset needs to be in (a `context`/`response`-style pair plus a human label column).
- **The criterion and its structure.** Whatever your team's judge is meant to score, harmlessness, helpfulness, policy compliance, determines which metrics apply. See [`agreement-metrics.md`](agreement-metrics.md#judgment-structure-determines-metric-choice-not-the-dimension) for how judgment structure (absolute ordinal score, binary classification, pairwise preference) drives that choice, not the label of the criterion itself.
- **The rubric(s) being compared.** [`configs/prompts/`](../configs/prompts/) holds plain text files, no code changes needed to test a new scoring prompt, just a new file and a new line in the experiment's `promptfooconfig.yaml`.
- **The provider.** Providers are commented in/out one line at a time in `promptfooconfig.yaml` (see [`approaches.md`](approaches.md#promptfoo)); testing a candidate judge model before committing to it in production is a config edit, not a code change.
- **The safety-critical class.** [`src/metrics.py`](../src/metrics.py)'s `recall_class_0`/`precision_class_0` pattern generalizes directly: pick whichever class's false negative is your worst-case outcome (a missed policy violation, a missed hallucination) and report recall on that class specifically, not just an aggregate agreement number that can hide it.
- **What doesn't need to change:** the Docker/Makefile reproducibility setup, the cost-aware permission split (free steps auto-run, paid API calls always confirm first), and the [paired bootstrap significance test](../src/significance.py), all apply unchanged to any dataset or criterion. See [`tastes.md`](tastes.md#reproducibility--velocity-in-practice) for the reasoning behind that infrastructure.

## What would need to change for a production setting

This repo is a batch, offline meta-evaluation harness, run once, by hand, against a static 150-item sample. Adopting the same pattern for an actual production judge would need more than a dataset swap:

- **A much larger, continuously refreshed sample.** 150 items gives a confidence interval wide enough that, as this project's own results show, one of three metrics didn't reach significance. A production decision (does this judge ship) usually needs a tighter interval and a sample that gets refreshed as traffic and failure modes shift, not a one-time snapshot.
- **A trigger for re-validation, not a one-time check.** A judge that passes meta-evaluation today can silently degrade after a provider-side model update, a prompt change, or a shift in the traffic it's scoring. Production use needs meta-evaluation re-run on a schedule or on a trigger (a new model version, a detected distribution shift), not treated as a one-time gate.
- **An adjudication process for disagreement, not just a metric.** This project treats the human label as ground truth throughout. A live system needs a defined process for when the judge and a human reviewer disagree on a real, monetarily or safety consequential case, not just a downstream statistic.
- **Monitoring the judge's own drift, not just the policy model's.** The [diagram in `llm-as-judge.md`](llm-as-judge.md#example-workflow) treats meta-evaluation as a gate before deployment; a production system needs that same check running continuously against the judge itself, since the judge is as capable of drifting as anything it's scoring.
