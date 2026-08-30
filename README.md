# judge-eval-harness

## Project Summary
A harness that measures whether an LLM's score agrees with a score given by a human.

I see LLM-as-judge being used everywhere but it makes me so uncomfortable, seeing AI evaluate AI.  So I created this harness to meassure LLM agreement with human labels using Cohen's κ, quadratic weighted κ, exact agreement rate, on the task RAG groundedness. See [Research](docs/research.md) for the dataset, hypothesis, and current results.

I build the repo to be flexible, to allow experimentation with different tasks, metrics, LLMs, and datasets. Details about [engineering choices](docs/tastes.md#engineering-taste).

This repo was built interactively with Claude Code with project-specific conventions in `CLAUDE.md`.

## Getting Started

**Just want to see the results?** The dataset, scored results, and figures are already committed. Start with [`docs/research.md`](docs/research.md) or browse [`experiments/ragtruth/01-strict-vs-cot-rubric/figures/`](experiments/ragtruth/01-strict-vs-cot-rubric/figures). No setup needed.

**Want to run it yourself?**

1. Install [Docker](https://docs.docker.com/get-docker/) and make sure it's running.
2. Clone the repo and `cd` into it.
3. Copy `.env.example` to `.env` and add a `GOOGLE_API_KEY` (the only provider currently active in the experiment's `promptfooconfig.yaml`).
4. `make docker-build` to build the image.
5. `make docker-eval` to run the judge evaluations. This calls a real API and spends money.
6. `make docker-analyze` to extract scores and compute agreement metrics. Free, local only.
7. `make docker-view` to browse eval history in the browser, or open the experiment's `agreement_summary.csv` and `figures/` directly.

`make docker-run` chains prepare, eval, and analyze in one command if you want the whole pipeline at once (also spends money on the eval step). See [`CLAUDE.md`](CLAUDE.md) for the full set of commands.

### Project Structure

```
judge-eval-harness/
├── CLAUDE.md                    # working conventions for this repo
├── Dockerfile
├── docker-compose.yml
├── Makefile                     # every workflow entry point
├── requirements.txt             # pinned Python dependencies
├── .claude/settings.json        # tool permissions + config-validation hook
├── configs/
│   └── prompts/                 # rubric prompts, shared across experiments
│       ├── rubric_v1_strict.txt
│       └── rubric_v2_chain_of_thought.txt
├── data/processed/
│   └── rag_groundedness_150.csv # the 150-item hand-labeled dataset
├── docs/
│   ├── research.md              # hypotheses tested, findings, limitations
│   ├── approaches.md            # how each part of the tooling works
│   └── tastes.md                # research/engineering taste notes
├── experiments/
│   └── ragtruth/
│       ├── ragtruth.md          # RAGTruth dataset description
│       └── 01-strict-vs-cot-rubric/
│           ├── promptfooconfig.yaml  # this experiment's judge eval orchestration
│           ├── scored_results.csv    # per-item judge vs. human scores
│           ├── agreement_summary.csv # kappa/QWK/agreement per condition
│           └── figures/              # confusion-matrix heatmaps
├── scripts/
│   ├── prepare_dataset.py       # RAGTruth -> 150-item CSV
│   ├── extract_scores.py        # results.json -> scored_results.csv
│   └── compute_agreement.py     # scored_results.csv -> metrics + figures
├── src/
│   ├── extractors.py            # judge output -> 0/1/2 score
│   ├── metrics.py                # Cohen's kappa, QWK, confusion matrix
│   └── visualization.py          # heatmap rendering
└── tests/                       # one file per src/scripts module
```

Note: each experiment's `results.json` (raw Promptfoo output) and `.promptfoo/` (eval history/cache) are generated locally by `make docker-eval` but git-ignored, so they won't appear after a fresh clone.

## Documentation

Deeper documentation than this README needs, organized by purpose:

- [Research](docs/research.md): Dataset, hypotheses, experiments and results.
- [Technologies](docs/approaches.md): Why each technology was chosen and how it is used in this repo (Promptfoo, Docker, Python libraries).
- [Research Taste and Engineering Taste](docs/tastes.md): Judgments and principles behind the decisions in this repo.
- [CLAUDE.md](CLAUDE.md): Conventions for this repo.
