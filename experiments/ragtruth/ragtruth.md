# RAGTruth

## Dataset Description
`wandb/RAGTruth-processed` on [Hugging Face](https://huggingface.co/datasets/wandb/RAGTruth-processed). 
An LLM-generated response to a task (summarization, QA, etc.) over a given source passage, human-annotated whether the response is a hallucination.
- 15,090 samples 
- 6,721 with hallucinations
- Each sample contains: 
    - A query/question
    - Context passages
    - Model output
    - Hallucination labels (evident conflict and/or baseless information)
    - Quality assessment
    - Model metadata (name, temperature)
