# Approaches

Running log of how each part of this project actually works and why, built up incrementally as a reference, not a tutorial.

## Promptfoo

**What it's for:** Promptfoo is the eval framework that actually runs the LLM judges. It takes three things (prompts, providers, and test cases) and produces one row of raw output for every (test case × prompt × provider) combination.

**How it's wired in this project** (`configs/promptfooconfig.yaml`):
- **`prompts`.** The rubric templates in `configs/prompts/` (e.g. `rubric_v1_strict.txt`), each containing `{{context}}` and `{{response}}` placeholders. Both rubric variants are currently active, so every row gets judged twice.
- **`providers`.** The judge LLMs to run. Currently just `google:gemini-3.5-flash-lite`; OpenAI/Anthropic entries exist but are commented out pending API keys.
- **`tests`.** Points at `data/processed/rag_groundedness_150.csv` directly. Promptfoo turns each CSV column into a template variable automatically, so `context` and `response` fill the prompt placeholders. `human_groundedness_score` isn't used in the prompt itself, but rides along in the output row unused. That's what lets it be joined back against the judge's score later.
- **`defaultTest.assert: contains-json`.** A light, cheap check that the judge's output contains *some* valid JSON substring. It does not validate that the JSON has the right shape or a sane score. That's a correctness concern, not a formatting one, so it's handled downstream instead (see `src/extractors.py`).

**Running it:** `make eval` (or `make docker-eval`) runs `npx promptfoo eval -c configs/promptfooconfig.yaml -o reports/results.json`. Output is one JSON file, `reports/results.json`, with one entry per (test case × prompt × provider). Each entry carries the judge's raw text response plus the original vars.

**What Promptfoo deliberately does *not* do here:** it does not parse the judge's raw output into a clean 0/1/2 score, and it does not compute agreement with human labels. Promptfoo *can* do inline transforms (a `transform:` hook that post-processes output before it's written), but this project keeps that parsing step as its own explicit, testable Python code (`src/extractors.py` + `scripts/extract_scores.py`) instead. See the extraction section below once it's added.

**A path-resolution gotcha worth remembering:** relative paths inside `promptfooconfig.yaml` resolve relative to *the config file's own directory* (`configs/`), not the repo root. That's why `tests: ../data/processed/...` needs the `../`, and why prompt paths are `file://prompts/...` rather than `file://configs/prompts/...`. Got this wrong twice before landing on a working config.

**Eval history:** every run also gets written to Promptfoo's own local store (`.promptfoo/`, bind-mounted into the container so it persists across runs). `make docker-view` launches Promptfoo's own browser UI (`promptfoo view`) against that history, separate from the `reports/*.json` files this project's own scripts read.

## Docker

**What it's for:** one identical Python + Node + Promptfoo environment for anyone running this project, so results are actually reproducible. No "works on my machine," no manually matching a Node version to whatever Promptfoo currently requires.

**`Dockerfile` layer ordering matters for caching:** instructions are ordered least-frequently-changing to most-frequently-changing, since invalidating one Docker layer invalidates every layer after it, never before it:
1. OS packages (`make`, Node 22 via NodeSource. Debian's own `nodejs` package is too old for Promptfoo's `>=22.22` requirement)
2. `COPY requirements.txt .` + `pip install`. Only reruns when `requirements.txt` itself changes, not on every code edit
3. `npm install -g promptfoo@0.122.0`. Version-pinned, so a future `--no-cache` rebuild can't silently pull a different Promptfoo version
4. `COPY . .`. Deliberately last, since it's the layer that changes on nearly every edit

**`docker-compose.yml` bind-mounts everything meant to be edited live:** `data/`, `configs/`, `reports/`, `src/`, `scripts/`, `tests/`, `Makefile`, and `.promptfoo/` are all mounted from the host, so editing any of them takes effect immediately in the next `docker compose run`. No rebuild. A rebuild is only needed after touching `requirements.txt` (a new dependency) or the `Dockerfile` itself. Two things weren't bind-mounted at first and quietly served stale content until noticed: `tests/` (new test files were invisible to the container) and `Makefile` (edits to it were silently ignored, since the container just ran whatever was baked in at the last build).

**`PYTHONPATH=/app`** is set explicitly in the compose environment because running a script directly (`python scripts/extract_scores.py`) only puts the script's own directory on Python's import path, not the repo root. Without this, `from src.extractors import ...` fails with `ModuleNotFoundError` depending on how a script is invoked.

**Ephemeral containers, not a long-running one:** every command runs as `docker compose run --rm ...` (spin up, run, tear down) rather than `docker compose up -d` plus repeated `exec`. This matches how CI would run the same commands and avoids state drifting between runs (leftover files, stale caches). Trade-off: an interrupted/killed process can occasionally leave a container not fully reaped despite `--rm`, which happened once and needed a manual `docker rm -f`.

