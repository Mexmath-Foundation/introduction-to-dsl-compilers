"""Starter test suite for Topic 2: Knuth–Morris–Pratt substring search.

Property-based tests written with Hypothesis: instead of hardcoding
input/output pairs, each test constructs random inputs with a known
property and checks that the property holds for the result.

This suite is intentionally incomplete. It covers only a few obvious
properties; you are expected to extend it — see topic-2/README.md.
"""

from hypothesis import given
from hypothesis import strategies as st

from kmp_search import find_occurrences


@given(prefix=st.text(), pattern=st.text(min_size=1), suffix=st.text())
def test_pattern_inserted_at_known_position_is_found(
    prefix: str, pattern: str, suffix: str
) -> None:
    text = prefix + pattern + suffix
    assert len(prefix) in find_occurrences(text, pattern)


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

    result = find_occurrences(text, pattern)
    for insertion_position in insertion_positions:
        assert insertion_position in result


@given(
    repetitions=st.integers(min_value=1, max_value=10),
    unit=st.text(alphabet="ab", min_size=1, max_size=3),
)
def test_self_overlapping_pattern_in_periodic_text(repetitions: int, unit: str) -> None:
    # Periodic texts such as "ababab..." stress the overlap handling
    # of the prefix function; occurrences may be denser, but every
    # period boundary must be reported.
    text = unit * repetitions
    result = find_occurrences(text, unit)
    for i in range(repetitions):
        assert i * len(unit) in result


@given(text=st.text(alphabet="ab"), pattern=st.text(alphabet="xyz", min_size=1))
def test_pattern_from_disjoint_alphabet_is_never_found(text: str, pattern: str) -> None:
    assert find_occurrences(text, pattern) == []


@given(text=st.text(), pattern=st.text(min_size=1))
def test_reported_indices_actually_match(text: str, pattern: str) -> None:
    for index in find_occurrences(text, pattern):
        assert text[index : index + len(pattern)] == pattern
