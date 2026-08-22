# Research

The actual research content of this project: what data, what's being tested, and what's been run so far. See `approaches.md` for how the tooling works; this doc is about findings, not implementation.

## Dataset Description

- **Source:** `wandb/RAGTruth-processed` on Hugging Face. 15,090 train + 2,700 test raw examples, each an LLM-generated response to a task (summarization, QA, etc.) over a given source passage, human-annotated for hallucination.
- **Task chosen:** RAG groundedness. Is a generated response supported by its source context, or does it fabricate/contradict it.
- **Sampling:** stratified, 50 examples per class, fixed seed (42), for **150 total items**, perfectly balanced across the 3-point scale. Small and hand-verifiable by design, not a large benchmark cut.
- **Label derivation:** RAGTruth's own `hallucination_labels_processed` field (counts of `evident_conflict` and `baseless_info` spans) is collapsed into a 3-point groundedness score:
  - **2 (Fully Grounded):** no hallucination spans of either kind
  - **1 (Partially Grounded):** `baseless_info` present, no `evident_conflict`
  - **0 (Ungrounded):** `evident_conflict` present (a hard contradiction)
- **Fields kept per item:** `context`, `response` (RAGTruth's `output` field), `human_groundedness_score`.
- **File:** `data/processed/rag_groundedness_150.csv`.

## Hypothesis Tested

**Overarching question:** "How do you know your grader is right?" This project measures whether an LLM-as-judge's groundedness scores actually agree with human labels, rather than assuming a judge is reliable by default.

**Hypothesis tested so far:** *Does judge prompt design, specifically asking for chain-of-thought reasoning before a score versus asking for a direct score only, change how well the judge agrees with human labels?*
- **H0:** Chain-of-thought reasoning makes no difference to judge/human agreement.
- **H1:** Chain-of-thought reasoning improves judge/human agreement over a strict, direct-scoring rubric.

**Not yet tested** (in original project scope, no experiments run yet):
- Position bias (does response order affect the score?)
- Verbosity bias (does a longer/padded response get scored more favorably regardless of accuracy?)
- Self-preference (does a judge favor output from its own model family?)
- Tautological rubrics (does a vague/circular rubric inflate agreement artificially?)
- Cross-provider comparison (OpenAI/Anthropic judges are configured but not yet run, pending API keys)

## Experiments Done

### Experiment 1: Strict rubric vs. chain-of-thought rubric

- **Setup:** one provider (`google:gemini-3.5-flash-lite`), two rubric prompts, same 150 items each, for 300 judge calls total.
- **Rubrics compared:** `rubric_v1_strict` (score only, no reasoning requested) vs. `rubric_v2_chain_of_thought` (step-by-step claim analysis before scoring).
- **Results:**

  | Rubric | Cohen's κ | Quadratic Weighted κ | Exact agreement | Parse failures |
  |---|---|---|---|---|
  | Without Chain-of-Thought | 0.38 | 0.45 | 58.7% | 0/150 |
  | With Chain-of-Thought | **0.54** | **0.60** | **69.3%** | 0/150 |

- **Finding:** chain-of-thought reasoning meaningfully improved agreement on all three metrics, so **H1 is supported** for this provider. The confusion matrix shows *why*: the strict rubric badly over-predicts "partially grounded" (1). Only 8/44 fully-ungrounded (human=0) items were caught correctly, with 36 misclassified as 1. The CoT rubric catches 30/50 of those same cases correctly. The fully-grounded (human=2) row is nearly identical between the two rubrics, so the improvement is concentrated in catching actual contradictions, not a uniform lift everywhere.
- **Provider note:** an earlier attempt used `google:gemini-3.7-flash`, which hit frequent `503 UNAVAILABLE` ("high demand") errors and ran slowly, so the project switched to `gemini-3.5-flash-lite` for stability and speed. Worth flagging as a limitation: flash-lite is a smaller/faster tier, so this result may understate what a stronger reasoning model would show. Not yet tested against a larger Gemini tier or a different provider.

*(Next experiments, multi-provider comparison and bias probes, are not yet run. Add them here once they are.)*
