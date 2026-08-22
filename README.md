# judge-eval-harness

## Project Summary

> "how do you know your grader is right?"

**Goal:** build the piece almost nobody publishes. A harness that measures whether an LLM judge agrees with human labels.

- ~150 hand-labeled examples on one narrow task (RAG groundedness is the cleanest)
- Run 3–4 judge configs
- Report Cohen's κ and judge–human agreement per rubric dimension
- Deliberately probe known failure modes (position bias, verbosity bias, self-preference, tautological rubrics) and show which ones move scores
- Ship as a Promptfoo-compatible repo plus a writeup with the disagreement matrix

## Documentation

- [`docs/research.md`](docs/research.md): the actual research content. Dataset, hypotheses, experiments and results.
- [`docs/approaches.md`](docs/approaches.md): how each part of the tooling works and why (Promptfoo, Docker, Python libraries), built up incrementally.
- [`docs/tastes.md`](docs/tastes.md): research and engineering taste notes distilled from building this project.
- [`docs/repo-structure.md`](docs/repo-structure.md): the intended repo layout.
- [`CLAUDE.md`](CLAUDE.md): working conventions for this repo (Docker/Makefile usage, doc style).

## Reproducibility & Efficiency

Built so a researcher can iterate fast without babysitting infrastructure or re-deriving "how do I run this again."

**Setup**
- **One-command, no-drift setup.** `make docker-build` gives everyone the same Python + Node + Promptfoo environment. No "works on my machine," no manually matching a Node version to Promptfoo's requirements.
- **Fast edit loop, no rebuild tax.** `data/`, `configs/`, `reports/`, `src/`, `scripts/` are all bind-mounted into the container. Rubric/metric/script edits take effect immediately; a rebuild is only needed after touching `requirements.txt`.

**Iterating without wasting spend**
- **Cheap smoke tests before a full run.** `--filter-first-n <N>` validates a new rubric or provider against a handful of rows before committing to the full 150-row × N-provider run.
- **Zero-cost config checks.** `promptfoo validate` catches bad paths/YAML/provider IDs in seconds, no API spend.
- **Judge/provider swaps are single-line edits.** Every rubric prompt and provider in `configs/promptfooconfig.yaml` is commented in/out individually. No code changes needed to add or drop a model.
- **Guardrails tuned for cost, not just correctness.** `.claude/settings.json`:
  - Auto-allows no-cost operations: `docker-build`, `docker-shell`, `docker-view`, `prepare`, `analyze`, `test`
  - Always asks first for anything that spends real API money: `eval`, `docker-eval`, `run-all`, `docker-run`, any `docker compose run`
- **Config mistakes caught before they cost anything.** A `PostToolUse` hook runs `promptfoo validate` automatically whenever `configs/promptfooconfig.yaml` changes, instead of surfacing the error after a failed (and possibly paid) `make eval`.

**History & team consistency**
- **Persistent, shareable eval history.** Promptfoo's own eval store (`.promptfoo/`) is bind-mounted too. `make docker-view` browses every past run's outputs/scores/errors, not just the latest, and survives container exits.
- **Conventions documented once.** `CLAUDE.md` records "always use the Makefile, always run through Docker" so work doesn't quietly drift into a mix of local and containerized runs with two disconnected `.promptfoo` histories (a real failure mode hit while building this harness).

## Working with Claude Code on This Project

This repo was built interactively with Claude Code. Two things worth carrying forward:

**Cross-session memory**
- Claude Code persists working *preferences* (not just project facts) across sessions and projects.
- Example: "work in small steps, one or two files at a time, then pause" is a standing preference, not something re-explained every session.
- Project-specific conventions (Docker/Makefile usage, directory layout, doc style) live in `CLAUDE.md` instead, since those apply to anyone working in this repo, not just one person's working style.

**Why going slow is actually the fast path here**

Every bug hit while building this project was caught cheaply because each change was reviewed and smoke-tested in isolation before moving on:

- Dataset schema mismatch in `prepare_dataset.py`
- Two relative-path errors in `configs/promptfooconfig.yaml`
- A missing `make` binary in the Docker image
- An outdated Node version in the Docker image

Batching those same changes together would have meant discovering all four failures only after kicking off a paid, 150-row eval run. That's the expensive way to learn the same lesson. When a "run" means real API spend and real wall-clock time, verifying one small change at a time is what makes iterating *quickly* possible, not what slows it down.
