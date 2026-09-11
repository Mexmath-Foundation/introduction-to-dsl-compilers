"""Hypothesis data generators for Topic 2: Knuth–Morris–Pratt substring search.

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


class PeriodicText(NamedTuple):
    """A text that is a unit repeated several times (e.g. "ababab").

    The unit is guaranteed to occur at every period boundary
    (0, len(unit), 2 * len(unit), ...); denser occurrences are possible
    when the unit overlaps itself (e.g. unit "aa").
    """

    text: str
    unit: str
    repetitions: int


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

    return TextWithPatternInsertedManyTimes(text=text, pattern=pattern, positions=positions)


@st.composite
def periodic_texts(draw: st.DrawFn) -> PeriodicText:
    # Repeat a short unit over a tiny alphabet to produce highly
    # repetitive texts such as "ababab" or "aaaaaa". These are the
    # inputs that stress the prefix-function (overlap) handling that
    # distinguishes KMP from shortcut implementations.
    unit = draw(st.text(alphabet="ab", min_size=1, max_size=3))
    repetitions = draw(st.integers(min_value=1, max_value=10))
    return PeriodicText(text=unit * repetitions, unit=unit, repetitions=repetitions)


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
