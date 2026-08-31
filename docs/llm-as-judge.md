# LLM-as-Judge

Background reference on LLM-as-judge as an evaluation technique: judges get validated via meta-evaluation before being deployed across contexts like red-teaming pipelines, capability benchmarks, RLHF training-signal generation, and production monitoring.

## Common criteria an LLM judge is asked to score

These are some evaluation dimensions, what the judge is scoring: 

- **Helpfulness / response quality.** The MT-Bench / Chatbot Arena style: is this response relevant, complete, and useful for what was asked. Usually judged on an absolute scale or as pairwise preference (A vs. B).
- **Instruction following.** Did the response actually satisfy the constraints given (format, length, "answer in exactly 3 bullets," etc.), independent of whether the content itself is good.
- **General factuality.** Similar to groundedness but not tied to a provided source document; checking claims against world knowledge rather than a specific context passage (closer to TruthfulQA-style evaluation).
- **Source-groundedness.** Is a generated response supported by its given source context, or does it fabricate or contradict it. Often called "RAG groundedness" since it's the generation-side half of what a full retrieval-augmented pipeline needs checked, but no retrieval step is required to test it: the context can simply be provided, as it is here. The criterion this project focuses on.
- **Summarization quality.** Its own sub-field, usually broken into faithfulness, coverage, and conciseness as separate judged dimensions rather than one score (SummEval is the reference benchmark here).
- **Harmlessness / safety.** Does a response avoid toxic, biased, or harmful content, and separately, did it appropriately refuse (or wrongly over-refuse) a request.
- **Reasoning / math correctness.** Grading whether a chain-of-thought reasoning path and final answer are both correct, common in math and logic benchmarks.
- **Code correctness.** Does generated code run, pass tests, or follow reasonable style, sometimes judged by an LLM reading the code rather than actually executing it.
- **Pairwise preference / reward modeling.** The RLHF/DPO framing: given two responses, which does a human prefer, used to train or evaluate reward models directly rather than scoring in isolation.
- **Dialogue / persona consistency.** In multi-turn settings, does the model stay coherent and in-character across turns.
- **Translation adequacy and fluency.** Classic MT evaluation, now often judged by LLMs instead of BLEU/ROUGE-style metrics.

The common thread across all of these: an LLM judge is doing the scoring, and its reliability is rarely checked against human labels. Groundedness is one of the cleaner criteria to calibrate against because the labeling itself is fairly objective (contradiction vs. not); helpfulness and creative-writing-style criteria are much harder to calibrate against because human agreement on those is often lower to begin with.

Which agreement metrics apply to a given criterion depends on how it's judged, not which criterion it is, several of the criteria above (helpfulness especially) can be judged in more than one way. See [`agreement-metrics.md`](agreement-metrics.md#judgment-structure-determines-metric-choice-not-the-dimension) for that breakdown.

## Meta-evaluation: validating the judge before it's trusted anywhere

Before a judge's score is trusted for any deployment context, it should go through **meta-evaluation** (also called judge calibration/validation): a fixed, human-labeled dataset is used to check whether the judge itself is reliable. This comes *before* the contexts below, not alongside them, a judge that hasn't been meta-evaluated is one nobody has checked is trustworthy yet. [Experiment 1](../experiments/ragtruth/01-strict-vs-cot-rubric/README.md) is an example: it studies the source-groundedness criterion via meta-evaluation.

## Contexts an LLM judge gets deployed in (once validated)

A single criterion above (e.g. Harmlessness/safety) gets applied across any of these contexts, a separate, cross-cutting axis from what's being scored:

- **Red-teaming pipelines.** Adversarial prompts probe for failures; a judge typically scores Harmlessness/safety on the model's response.
- **Capability benchmarks.** A fixed test set scores the *generating* model's ability at a task; a judge typically scores Reasoning/math correctness or Code correctness.
- **RLHF training-signal generation.** A judge's score (or pairwise preference) becomes the reward signal a policy model is trained against.
- **Production monitoring.** Live traffic is sampled and scored, often for Harmlessness/safety or Helpfulness, to catch regressions after deployment.

## How LLM-as-judge relates to AI safety
Since an LLM judge is often doing the scoring for these criteria, it is important to know if that delegation can be trusted and under what conditions it breaks down. 


## Further Explanations from Claude Sonnet
 "This project treats 'trusting an LLM judge' as an empirical question rather than an assumption, which is the same posture scalable-oversight research takes toward AI-checking-AI more broadly, just at a scale small enough to actually validate against ground truth."

 **Eval trust.** A lot of the AI safety evaluation ecosystem (capability evals, red-teaming, safety benchmarks) has quietly shifted to LLM-as-judge grading for cost reasons. If judges have systematic biases, position, verbosity, self-preference (your own "not yet tested" list), then safety evaluations built on top of them can look clean while missing real problems. You're not testing a downstream safety eval directly, but you're testing the primitive those evals are all built on.