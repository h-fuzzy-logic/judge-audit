# judge-eval-harness

## Working conventions

- **Always use the Makefile**, not raw `python`/`npx` commands. Every workflow step has a target: `make prepare`, `make eval`, `make analyze`, `make run-all`.
- **Always run through Docker**, not natively on the host. Prefer the `docker-*` targets over their bare equivalents:
  - `make docker-build`: build the image
  - `make docker-run`: full pipeline (`prepare -> eval -> analyze`) in Docker
  - `make docker-eval`: eval step only, skips `analyze`
  - `make docker-shell`: debug shell inside the container
  - `make docker-view`: Promptfoo browser UI at http://localhost:15500
  - `make docker-clean`: remove containers/image/volumes for this project
- `data/`, `configs/`, `experiments/`, `src/`, `scripts/`, and `.promptfoo/` are all bind-mounted into the container (see `docker-compose.yml`). Code and config edits and pipeline outputs sync live with the host. A rebuild (`make docker-build`) is only needed after changing `requirements.txt`.
- `.promptfoo/` holds Promptfoo's own eval history/cache (git-ignored), separate from each experiment's own `results.json`/`scored_results.csv` files written via `-o`. Running Promptfoo outside Docker writes to `~/.promptfoo` on the host instead, splitting history across two stores. Don't do that.
- Each experiment lives in `experiments/<dataset>/<experiment-name>/` with its own `promptfooconfig.yaml` and outputs. `configs/prompts/`, `data/`, `src/`, and `scripts/` are shared across experiments, not duplicated per experiment. The Makefile's `EXPERIMENT` variable points `eval`/`analyze`/`clean` at the active experiment directory; update it (or override with `make eval EXPERIMENT=...`) when starting a new experiment.
- `check-env` auto-copies `.env.example` to `.env` if missing; real API keys still need to be filled in by hand.

## Git commits

- Keep commit messages short: a single imperative-mood line, no body. Only add a body if the change genuinely needs explanation that isn't obvious from the diff or the subject line. Add period at the end. 

## Documentation Style Guidelines

### Persona & Core Objective
Act as a principal technical writer and system architect. Convert rough notes, requirements, or ideas into dense, skimmable, and factual documentation. Aim for extreme brevity.

### Syntax & Compression Rules
- Telegraphic Style: Favor short noun phrases and predicate clauses over full narrative sentences. 
- Strict Word Ceiling: Keep total section outputs under 70 words.
- Zero Fluff & Meta-Talk: Omit introductory setups, transitional clauses, self-justifications, hedging, greetings, and sign-offs.
- Direct Punctuation: Use colons for cause/effect instead of joining words (e.g., "Risk: format alignment" instead of "The risk is that it might align with the format").
- Punctuation Constraint: Never use em dashes (—). Use commas, parentheses, or periods instead.

### Format & Layout
- Scannable Layout: Use bolding for key concepts. Keep prose minimal.
- Lead First: Put the single most critical point in the first 5 words.

### Calibration Example (Match This Density & Style)
[Input]
- Primary goal: exercise the meta-evaluation pipeline end to end. Dataset prep, two judge configs, structured score extraction... The hypothesis is secondary... Known limit: The CoT rubric's claim-by-claim structure mirrors how the ground-truth label was built, so the gain can't be attributed to reasoning...

[Output]
**Purpose:** Dry-run the evaluation pipeline ($n=150$) to establish a reusable baseline.

**Key Risk:** Performance gains may reflect rubric-format alignment rather than improved model reasoning. Isolating reasoning requires a non-matching prompt or human re-rating.

### Diagrams
- Diagrams use Mermaid fenced code blocks (```` ```mermaid ````), not ASCII art. 
