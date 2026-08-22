# Tastes

Notes on research and engineering taste, distilled from building `judge-eval-harness`. Kept here for reuse on an about page, resume, and in interviews.

## Research Taste

- **Trust nothing you haven't calibrated.** Started from "how do you know your grader is right?" instead of assuming an LLM judge is reliable, and built a harness to measure judge/human agreement (Cohen's κ, quadratic weighted κ) before trusting the judge for anything downstream.
- **Pick the narrowest task that still proves the point.** Scoped to one task (RAG groundedness) and ~150 hand-labeled examples rather than a broad benchmark. Small and well-labeled beats large and unverifiable.
- **Assume failure modes exist, and go looking for them.** Didn't stop at a headline agreement score. Deliberately built adversarial probes (position bias, verbosity bias, self-preference, tautological rubrics) to see which ones actually move the judge's scores.
- **Verify the data before trusting the pipeline.** Caught a live schema mismatch (the real dataset's columns didn't match the script's assumed field names) by inspecting actual output, not by trusting a docstring.
- **A result isn't done until someone else can reproduce it.** The deliverable isn't a number, it's a Promptfoo-compatible repo plus a writeup with the disagreement matrix, built so someone else can rerun and check the claim.
- **Work on the unglamorous, unpublished problem.** Chose to build "the piece almost nobody publishes" (meta-evaluation of the evaluator) over another benchmark leaderboard entry.

## Engineering Taste

- **Reproducibility over convenience.** Standardized on Docker specifically to kill "works on my machine" drift, even though it took several rounds (Node version mismatch, missing `make` binary) to get right.
- **Cheap checks before expensive ones.** Smoke-test on a few rows before a full paid eval run. Run a free config validator before the paid run itself. Always spend the cheapest resource first to catch the same bug.
- **Guardrails should track actual risk, not blanket-allow or blanket-deny.** Split tool permissions so free operations run without friction, while anything that spends real API money always asks first. Friction proportional to consequence, not to the tool name.
- **Prevent mistakes at the moment they happen, not after.** Added an automatic check that runs on every relevant edit, instead of discovering a bad config only after a failed run.
- **Small, verifiable steps over big batches.** Prefers editing one or two files at a time and pausing to test/understand. In a system where a "run" costs real money and real time, unverified batching just means discovering several bugs at once instead of one.
- **Say the convention once, in the right place.** Team-shared conventions (tooling usage, doc style) go in the project's own instructions file; personal working-style preferences go in cross-session memory instead. Doesn't conflate "how this repo works" with "how I like to work."
- **Documentation is a UX problem too.** Pushed back on prose-heavy docs in favor of skimmable, heavily-bulleted structure. A README should be scannable, not just complete.
- **Organize documentation the way you organize thinking.** Structure (headings, grouping, ordering) should make the logic legible to a collaborator, not just hold the content. Documentation is a way of thinking out loud clearly, meant to be followed by someone else.
- **Write for what the reader needs, not the path taken to get there.** Docs are framed around outcomes and benefits to whoever's using the project (a researcher iterating fast, a teammate onboarding), not as a chronological log of the steps taken to build it.
