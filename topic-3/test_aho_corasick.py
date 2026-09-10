"""Starter test suite for Topic 3: Aho–Corasick multi-pattern search.

Property-based tests written with Hypothesis: instead of hardcoding
input/output pairs, each test constructs random inputs with a known
property and checks that the property holds for the result.

This suite is intentionally incomplete. It covers only a few obvious
properties; you are expected to extend it — see topic-3/README.md.
"""

from hypothesis import given
from hypothesis import strategies as st

from aho_corasick import find_occurrences


@given(
    prefix=st.text(),
    pattern=st.text(min_size=1),
    suffix=st.text(),
    other_patterns=st.lists(st.text(min_size=1), max_size=4),
)
def test_pattern_inserted_at_known_position_is_found(
    prefix: str, pattern: str, suffix: str, other_patterns: list[str]
) -> None:
    text = prefix + pattern + suffix
    result = find_occurrences(text, [pattern, *other_patterns])
    assert len(prefix) in result[pattern]


@given(parts=st.lists(st.text(), min_size=2, max_size=6), pattern=st.text(min_size=1))
def test_pattern_inserted_several_times_is_found_at_every_insertion(
    parts: list[str], pattern: str
) -> None:
    text = pattern.join(parts)
    insertion_positions = []
    position = 0
    for part in parts[:-1]:
        position += len(part)
        insertion_positions.append(position)
        position += len(pattern)

    result = find_occurrences(text, [pattern])
    for insertion_position in insertion_positions:
        assert insertion_position in result[pattern]


@given(
    text=st.text(alphabet="ab"),
    patterns=st.lists(st.text(alphabet="xyz", min_size=1), min_size=1, max_size=5),
)
def test_patterns_from_disjoint_alphabet_are_never_found(
    text: str, patterns: list[str]
) -> None:
    assert find_occurrences(text, patterns) == {pattern: [] for pattern in patterns}


@given(text=st.text(), patterns=st.lists(st.text(min_size=1), min_size=1, max_size=5))
def test_every_pattern_is_present_in_the_result(text: str, patterns: list[str]) -> None:
    assert set(find_occurrences(text, patterns)) == set(patterns)


@given(text=st.text(), patterns=st.lists(st.text(min_size=1), min_size=1, max_size=5))
def test_reported_indices_actually_match(text: str, patterns: list[str]) -> None:
    result = find_occurrences(text, patterns)
    for pattern, indices in result.items():
        for index in indices:
            assert text[index : index + len(pattern)] == pattern
