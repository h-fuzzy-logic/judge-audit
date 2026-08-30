# LLM-as-Judge

Background reference on LLM-as-judge as an evaluation technique: what it's commonly used for, and how those tasks relate to the calibration problem this project studies.

## Common tasks for LLM-as-judge

- **Helpfulness / response quality.** The MT-Bench / Chatbot Arena style: is this response relevant, complete, and useful for what was asked. Usually judged on an absolute scale or as pairwise preference (A vs. B).
- **Instruction following.** Did the response actually satisfy the constraints given (format, length, "answer in exactly 3 bullets," etc.), independent of whether the content itself is good.
- **General factuality.** Similar to groundedness but not tied to a provided source document; checking claims against world knowledge rather than a specific context passage (closer to TruthfulQA-style evaluation).
- **Source-groundedness.** Is a generated response supported by its given source context, or does it fabricate or contradict it. Often called "RAG groundedness" since it's the generation-side half of what a full retrieval-augmented pipeline needs checked, but no retrieval step is required to test it: the context can simply be provided, as it is here. The task this project focuses on.
- **Summarization quality.** Its own sub-field, usually broken into faithfulness, coverage, and conciseness as separate judged dimensions rather than one score (SummEval is the reference benchmark here).
- **Harmlessness / safety.** Does a response avoid toxic, biased, or harmful content, and separately, did it appropriately refuse (or wrongly over-refuse) a request.
- **Reasoning / math correctness.** Grading whether a chain-of-thought reasoning path and final answer are both correct, common in math and logic benchmarks.
- **Code correctness.** Does generated code run, pass tests, or follow reasonable style, sometimes judged by an LLM reading the code rather than actually executing it.
- **Pairwise preference / reward modeling.** The RLHF/DPO framing: given two responses, which does a human prefer, used to train or evaluate reward models directly rather than scoring in isolation.
- **Dialogue / persona consistency.** In multi-turn settings, does the model stay coherent and in-character across turns.
- **Translation adequacy and fluency.** Classic MT evaluation, now often judged by LLMs instead of BLEU/ROUGE-style metrics.

The common thread across all of these: an LLM judge is doing the scoring, and its reliability is rarely checked against human labels. Groundedness is one of the cleaner tasks to calibrate against because the label criteria are fairly objective (contradiction vs. not); helpfulness and creative-writing-style tasks are much harder to calibrate against because human agreement on those is often lower to begin with.
