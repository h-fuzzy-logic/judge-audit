# Experiment 1 

## Hypothesis Tested

**Overarching question:** "How do you know your grader is right?" Measuring whether an LLM-as-judge's groundedness scores actually agree with human labels, rather than assuming a judge is reliable by default.

Measure LLM agreement with human labels using Cohen's κ, quadratic weighted κ, exact agreement rate, on the task RAG groundedness. 

**Hypothesis tested so far:** *Does judge prompt design, specifically asking for chain-of-thought reasoning before a score versus asking for a direct score only, change how well the judge agrees with human labels?*
- **H0:** Chain-of-thought reasoning makes no difference to judge/human agreement.
- **H1:** Chain-of-thought reasoning improves judge/human agreement over a strict, direct-scoring rubric.

**Not yet tested** (no experiments run yet):
- Position bias (does response order affect the score?)
- Verbosity bias (does a longer/padded response get scored more favorably regardless of accuracy?)
- Self-preference (does a judge favor output from its own model family?)
- Tautological rubrics (does a vague/circular rubric inflate agreement artificially?)
- Cross-provider comparison (OpenAI/Anthropic judges are configured but not yet run, pending API keys)


## Dataset Description
See [`experiments/ragtruth/ragtruth.md`](../experiments/ragtruth/ragtruth.md) for the RAGTruth dataset description.

## Data Processing In This Repo
### Experiment 1

Built by `scripts/prepare_dataset.py`, resulting in [150 rows](data/processed/rag_groundedness_150.csv) from the train set. 

- **Columns used:** `context`, `output` (renamed `response`), `hallucination_labels_processed`, and `quality` (used only as a filter, not carried into the final CSV).
- **Columns dropped:** `task_type`, `model`, `temperature`, and `hallucination_labels`.
- **Quality filtering:** rows where `quality` isn't `good` are dropped first. A refusal or truncated generation has no hallucination spans to detect, so without this filter it would silently score as "Fully Grounded" despite never being evaluated for groundedness at all. On the `train` split this drops 148/15,090 rows (120 `incorrect_refusal`, 28 `truncated`), well within the margin needed to still get 50 rows per class.
- **Length filtering:** rows with `context` under 50 characters or `response` under 20 characters are dropped (removes empty/degenerate rows) before sampling.
- **New column:** `human_groundedness_score` 
    - Maps `hallucination_labels_processed` column's into a single 0-2 score based on `evident_conflict`/`baseless_info` counts and collapses:
  - `2` (Fully Grounded): no hallucination spans of either kind
  - `1` (Partially Grounded): `baseless_info` present, no `evident_conflict`
  - `0` (Ungrounded): `evident_conflict` present, regardless of `baseless_info` count
- **Sampling:** stratified, 50 rows per `human_groundedness_score` class, fixed seed (42), for **150 total rows**, then shuffled (same seed) before being written out.
- **Final columns written to CSV:** `context`, `response`, `human_groundedness_score`, exactly the three fields Promptfoo's judge prompts and this project's scoring scripts need.


## Experiments Done

### Experiment 1: Strict rubric vs. chain-of-thought rubric

- **Setup:** one provider (`google:gemini-3.5-flash-lite`), two rubric prompts, same 150 items each, for 300 judge calls total.
- **Rubrics compared:** `rubric_v1_strict` (score only, no reasoning requested) vs. `rubric_v2_chain_of_thought` (step-by-step claim analysis before scoring).
- **Results:**

  | Rubric | Cohen's κ | Quadratic Weighted κ | Exact agreement | Parse failures |
  |---|---|---|---|---|
  | Without Chain-of-Thought | 0.40 | 0.53 | 60.0% | 0/150 |
  | With Chain-of-Thought | **0.53** | **0.60** | **68.7%** | 0/150 |

  *(Corrected after adding the quality filter described above; see the Data Processing Correction note below.)*

- **Finding:** chain-of-thought reasoning meaningfully improved agreement on all three metrics, so **H1 is supported** for this provider. The confusion matrix shows *why*: the strict rubric badly over-predicts "partially grounded" (1). Only 13/50 fully-ungrounded (human=0) items were caught correctly, with 31 misclassified as 1. The CoT rubric catches 28/50 of those same cases correctly. The fully-grounded (human=2) row is close between the two rubrics (37/50 vs 40/50 correct), so the improvement is concentrated in catching actual contradictions, not a uniform lift everywhere.
- **Data Processing Correction:** the original run of this experiment didn't filter RAGTruth's `quality` column, so a small number of refusals/truncated generations were present in the 150-item sample, misclassified as "Fully Grounded" purely because a refusal has no hallucination spans to detect. After adding the quality filter (see Feature Selection above) and re-sampling, re-running both rubrics against the corrected 150-item sample moved κ from 0.38 → 0.40 (strict) and 0.54 → 0.53 (CoT), both within normal sampling noise for n=150. **The finding is unchanged**: CoT still meaningfully outperforms the strict rubric on every metric, so this correction doesn't overturn H1, it just removes a known confound from the underlying sample.
- **Caveat on that finding:** `rubric_v2_chain_of_thought` asks the judge to break the response into claims and categorize each one, which structurally resembles how the ground-truth label itself was built (span-by-span categorization, then collapsed). `rubric_v1_strict` asks for a single holistic guess with no such breakdown. Part of the κ improvement may reflect that the CoT process happens to match the label's own construction method, not that chain-of-thought reasoning is generally better. This experiment can't separate those two explanations; see the label-derivation limitation above.
- **Provider note:** an earlier attempt used `google:gemini-3.7-flash`, which hit frequent `503 UNAVAILABLE` ("high demand") errors and ran slowly, so the project switched to `gemini-3.5-flash-lite` for stability and speed. Worth flagging as a limitation: flash-lite is a smaller/faster tier, so this result may understate what a stronger reasoning model would show. Not yet tested against a larger Gemini tier or a different provider.

*(Next experiments, multi-provider comparison and bias probes, are not yet run. Add them here once they are.)*


### Future Experiments
- See [Annotation Methodology](#annotation-methodology) and the label-derivation caveat in [`docs/research.md`](../../docs/research.md) for known limitations of this sample not yet addressed (label collapsing, no direct human holistic re-rating).
