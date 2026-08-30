# RAGTruth

## Dataset Description
`wandb/RAGTruth-processed` on [Hugging Face](https://huggingface.co/datasets/wandb/RAGTruth-processed). 

The dataset is a standardized distribution of the original RAGTruth hallucination corpus used for the paper *RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models*. This version of the dataset has a cleaner schema and eliminates the need for complex processing. It contains about 18,000 rows and each row contains these columns:

| Name | Type | Description |
|---|---|---|
| `id` | string | Row identifier. |
| `query` | string | The question/task instruction given to the generating LLM (summarization, QA, or data-to-text prompt). |
| `context` | string | The source passage(s) the response should be grounded in. |
| `output` | string | The LLM-generated response being evaluated for hallucination. |
| `task_type` | categorical:<br>`Data2txt`<br>`QA`<br>`Summary` | Which of the three RAGTruth task families this example belongs to. |
| `quality` | categorical:<br>`good`<br>`incorrect_refusal`<br>`truncated` | Whether the response itself is well-formed, or is a refusal/cut off. A generation-quality flag, separate from hallucination. |
| `model` | categorical:<br>`gpt-3.5-turbo-0613`<br>`gpt-4-0613`<br>`llama-2-7b-chat`<br>`llama-2-13b-chat`<br>`llama-2-70b-chat`<br>`mistral-7B-instruct` | Which LLM generated `output`. |
| `temperature` | float32 | Sampling temperature used to generate `output`. Fixed sweep of 5 values: `{0.7, 0.775, 0.85, 0.925, 1.0}`. |
| `hallucination_labels` | string | Human-annotated.<br>  Raw annotation string (JSON-as-string; empty list when no hallucination spans), holding span-level detail before collapsing. |
| `hallucination_labels_processed` | dict | Human-annotated. <br> `{"evident_conflict": <int count>, "baseless_info": <int count>}`, the collapsed span counts this project's `prepare_dataset.py` reads. |
| `input_str` | string | The fully-assembled prompt text sent to the generating model (`query` + `context`, pre-composed into one string). |


## Annotation Methodology

Hallucination labels are human-annotated and used this methodology

- **Annotators:** recruited via a professional vendor, required to be proficient in English with a bachelor's degree in English, Communications, or a related field. Paid $25/hour.
- **Process:** annotators used Label Studio, viewing six model responses per page alongside the shared source context, and marked hallucinated spans directly in the text.
- **Original categories (four):** the source paper defines four hallucination types, not two:
  - **Evident Conflict:** direct contradiction/opposition to the source (e.g. a wrong number), easily verifiable.
  - **Subtle Conflict:** a departure that shifts meaning without being a flat factual contradiction.
  - **Evident Baseless Info:** fabricated/hypothetical detail with no basis in the source.
  - **Subtle Baseless Info:** an inferred detail or sentiment that goes beyond the source without being wholly invented.
- **Inter-annotator agreement:** two independent annotators per response. Consistency was 91.8% at the response level, 78.8% at the span level. Disagreements with substantial differences went to a third-party reviewer for adjudication.

**Caveat:** `wandb/RAGTruth-processed`'s `evident_conflict`/`baseless_info` fields collapse the original four categories down to two, merging the "evident" and "subtle" variant of each into one count. Some annotation resolution is lost in this collapsed version: a "subtle conflict" span and an "evident conflict" span both count toward the same `evident_conflict` total, and this project's derived `human_groundedness_score` inherits that loss.

## Weaknesses With This Data 
### Judge/benchmark contamination risk. 
RAGTruth is a well-known public benchmark. If a judge model (Gemini, GPT, Claude) saw this dataset or discussions of it during pretraining, measured agreement could be inflated by memorization rather than genuine groundedness reasoning. 

### Annotation agreement isn't that high. 
78.8% span-level IAA means a meaningful fraction of "ground truth" spans were themselves contested between two trained annotators.


## Citations
* **Original Paper:** Wu, Y., Zhu, J., Xu, S., Shum, K., Niu, C., Zhong, R., Song, J., & Zhang, T. (2024). *RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models*. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics.
* **Dataset Repository:** Weights & Biases. (2024). *RAGTruth-processed* [Dataset]. Hugging Face. Available at: [huggingface.co/datasets/wandb/RAGTruth-processed](https://huggingface.co)

