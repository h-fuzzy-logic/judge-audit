# Research

## Completed Experiments

| Experiment | Judge | n | Key Finding |
|---|---|---|---|
| [Strict vs. CoT rubric](/experiments/ragtruth/01-strict-vs-cot-rubric/README.md) | google:gemini-3.5-flash-lite | 150 | CoT doubles class 0 recall: 0.26 → 0.56 (p=0.0002). κ: 0.40 → 0.53. |

## Roadmap 🚧

### How do you know your grader is right? 
- ⚡ Up Next:
  - Position bias (does response order affect the score?)
  - Verbosity bias (does a longer/padded response get scored more favorably regardless of accuracy?)
  - Self-preference (does a judge favor output from its own model family?)
  - Tautological rubrics (does a vague/circular rubric inflate agreement artificially?)
  - Cross-provider comparison (OpenAI/Anthropic judges are configured but not yet run, pending API keys)




