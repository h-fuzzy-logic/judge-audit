# judge-eval-harness

## Project Summary
A harness that measures whether an LLM judge agrees with human labels.

LLM-as-judge is used everywhere now (evals, RLHF/DPO reward signals, benchmark grading) but is rarely checked against real human judgment. A judge that quietly disagrees with humans corrupts every downstream decision built on top of it.

This harness measures that agreement directly, using Cohen's κ, quadratic weighted κ, exact agreement rate, and confusion matrices, on one narrow task: RAG groundedness. See [Research](docs/research.md) for the dataset, hypotheses, and current results.

This repo was built interactively with Claude Code with project-specific conventions in `CLAUDE.md`.

## Getting Started

**Just want to see the results?** The dataset, scored results, and figures are already committed. Start with [`docs/research.md`](docs/research.md) or browse `reports/figures/`. No setup needed.

**Want to run it yourself?**

1. Install [Docker](https://docs.docker.com/get-docker/) and make sure it's running.
2. Clone the repo and `cd` into it.
3. Copy `.env.example` to `.env` and add a `GOOGLE_API_KEY` (the only provider currently active in `configs/promptfooconfig.yaml`).
4. `make docker-build` to build the image.
5. `make docker-eval` to run the judge evaluations. This calls a real API and spends money.
6. `make docker-analyze` to extract scores and compute agreement metrics. Free, local only.
7. `make docker-view` to browse eval history in the browser, or open `reports/agreement_summary.csv` and `reports/figures/` directly.

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
│   ├── promptfooconfig.yaml     # judge eval orchestration
│   └── prompts/
│       ├── rubric_v1_strict.txt
│       └── rubric_v2_chain_of_thought.txt
├── data/processed/
│   └── rag_groundedness_150.csv # the 150-item hand-labeled dataset
├── docs/
│   ├── research.md              # dataset, hypotheses, results
│   ├── approaches.md            # how each part of the tooling works
│   ├── tastes.md                # research/engineering taste notes
│   └── repo-structure.md        # the original planning doc
├── reports/
│   ├── scored_results.csv       # per-item judge vs. human scores
│   ├── agreement_summary.csv    # kappa/QWK/agreement per condition
│   └── figures/                 # confusion-matrix heatmaps
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

Note: `reports/results.json` (raw Promptfoo output) and `.promptfoo/` (eval history/cache) are generated locally by `make docker-eval` but git-ignored, so they won't appear after a fresh clone.

## Documentation

- [Research](docs/research.md): Dataset, hypotheses, experiments and results.
- [Technologies](docs/approaches.md): Why each technology was chosen and how it is used in this repo (Promptfoo, Docker, Python libraries).
- [Research Taste and Engineering Taste](docs/tastes.md): My judgements and principles that drive my work. 
- [Repository Structure](docs/repo-structure.md): The repo layout.
- [`CLAUDE.md`](CLAUDE.md): Conventions for this repo.

## Reproducibility & Velocity

Reproducible environments, cost-aware guardrails, and a fast experiment loop are some of the disciplines every team (a research lab, a startup, an enterprise ML org) needs to move fast without breaking things or burning budget. Built so anyone picking this up can iterate quickly without babysitting infrastructure or trying to remember "how do I run this again."

### Reproducible environments
- **One Makefile, not five remembered commands.** Every workflow step has the same entry point for every contributor, so no one's typing a slightly different command or flag by hand.
- **One Docker image, not manually matched versions.** A single command gives everyone the same environment. No "works on my machine" headaches.
- **One CLAUDE.md, not repeated tribal knowledge.** It captures the team's conventions, so work doesn't quietly drift back to ad hoc, undocumented commands.

### Cost-aware guardrails
- **Guardrails tuned for cost, not just correctness.** `.claude/settings.json`:
  - Auto-allows no-cost operations
  - Always asks first for anything that spends real API money
- **Config mistakes caught before they cost anything.** An automated check runs on every config edit, catching errors immediately instead of surfacing them only after a failed (and possibly paid) eval run.
- **Zero-cost config checks.** A free validation step catches bad paths/YAML/provider IDs in seconds, no API spend.

### Fast experiment loop
- **Eval history survives ephemeral containers.** Local results stay browsable across runs, not just the latest.
- **Fast edit loop, no rebuild tax.** Code and config edits take effect immediately in the Docker container; a rebuild is only needed after a dependency change.
- **Cheap smoke tests before a full run.** A new rubric or provider can be validated against a handful of rows before committing to the full run.
- **Judge/provider swaps are single-line edits.** Rubric prompts and providers are commented in/out individually, no code changes needed.

See [`docs/approaches.md`](docs/approaches.md) for implementation details and the specific bugs this setup was built to catch early.
