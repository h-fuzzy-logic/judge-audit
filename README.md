# judge-eval-harness

## Project Summary
A harness that measures whether an LLM judge agrees with human labels.

LLM-as-judge is used everywhere now (evals, RLHF/DPO reward signals, benchmark grading) but is rarely checked against real human judgment. A judge that quietly disagrees with humans corrupts every downstream decision built on top of it.

This harness measures that agreement directly, using Cohen's κ, quadratic weighted κ, exact agreement rate, and confusion matrices, on one narrow task: RAG groundedness. See [Research](docs/research.md) for the dataset, hypotheses, and current results.

This repo was built interactively with Claude Code with project-specific conventions in `CLAUDE.md`.

## Documentation

- [Research](docs/research.md): Dataset, hypotheses, experiments and results.
- [Technologies](docs/approaches.md): Why each technology was chosen and how it is used in this repo (Promptfoo, Docker, Python libraries).
- [Research Taste and Engineering Taste](docs/tastes.md): My judgements and principles that drive my work. 
- [Repository Structure](docs/repo-structure.md): The repo layout.
- [`CLAUDE.md`](CLAUDE.md): Conventions for this repo.

## Reproducibility & Velocity

Reproducible environments, cost-aware guardrails, and a fast experiment loop are some of the disciplines every team (a research lab, a startup, an enterprise ML org) needs to move fast without breaking things or burning budget. Built so anyone picking this up can iterate quickly without babysitting infrastructure or trying to remember "how do I run this again."

### Reproducible environments
- **One-command, no-drift setup.** `make docker-build` gives everyone the same environment. No "works on my machine" headaches.
- **One Makefile, not five remembered commands.** `make prepare`, `make eval`, `make analyze` are the same entry points for every contributor, so no one's typing a slightly different `docker compose run` or `npx promptfoo eval` flag by hand.
- **Conventions documented once.** `CLAUDE.md` captures them, so work doesn't quietly drift back to ad hoc, undocumented commands.

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
