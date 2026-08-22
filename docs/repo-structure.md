judge-eval-harness/
├── .github/
│   └── workflows/
│       └── eval.yml               # Automated CI evaluation run on PRs
├── data/
│   ├── raw/                       # Original downloaded benchmark cuts (e.g., RAGTruth subsets)
│   ├── processed/
│   │   └── rag_groundedness_150.csv # Formatted 150-sample human-annotated dataset
│   └── README.md                  # Lineage & schema details for the human labels
├── configs/
│   ├── promptfooconfig.yaml       # Primary Promptfoo orchestration config
│   ├── prompts/                   # Evaluator prompt variants & rubrics
│   │   ├── rubric_v1_strict.txt
│   │   └── rubric_v2_chain_of_thought.txt
│   └── probes/                    # Adversarial bias injection configurations
│       ├── position_bias.yaml
│       └── verbosity_bias.yaml
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Preprocessing scripts to standardise public datasets
│   ├── extractors.py              # Robust output parsers (JSON, fallback regex)
│   └── metrics.py                 # Core math: Cohen's κ, quadratic weighted κ, confusion matrices
├── scripts/
│   ├── prepare_dataset.py         # Script to slice & convert raw dataset to CSV
│   └── run_calibration.py         # Main analysis runner parsing Promptfoo results
├── reports/
│   ├── figures/                   # Generated disagreement matrix heatmaps & delta plots
│   └── calibration_report.md      # Auto-generated or manual analytical writeup
├── .env.example                   # API key placeholders (OPENAI_API_KEY, ANTHROPIC_API_KEY)
├── .gitignore
├── Makefile                       # One-command CLI entrypoints (e.g., `make eval`, `make report`)
├── pyproject.toml / requirements.txt
└── README.md                      # Executive summary, methodology, and key findings