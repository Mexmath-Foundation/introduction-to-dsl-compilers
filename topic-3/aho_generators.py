"""Hypothesis data generators for Topic 3: Aho–Corasick multi-pattern search.

Each generator is a Hypothesis *composite strategy*: it draws random
building blocks and assembles them into a search input whose key
property — where a pattern occurs, or that no pattern can occur at
all — is known *by construction*. The tests then only need to assert
that property; they never build test data themselves.

Students are encouraged to add more generators here (and more tests
that use them).
"""

from typing import NamedTuple

from hypothesis import strategies as st


class MultiPatternSearchInput(NamedTuple):
    """A plain (text, patterns) pair with no guarantees about occurrences."""

    text: str
    patterns: list[str]


class TextWithPatternInsertedOnce(NamedTuple):
    """A text built around one tracked pattern placed at a known position.

    ``patterns`` is the full pattern set to search for; it contains
    ``inserted_pattern`` plus unrelated patterns. The tracked pattern
    may incidentally occur elsewhere in the text as well, but it is
    guaranteed to occur at ``position``.
    """

    text: str
    patterns: list[str]
    inserted_pattern: str
    position: int


class TextWithPatternInsertedManyTimes(NamedTuple):
    """A text with one pattern deliberately inserted at several known positions.

    ``positions`` lists only the deliberate insertions; incidental
    occurrences (e.g. created by overlaps at the seams) may exist too.
    """

    text: str
    pattern: str
    positions: list[int]


@st.composite
def texts_with_pattern_inserted_once(draw: st.DrawFn) -> TextWithPatternInsertedOnce:
    # Build the text as prefix + pattern + suffix, so the tracked
    # pattern is guaranteed to start exactly at index len(prefix).
    # Extra patterns are added to the search set to make sure the
    # automaton handles several patterns at once.
    prefix = draw(st.text())
    pattern = draw(st.text(min_size=1))
    suffix = draw(st.text())
    other_patterns = draw(st.lists(st.text(min_size=1), max_size=4))
    return TextWithPatternInsertedOnce(
        text=prefix + pattern + suffix,
        patterns=[pattern, *other_patterns],
        inserted_pattern=pattern,
        position=len(prefix),
    )


@st.composite
def texts_with_pattern_inserted_many_times(
    draw: st.DrawFn,
) -> TextWithPatternInsertedManyTimes:
    # Join 2..6 random fragments with the pattern as the separator:
    # text = part_0 + pattern + part_1 + pattern + ... + part_n.
    # Every separator position is computed and recorded, so the test
    # knows exactly where the pattern was placed.
    pattern = draw(st.text(min_size=1))
    parts = draw(st.lists(st.text(), min_size=2, max_size=6))
    text = pattern.join(parts)

    positions = []
    position = 0
    for part in parts[:-1]:
        position += len(part)
        positions.append(position)
        position += len(pattern)

    return TextWithPatternInsertedManyTimes(
        text=text, pattern=pattern, positions=positions
    )


@st.composite
def texts_with_absent_patterns(draw: st.DrawFn) -> MultiPatternSearchInput:
    # The text and all patterns are drawn from disjoint alphabets
    # ("ab" vs "xyz"), so no pattern can occur in the text.
    text = draw(st.text(alphabet="ab"))
    patterns = draw(st.lists(st.text(alphabet="xyz", min_size=1), min_size=1, max_size=5))
    return MultiPatternSearchInput(text=text, patterns=patterns)


@st.composite
def arbitrary_search_inputs(draw: st.DrawFn) -> MultiPatternSearchInput:
    # Fully unconstrained inputs: nothing is known about occurrences,
    # so tests using this generator may only assert properties that
    # hold for *any* input (soundness, result keys, ordering, ...).
    text = draw(st.text())
    patterns = draw(st.lists(st.text(min_size=1), min_size=1, max_size=5))
    return MultiPatternSearchInput(text=text, patterns=patterns)
