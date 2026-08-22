import csv

import pandas as pd
import pytest

from scripts.compute_agreement import compute_group_summaries, print_confusion_matrices, write_csv


def _row(provider, prompt, human, judge):
    return {
        "provider": provider,
        "prompt": prompt,
        "context": "c",
        "response": "r",
        "human_score": human,
        "judge_score": judge,
    }


def test_compute_group_summaries_single_group():
    df = pd.DataFrame(
        [
            _row("providerA", "promptA", 0, 0),
            _row("providerA", "promptA", 1, 1),
            _row("providerA", "promptA", 2, 1),
        ]
    )
    summaries = compute_group_summaries(df)
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary["provider"] == "providerA"
    assert summary["prompt"] == "promptA"
    assert summary["n_items"] == 3
    assert summary["n_valid"] == 3
    assert summary["n_parse_failures"] == 0
    assert summary["exact_agreement_rate"] == pytest.approx(2 / 3)


def test_compute_group_summaries_multiple_groups_kept_separate():
    df = pd.DataFrame(
        [
            _row("providerA", "promptA", 0, 0),
            _row("providerA", "promptA", 1, 1),
            _row("providerB", "promptA", 0, 1),
            _row("providerB", "promptA", 1, 1),
        ]
    )
    summaries = compute_group_summaries(df)
    by_key = {(s["provider"], s["prompt"]): s for s in summaries}
    assert set(by_key.keys()) == {("providerA", "promptA"), ("providerB", "promptA")}
    assert by_key[("providerA", "promptA")]["exact_agreement_rate"] == 1.0
    assert by_key[("providerB", "promptA")]["exact_agreement_rate"] == 0.5


def test_compute_group_summaries_counts_parse_failures():
    df = pd.DataFrame(
        [
            _row("providerA", "promptA", 0, 0),
            _row("providerA", "promptA", 1, None),
            _row("providerA", "promptA", 2, 2),
        ]
    )
    summary = compute_group_summaries(df)[0]
    assert summary["n_items"] == 3
    assert summary["n_valid"] == 2
    assert summary["n_parse_failures"] == 1


def test_write_csv_round_trip(tmp_path):
    summaries = [
        {
            "provider": "providerA",
            "prompt": "promptA",
            "n_items": 3,
            "n_valid": 3,
            "n_parse_failures": 0,
            "cohen_kappa": 1.0,
            "quadratic_weighted_kappa": 1.0,
            "exact_agreement_rate": 1.0,
        }
    ]
    output_path = tmp_path / "summary.csv"
    write_csv(summaries, str(output_path))

    with open(output_path) as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    assert rows[0]["provider"] == "providerA"
    assert rows[0]["exact_agreement_rate"] == "1.0"


def test_write_csv_creates_parent_directory(tmp_path):
    summaries = [
        {
            "provider": "p",
            "prompt": "q",
            "n_items": 1,
            "n_valid": 1,
            "n_parse_failures": 0,
            "cohen_kappa": 1.0,
            "quadratic_weighted_kappa": 1.0,
            "exact_agreement_rate": 1.0,
        }
    ]
    output_path = tmp_path / "nested" / "summary.csv"
    write_csv(summaries, str(output_path))
    assert output_path.exists()


def test_print_confusion_matrices_outputs_group_header(capsys):
    df = pd.DataFrame(
        [
            _row("providerA", "promptA", 0, 0),
            _row("providerA", "promptA", 1, 1),
        ]
    )
    print_confusion_matrices(df)
    captured = capsys.readouterr()
    assert "providerA / promptA" in captured.out
    assert "judge=0" in captured.out
