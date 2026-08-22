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
- `data/`, `configs/`, `reports/`, `src/`, `scripts/`, and `.promptfoo/` are all bind-mounted into the container (see `docker-compose.yml`). Code and config edits and pipeline outputs sync live with the host. A rebuild (`make docker-build`) is only needed after changing `requirements.txt`.
- `.promptfoo/` holds Promptfoo's own eval history/cache (git-ignored), separate from the `reports/*.json` files written via `-o`. Running Promptfoo outside Docker writes to `~/.promptfoo` on the host instead, splitting history across two stores. Don't do that.
- `check-env` auto-copies `.env.example` to `.env` if missing; real API keys still need to be filled in by hand.

## Git commits

- Keep commit messages short: a single imperative-mood line, no body. Only add a body if the change genuinely needs explanation that isn't obvious from the diff or the subject line.

## Documentation style

- Text generated for this project (README, docs) should be structured and skimmable: clear headings, heavy use of bulleted lists over prose paragraphs, so the outline is visible at a glance.
- No em dashes. Use a comma, parentheses, or a period instead.
