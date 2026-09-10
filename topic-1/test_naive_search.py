"""Starter test suite for Topic 1: Naive substring search.

This suite is intentionally incomplete. It covers only a few obvious
cases; you are expected to extend it — see topic-1/README.md.
"""

from hypothesis import given
from hypothesis import strategies as st

from naive_search import find_occurrences


def test_pattern_found_once() -> None:
    assert find_occurrences("hello world", "world") == [6]


def test_pattern_found_multiple_times() -> None:
    assert find_occurrences("abcabcabc", "abc") == [0, 3, 6]


def test_overlapping_occurrences() -> None:
    assert find_occurrences("aaaa", "aa") == [0, 1, 2]


def test_pattern_not_found() -> None:
    assert find_occurrences("hello", "xyz") == []


def test_pattern_equals_text() -> None:
    assert find_occurrences("abc", "abc") == [0]


@given(text=st.text(), pattern=st.text(min_size=1))
def test_reported_indices_actually_match(text: str, pattern: str) -> None:
    for index in find_occurrences(text, pattern):
        assert text[index : index + len(pattern)] == pattern
