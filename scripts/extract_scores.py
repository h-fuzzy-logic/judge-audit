"""Reads a Promptfoo results.json export, extracts each judge's score via
src.extractors.extract_score, and writes a scored CSV for calibration analysis.

Usage:
    python scripts/extract_scores.py --results reports/results.json --output reports/scored_results.csv
"""
import argparse
import csv
import json
from pathlib import Path

from src.extractors import extract_score


def load_results(results_path: str) -> list[dict]:
    with open(results_path) as f:
        data = json.load(f)
    return data["results"]["results"]


def score_results(rows: list[dict]) -> list[dict]:
    scored = []
    for row in rows:
        raw_output = row.get("response", {}).get("output", "")
        judge_score = extract_score(raw_output)

        # prompt.label is "<file path>: <full prompt text>" - keep just the path
        prompt_label = row.get("prompt", {}).get("label", "")
        prompt_id = prompt_label.split(":", 1)[0] if ":" in prompt_label else prompt_label

        scored.append({
            "provider": row.get("provider", {}).get("id"),
            "prompt": prompt_id,
            "context": row["vars"].get("context"),
            "response": row["vars"].get("response"),
            "human_score": int(row["vars"]["human_groundedness_score"]),
            "judge_score": judge_score,
            "parse_failed": judge_score is None,
        })
    return scored


def write_csv(scored: list[dict], output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["provider", "prompt", "context", "response", "human_score", "judge_score", "parse_failed"]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="reports/results.json")
    parser.add_argument("--output", default="reports/scored_results.csv")
    args = parser.parse_args()

    rows = load_results(args.results)
    scored = score_results(rows)
    write_csv(scored, args.output)

    n_failed = sum(1 for r in scored if r["parse_failed"])
    print(f"Scored {len(scored)} rows -> {args.output}")
    print(f"Parse failures: {n_failed} ({n_failed / len(scored):.1%})")


if __name__ == "__main__":
    main()
