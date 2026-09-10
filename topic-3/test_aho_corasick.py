"""Starter test suite for Topic 3: Aho–Corasick multi-pattern search.

This suite is intentionally incomplete. It covers only a few obvious
cases; you are expected to extend it — see topic-3/README.md.
"""

from hypothesis import given
from hypothesis import strategies as st

from aho_corasick import find_occurrences


def test_classic_example() -> None:
    assert find_occurrences("ushers", ["he", "she", "hers"]) == {
        "he": [2],
        "she": [1],
        "hers": [2],
    }


def test_single_pattern() -> None:
    assert find_occurrences("abcabcabc", ["abc"]) == {"abc": [0, 3, 6]}


def test_no_matches() -> None:
    assert find_occurrences("hello", ["xyz", "world"]) == {"xyz": [], "world": []}


def test_overlapping_occurrences() -> None:
    assert find_occurrences("aaaa", ["aa"]) == {"aa": [0, 1, 2]}


def test_pattern_inside_another_pattern() -> None:
    assert find_occurrences("abcd", ["abcd", "bc"]) == {"abcd": [0], "bc": [1]}


@given(text=st.text(), patterns=st.lists(st.text(min_size=1), min_size=1, max_size=5))
def test_reported_indices_actually_match(text: str, patterns: list[str]) -> None:
    result = find_occurrences(text, patterns)
    for pattern, indices in result.items():
        for index in indices:
            assert text[index : index + len(pattern)] == pattern
