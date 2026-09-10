"""Starter test suite for Topic 2: Knuth–Morris–Pratt substring search.

This suite is intentionally incomplete. It covers only a few obvious
cases; you are expected to extend it — see topic-2/README.md.
"""

from hypothesis import given
from hypothesis import strategies as st

from kmp_search import find_occurrences


def test_pattern_found_once() -> None:
    assert find_occurrences("hello world", "world") == [6]


def test_pattern_found_multiple_times() -> None:
    assert find_occurrences("abcabcabc", "abc") == [0, 3, 6]


def test_overlapping_occurrences() -> None:
    assert find_occurrences("aaaa", "aa") == [0, 1, 2]


def test_pattern_not_found() -> None:
    assert find_occurrences("hello", "xyz") == []


def test_repetitive_pattern_with_partial_matches() -> None:
    assert find_occurrences("ababababa", "ababa") == [0, 2, 4]


@given(text=st.text(), pattern=st.text(min_size=1))
def test_reported_indices_actually_match(text: str, pattern: str) -> None:
    for index in find_occurrences(text, pattern):
        assert text[index : index + len(pattern)] == pattern
