import pytest

from src.extractors import extract_score


@pytest.mark.parametrize(
    "raw_output, expected",
    [
        pytest.param('{"score": 1, "reasoning": "some claims unsupported"}', 1, id="bare-json"),
        pytest.param('```json\n{"score": 2, "reasoning": "fully supported"}\n```', 2, id="labeled-fence"),
        pytest.param('```\n{"score": 0, "reasoning": "contradicts context"}\n```', 0, id="unlabeled-fence"),
        pytest.param('{"score": 0, "reasoning": "the claim {x} is unsupported by {y}"}', 0, id="nested-braces"),
        pytest.param('{"score": 2, "reasoning": "all good"}\n\nThanks for using the API!', 2, id="trailing-content"),
        pytest.param("score: 1 (not valid json, missing quotes and braces)", 1, id="regex-fallback"),
        pytest.param('{"score": "2", "reasoning": "ok"}', 2, id="score-as-json-string"),
        pytest.param('{"score": "high", "reasoning": "vague"}', None, id="non-numeric-score"),
        pytest.param("", None, id="empty-string"),
        pytest.param(None, None, id="none-input"),
        pytest.param("the model refused to answer", None, id="unparseable-garbage"),
    ],
)
def test_extract_score(raw_output, expected):
    assert extract_score(raw_output) == expected


def test_chain_of_thought_prose_before_json():
    raw = (
        "1. Claim: the venue has multiple floors. Supported.\n"
        "2. Claim: it serves food. Unsupported.\n\n"
        '{"score": 1, "reasoning": "one unsupported claim"}'
    )
    assert extract_score(raw) == 1
