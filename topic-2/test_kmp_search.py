"""Starter test suite for Topic 2: Knuth–Morris–Pratt substring search.

Property-based tests written with Hypothesis. All test data comes from
the composite strategies in ``kmp_generators.py`` — tests never build
their inputs inline, they only assert the property the generator
guarantees by construction.

This suite is intentionally incomplete. It covers only a few obvious
properties; you are expected to extend it (and the generators) — see
topic-2/README.md.
"""

from hypothesis import given
from kmp_generators import (
    arbitrary_search_inputs,
    periodic_texts,
    texts_with_absent_pattern,
    texts_with_pattern_inserted_many_times,
    texts_with_pattern_inserted_once,
)
from kmp_search import find_occurrences


# Completeness (one occurrence): the generator placed the pattern at a
# known position, so that position must be among the reported indices.
@given(case=texts_with_pattern_inserted_once())
def test_pattern_inserted_at_known_position_is_found(case) -> None:
    assert case.position in find_occurrences(case.text, case.pattern)


# Completeness (many occurrences): every deliberate insertion position
# must be reported. Extra incidental matches are allowed — the seams
# between fragments can accidentally form additional occurrences.
@given(case=texts_with_pattern_inserted_many_times())
def test_pattern_inserted_several_times_is_found_at_every_insertion(case) -> None:
    result = find_occurrences(case.text, case.pattern)
    for position in case.positions:
        assert position in result


# Overlap handling: in a periodic text (the unit repeated N times) the
# unit occurs at every period boundary. Repetitive inputs like these
# exercise the prefix-function logic that makes KMP different from a
# naive scan — a broken shortcut implementation typically misses
# overlapping occurrences here.
@given(case=periodic_texts())
def test_unit_is_found_at_every_period_boundary_of_periodic_text(case) -> None:
    result = find_occurrences(case.text, case.unit)
    for i in range(case.repetitions):
        assert i * len(case.unit) in result


# Absence: the generator draws the text and the pattern from disjoint
# alphabets, so reporting any occurrence at all would be a bug.
@given(case=texts_with_absent_pattern())
def test_pattern_from_disjoint_alphabet_is_never_found(case) -> None:
    assert find_occurrences(case.text, case.pattern) == []


# Soundness: for arbitrary inputs nothing is known about where the
# pattern occurs — but every index the function *does* report must
# point at a real occurrence when the text is sliced there.
@given(case=arbitrary_search_inputs())
def test_reported_indices_actually_match(case) -> None:
    for index in find_occurrences(case.text, case.pattern):
        assert case.text[index : index + len(case.pattern)] == case.pattern
