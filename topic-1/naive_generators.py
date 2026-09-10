"""Hypothesis data generators for Topic 1: Naive substring search.

Each generator is a Hypothesis *composite strategy*: it draws random
building blocks and assembles them into a search input whose key
property — where the pattern occurs, or that it cannot occur at all —
is known *by construction*. The tests then only need to assert that
property; they never build test data themselves.

Students are encouraged to add more generators here (and more tests
that use them).
"""

from typing import NamedTuple

from hypothesis import strategies as st


class SearchInput(NamedTuple):
    """A plain (text, pattern) pair with no guarantees about occurrences."""

    text: str
    pattern: str


class TextWithPatternInsertedOnce(NamedTuple):
    """A text built around a pattern placed at a known position.

    The pattern may incidentally occur elsewhere in the text as well,
    but it is guaranteed to occur at ``position``.
    """

    text: str
    pattern: str
    position: int


class TextWithPatternInsertedManyTimes(NamedTuple):
    """A text with the pattern deliberately inserted at several known positions.

    ``positions`` lists only the deliberate insertions; incidental
    occurrences (e.g. created by overlaps at the seams) may exist too.
    """

    text: str
    pattern: str
    positions: list[int]


@st.composite
def texts_with_pattern_inserted_once(draw: st.DrawFn) -> TextWithPatternInsertedOnce:
    # Build the text as prefix + pattern + suffix, so the pattern is
    # guaranteed to start exactly at index len(prefix).
    prefix = draw(st.text())
    pattern = draw(st.text(min_size=1))
    suffix = draw(st.text())
    return TextWithPatternInsertedOnce(
        text=prefix + pattern + suffix,
        pattern=pattern,
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
def texts_with_absent_pattern(draw: st.DrawFn) -> SearchInput:
    # The text and the pattern are drawn from disjoint alphabets
    # ("ab" vs "xyz"), so the pattern cannot occur in the text.
    text = draw(st.text(alphabet="ab"))
    pattern = draw(st.text(alphabet="xyz", min_size=1))
    return SearchInput(text=text, pattern=pattern)


@st.composite
def arbitrary_search_inputs(draw: st.DrawFn) -> SearchInput:
    # Fully unconstrained inputs: nothing is known about occurrences,
    # so tests using this generator may only assert properties that
    # hold for *any* input (soundness, ordering, uniqueness, ...).
    text = draw(st.text())
    pattern = draw(st.text(min_size=1))
    return SearchInput(text=text, pattern=pattern)
