"""Extracts a 0-2 groundedness score from a judge's raw text output."""
import json
import re
from typing import Optional

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)
_SCORE_FALLBACK_RE = re.compile(r'"?score"?\s*[:=]\s*(\d)', re.IGNORECASE)

_decoder = json.JSONDecoder()


def _parse_first_json_object(text: str) -> Optional[dict]:
    # raw_decode parses one JSON value starting at an index and ignores
    # trailing content — handles both "JSON + junk" and "prose + JSON"
    # (chain-of-thought output) without needing to guess where it ends.
    start = text.find("{")
    while start != -1:
        try:
            obj, _ = _decoder.raw_decode(text, start)
            return obj
        except json.JSONDecodeError:
            start = text.find("{", start + 1)
    return None


def extract_score(raw_output: str) -> Optional[int]:
    """Parses a judge's score from its raw output.

    Tries the response as-is, then with a markdown code fence stripped
    (some judges wrap JSON in ```json blocks despite instructions not to),
    then falls back to a bare regex match as a last resort. Fallback tiers
    are keyed to output *shape*, not to which model produced it, so a new
    provider is handled without new code.
    """
    if not raw_output:
        return None

    fence_match = _FENCE_RE.search(raw_output)
    candidates = [fence_match.group(1), raw_output] if fence_match else [raw_output]

    for candidate in candidates:
        obj = _parse_first_json_object(candidate)
        if obj and "score" in obj:
            try:
                return int(obj["score"])
            except (TypeError, ValueError):
                continue

    fallback = _SCORE_FALLBACK_RE.search(raw_output)
    if fallback:
        return int(fallback.group(1))

    return None
