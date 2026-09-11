"""Starter test suite for Topic 3: Aho–Corasick multi-pattern search.

Property-based tests written with Hypothesis. All test data comes from
the composite strategies in ``aho_generators.py`` — tests never build
their inputs inline, they only assert the property the generator
guarantees by construction.

This suite is intentionally incomplete. It covers only a few obvious
properties; you are expected to extend it (and the generators) — see
topic-3/README.md.
"""

from aho_corasick import find_occurrences
from aho_generators import (
    arbitrary_search_inputs,
    texts_with_absent_patterns,
    texts_with_pattern_inserted_many_times,
    texts_with_pattern_inserted_once,
)
from hypothesis import given


# Completeness (one occurrence): the generator placed one tracked
# pattern at a known position and mixed unrelated patterns into the
# search set; the tracked pattern must be reported at that position.
@given(case=texts_with_pattern_inserted_once())
def test_pattern_inserted_at_known_position_is_found(case) -> None:
    result = find_occurrences(case.text, case.patterns)
    assert case.position in result[case.inserted_pattern]


# Completeness (many occurrences): every deliberate insertion position
# must be reported. Extra incidental matches are allowed — the seams
# between fragments can accidentally form additional occurrences.
@given(case=texts_with_pattern_inserted_many_times())
def test_pattern_inserted_several_times_is_found_at_every_insertion(case) -> None:
    result = find_occurrences(case.text, [case.pattern])
    for position in case.positions:
        assert position in result[case.pattern]


# Absence: the generator draws the text and all patterns from disjoint
# alphabets, so every pattern must map to an empty list of indices.
@given(case=texts_with_absent_patterns())
def test_patterns_from_disjoint_alphabet_are_never_found(case) -> None:
    expected = {pattern: [] for pattern in case.patterns}
    assert find_occurrences(case.text, case.patterns) == expected


# Shape of the result: every requested pattern must be present as a
# key, even when it does not occur in the text.
@given(case=arbitrary_search_inputs())
def test_every_pattern_is_present_in_the_result(case) -> None:
    assert set(find_occurrences(case.text, case.patterns)) == set(case.patterns)


# Soundness: for arbitrary inputs nothing is known about where the
# patterns occur — but every index reported for a pattern must point
# at a real occurrence of that pattern when the text is sliced there.
@given(case=arbitrary_search_inputs())
def test_reported_indices_actually_match(case) -> None:
    result = find_occurrences(case.text, case.patterns)
    for pattern, indices in result.items():
        for index in indices:
            assert case.text[index : index + len(pattern)] == pattern
