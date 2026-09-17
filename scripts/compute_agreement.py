"""Reads a scored results CSV (from extract_scores.py), computes agreement
metrics per (provider, prompt) group, and writes a summary CSV.

Usage:
    python scripts/compute_agreement.py \
        --input <experiment_dir>/scored_results.csv \
        --output <experiment_dir>/agreement_summary.csv
"""
import argparse
import csv
import re
from pathlib import Path

import pandas as pd

from src.metrics import compute_confusion_matrix, summarize_calibration
from src.visualization import plot_confusion_matrix, plot_confusion_matrix_grid


def compute_group_summaries(df: pd.DataFrame) -> list[dict]:
    summaries = []
    for (provider, prompt), group in df.groupby(["provider", "prompt"]):
        summary = summarize_calibration(group["human_score"], group["judge_score"])
        summaries.append({"provider": provider, "prompt": prompt, **summary})
    return summaries


def write_csv(summaries: list[dict], output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(summaries[0].keys())
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)


def print_confusion_matrices(df: pd.DataFrame) -> None:
    for (provider, prompt), group in df.groupby(["provider", "prompt"]):
        valid = group.dropna(subset=["judge_score"])
        print(f"\n{provider} / {prompt}")
        print(compute_confusion_matrix(valid["human_score"], valid["judge_score"], label_sep="="))


def _safe_filename(*parts: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", "_".join(parts)).strip("_")


# Curated display names for known rubric prompts, framed around the actual
# experimental variable (reasoning style) rather than the internal file
# name. Anything not listed falls back to a title-cased file stem, so a
# new rubric prompt gets a readable label instead of breaking.
_PROMPT_DISPLAY_NAMES = {
    "rubric_v1_strict": "Without Chain-of-Thought",
    "rubric_v2_chain_of_thought": "With Chain-of-Thought",
}


def _clean_prompt_name(prompt: str) -> str:
    # "configs/prompts/rubric_v1_strict.txt" -> "Without Chain-of-Thought"
    stem = Path(prompt).stem
    return _PROMPT_DISPLAY_NAMES.get(stem, stem.replace("_", " ").title())


def save_confusion_matrix_figures(
    df: pd.DataFrame,
    output_dir: str = "experiments/ragtruth/01-strict-vs-cot-rubric/figures",
) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    for (provider, prompt), group in df.groupby(["provider", "prompt"]):
        valid = group.dropna(subset=["judge_score"])
        matrix = compute_confusion_matrix(valid["human_score"], valid["judge_score"], label_sep="=")
        output_path = output_dir / f"confusion_{_safe_filename(provider, prompt)}.png"
        title = f"{provider} / {_clean_prompt_name(prompt)}"
        plot_confusion_matrix(matrix, title, output_path)
        paths.append(output_path)
    return paths


def _build_comparison_headline(prompt_summaries: dict[str, dict]) -> str:
    """Plain-language summary of which rubric agrees with human labels best,
    for readers who should know what to look for before studying the grid."""
    ranked = sorted(
        ((name, s) for name, s in prompt_summaries.items() if s["cohen_kappa"] is not None),
        key=lambda item: item[1]["cohen_kappa"],
        reverse=True,
    )
    if len(ranked) < 2:
        return "Judge vs. human agreement"

    best_name, best = ranked[0]
    worst_name, worst = ranked[-1]
    if best_name == worst_name:
        return f"{best_name}: Cohen's κ = {best['cohen_kappa']:.2f}"
    return (
        f"{best_name}\n"
        f"agrees with human labels more than\n"
        f"{worst_name} (κ {best['cohen_kappa']:.2f} vs {worst['cohen_kappa']:.2f})"
    )


def save_combined_confusion_matrix_figure(
    df: pd.DataFrame,
    output_dir: str = "experiments/ragtruth/01-strict-vs-cot-rubric/figures",
) -> list[Path]:
    """One image per provider, with each of that provider's prompts as its own
    subplot, headlined by which rubric performed best and footed by the model name."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    for provider, provider_group in df.groupby("provider"):
        matrices = {}
        summaries = {}
        for prompt, group in provider_group.groupby("prompt"):
            valid = group.dropna(subset=["judge_score"])
            name = _clean_prompt_name(prompt)
            matrices[name] = compute_confusion_matrix(valid["human_score"], valid["judge_score"], label_sep="=")
            summaries[name] = summarize_calibration(group["human_score"], group["judge_score"])

        title = _build_comparison_headline(summaries)
        output_path = output_dir / f"combined_{_safe_filename(provider)}.png"
        plot_confusion_matrix_grid(matrices, title=title, subtitle=provider, output_path=output_path)
        paths.append(output_path)
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="experiments/ragtruth/01-strict-vs-cot-rubric/scored_results.csv")
    parser.add_argument("--output", default="experiments/ragtruth/01-strict-vs-cot-rubric/agreement_summary.csv")
    parser.add_argument("--figures-dir", default="experiments/ragtruth/01-strict-vs-cot-rubric/figures")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    summaries = compute_group_summaries(df)
    write_csv(summaries, args.output)

    for summary in summaries:
        print(summary)
    print_confusion_matrices(df)

    figure_paths = save_confusion_matrix_figures(df, args.figures_dir)
    figure_paths += save_combined_confusion_matrix_figure(df, args.figures_dir)
    for path in figure_paths:
        print(f"Saved confusion matrix heatmap to {path}")

    print(f"\nSummary written to {args.output}")


if __name__ == "__main__":
    main()