**Permissions are split by cost, not by "is this Docker":** `.claude/settings.json` auto-allows no-cost operations (`docker-build`, `docker-shell`, `docker-view`, `docker-analyze`, `docker-clean`) but always asks first for anything that spends real API money (`docker-eval`, `docker-run`, `run-all`, or any `docker compose run` directly). Since Docker is what actually executes the paid API calls, the safe/costly split naturally lands on which Docker command is being run.

**Long-running evals get wrapped in `caffeinate -i`** (a macOS utility) to prevent the Mac from sleeping mid-run. Actual system sleep (not just a screen lock) suspends Docker Desktop's own VM along with any in-flight network requests, which is a good way to end up with the same kind of orphaned container mentioned above.

## Python

Standard library modules (`json`, `re`, `csv`, `argparse`, `pathlib`, `textwrap`, `typing`) show up throughout but aren't worth their own subsections. `python-dotenv` is listed in `requirements.txt` but currently **unused**. No script actually imports it, since API keys reach the container as real process environment variables via `docker-compose.yml`'s `env_file`, not by a Python script reading `.env` itself. Worth a cleanup at some point, noted here rather than silently left.

### pandas

The one dependency nearly every script touches. Used for:
- Reading CSVs (`data/processed/rag_groundedness_150.csv`, `reports/scored_results.csv`) and writing them back out
- `groupby(["provider", "prompt"])` in `compute_agreement.py`, the mechanism that turns "one row per graded item" into "one summary per experimental condition"
- `pd.isna()` in `summarize_calibration` to detect missing judge scores, since a CSV round-trip represents "missing" as float `NaN`, not Python `None`
- Building the confusion matrix's labeled `DataFrame` (row/column names, not just the raw numpy array)

### NumPy

Used narrowly, just for `np.mean()` in `compute_exact_agreement_rate` (`src/metrics.py`), the mean of an array of booleans (`human == judge`), which is the simplest way to express "fraction of exact matches" in one line.

### scikit-learn

Only `sklearn.metrics` is used, for the actual agreement math:
- `cohen_kappa_score`, both the plain (unweighted) and `weights="quadratic"` variants, computed via the same function with a different argument (see `compute_cohen_kappa` / `compute_quadratic_weighted_kappa` in `src/metrics.py`)
- `confusion_matrix`, the raw 3×3 array, which `compute_confusion_matrix` then wraps in a labeled `pandas.DataFrame` for readability

Deliberately not reimplemented by hand. The actual kappa math isn't something worth re-deriving and risking a subtle bug in, so this project's own tests check that *our wrapper* behaves correctly (missing-value handling, distance-sensitivity of QWK vs. plain kappa), not that sklearn's underlying formula is right.

### Hugging Face `datasets`

Used in exactly one place, `scripts/prepare_dataset.py`, to pull `wandb/RAGTruth-processed` via `load_dataset(...)`. This is what originally surfaced the schema mismatch bug (the real dataset's columns didn't match what the script assumed): `context`, `output`, and `hallucination_labels_processed`, not `context`/`response`/`labels`.

### matplotlib

The rendering engine underneath every figure in `src/visualization.py`. Notable choices:
- `matplotlib.use("Agg")` set explicitly before importing `pyplot`. There's no display in the Docker container, so the default interactive backend would fail; `Agg` renders straight to a file instead
- Manual `fig.suptitle()` / `fig.text()` positioning (in inches, converted to figure-fraction coordinates) rather than relying on `tight_layout()`'s automatic spacing. `tight_layout()` doesn't know about manually-placed text artists and reserves unpredictable extra space around them, which is what caused a large blank gap that needed `subplots_adjust()` (exact margins, no auto-avoidance) instead

### seaborn

Used for exactly one thing: `sns.heatmap(..., annot=True, fmt="d", cmap="Blues", square=True)`, the actual confusion-matrix rendering, layered on top of matplotlib's `Axes` objects. `square=True` is what guarantees square cells regardless of the surrounding figure/subplot dimensions, which turned out to be the direct fix once the figure-sizing math alone wasn't reliably producing square heatmaps.

### pytest

The test runner for everything in `tests/`. Notes specific to how it's used here:
- Plain `assert` statements throughout. No `unittest.TestCase`, since pytest rewrites bare `assert` to give rich failure diffs without needing that API
- `@pytest.mark.parametrize` for the extractor's shape-based test cases (`tests/test_extractors.py`), with explicit `ids=` so failures still read as a named scenario rather than a numeric index
- `capsys` fixture to assert on printed output (`test_print_confusion_matrices_outputs_group_header`)
- `tmp_path` fixture for file-writing tests (`test_write_csv_round_trip`), so tests never touch the real `reports/` directory
- No `import pytest` needed at all for the simplest tests. Only pulled in when a test actually uses a pytest-specific feature (`parametrize`, `approx`, `capsys`)
