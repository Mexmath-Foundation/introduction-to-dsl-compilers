"""Hypothesis data generators for Topic 5: Syntax trees.

The central strategy is ``expressions(...)``: it generates a random
syntax tree from the node classes in ``syntax_tree.py`` and renders it
to text with ``render``, returning both. The tree is the *expected*
result of parsing the text, so a test needs no oracle of its own: it
parses the text and compares the result with the tree it came from.

The caller controls which operators the tree may contain:

* ``binary_operators`` — the binary operators to draw from (a subset
  of the keys of ``BINARY_PRECEDENCE``);
* ``unary_operators`` — the prefix operators to draw from (a subset of
  ``UNARY_OPERATORS``); empty by default, so no unary nodes appear.

This is how the starter suite separates what is already implemented
from what is yours: a tree over ``("+", "*")`` must round-trip today,
a tree over the full operator set only once your parser is complete.

The generator knows nothing about the parser. ``render`` is the single
link between trees and text, and it places the fewest parentheses that
preserve the tree, so the generated text exercises precedence and
associativity rather than hiding them behind brackets.

Students are encouraged to add more generators here (and more tests
that use them): for instance texts with random whitespace, fully
parenthesized texts, or texts that are deliberately broken in one
known place.
"""

from collections.abc import Sequence
from typing import NamedTuple

from hypothesis import strategies as st
from syntax_tree import BINARY_PRECEDENCE, UNARY_OPERATORS, BinaryOp, Expr, Number, UnaryOp, render

# Cap on the number of leaves of a generated tree, to keep generated
# expressions short and readable.
MAX_LEAVES = 8

# Literals are kept small, so a failing example reads naturally.
MAX_LITERAL = 999


class GeneratedExpression(NamedTuple):
    """A rendered expression together with the tree it was rendered from."""

    text: str
    tree: Expr


def _check_operators(binary_operators: Sequence[str], unary_operators: Sequence[str]) -> None:
    # Fail fast on misuse: every operator must exist in the language.
    for op in binary_operators:
        if op not in BINARY_PRECEDENCE:
            raise ValueError(f"unknown binary operator {op!r}")
    for op in unary_operators:
        if op not in UNARY_OPERATORS:
            raise ValueError(f"unknown unary operator {op!r}")


def numbers() -> st.SearchStrategy[Number]:
    return st.builds(Number, st.integers(min_value=0, max_value=MAX_LITERAL))


def trees(
    binary_operators: Sequence[str] = ("+", "*"),
    unary_operators: Sequence[str] = (),
    max_leaves: int = MAX_LEAVES,
) -> st.SearchStrategy[Expr]:
    """A random syntax tree whose operators come from the given sets."""
    _check_operators(binary_operators, unary_operators)
    if not binary_operators and not unary_operators:
        return numbers()

    def extend(children: st.SearchStrategy[Expr]) -> st.SearchStrategy[Expr]:
        # One more level: an operator node whose operands are smaller trees.
        options: list[st.SearchStrategy[Expr]] = []
        if binary_operators:
            op = st.sampled_from(list(binary_operators))
            options.append(st.builds(BinaryOp, op, children, children))
        if unary_operators:
            op = st.sampled_from(list(unary_operators))
            options.append(st.builds(UnaryOp, op, children))
        return st.one_of(options)

    return st.recursive(numbers(), extend, max_leaves=max_leaves)


@st.composite
def expressions(
    draw: st.DrawFn,
    binary_operators: Sequence[str] = ("+", "*"),
    unary_operators: Sequence[str] = (),
    max_leaves: int = MAX_LEAVES,
) -> GeneratedExpression:
    tree = draw(trees(binary_operators, unary_operators, max_leaves))
    return GeneratedExpression(text=render(tree), tree=tree)
