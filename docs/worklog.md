# Worklog

## Summary

| Date | Goal | Cost | Key Metrics | Details |
|---|---|---|---|---|
| 2024-08-30 | CoT vs. strict rubric baseline | ~50 Gemini Flash evals | Recall 0.26 → 0.56 (p=0.0002); κ 0.40 → 0.53 | [Experiment 1](#2024-08-30--strict-vs-cot-rubric-baseline) |

---

## Sessions (newest first)

### 2024-08-30 — Strict vs. CoT rubric baseline

| Field | Details |
|---|---|
| **Goal** | Dry-run evaluation pipeline end-to-end with two judge configs to establish reproducibility. |
| **Changed** | `experiments/ragtruth/01-strict-vs-cot-rubric/` (promptfooconfig.yaml, results.json, scored_results.csv, README.md). Refined `src/significance.py` (paired bootstrap) and `src/metrics.py` (class-wise recall/precision). |
| **Learned** | CoT more than doubles hallucination detection (recall 0.26 → 0.56, p=0.0002). κ improves 0.40 → 0.53 (p=0.027). Gains robust but narrow: single model, single dataset. Label construction may favor CoT structure. |
| **Cost** | ~50 Gemini Flash evals (standard pricing). |
