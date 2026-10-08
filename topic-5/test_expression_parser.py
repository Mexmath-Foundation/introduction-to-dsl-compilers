"""Starter test suite for Topic 5: Syntax trees.

Property-based tests written with Hypothesis. All generated data comes
from the composite strategies in ``tree_generators.py``: a generated
expression carries both its text and the tree the text was rendered
from, and the tests only assert that parsing the text gives that tree
back — the generator guarantees the expectation by construction.

The suite is split in two halves. The first half exercises what the
template already implements (``+``, ``*``, numbers, parentheses) and
must pass as is. The second half exercises ``-``, ``/`` and unary
minus and fails until you implement them.

This suite is intentionally incomplete. It covers only a few obvious
properties; you are expected to extend it (and the generators) — see
topic-5/README.md.
"""

import pytest
from expression_parser import NumberToken, OperatorToken, parse, tokenize
from hypothesis import given
from syntax_tree import BinaryOp, Number, UnaryOp
from tree_generators import expressions

ALL_BINARY = ("+", "-", "*", "/")
UNARY_MINUS = ("-",)


# --- The given part: + and * ------------------------------------------------


# The lexer: whitespace is skipped, a number is a maximal digit run,
# positions point into the original text.
def test_tokenize_example() -> None:
    assert tokenize(" 12+ 3 ") == [
        NumberToken(12, 1),
        OperatorToken("+", 3),
        NumberToken(3, 5),
    ]


# Round trip: a tree rendered to text and parsed back must come back
# unchanged. Over "+" and "*" this holds already.
@given(expr=expressions(("+", "*")))
def test_plus_and_times_round_trip(expr) -> None:
    assert parse(expr.text) == expr.tree


# A few fixed shapes, so a failure is readable: precedence ("*" binds
# tighter than "+"), parentheses, and left-associativity.
@pytest.mark.parametrize(
    ("text", "tree"),
    [
        ("7", Number(7)),
        ("((7))", Number(7)),
        ("1 + 2 * 3", BinaryOp("+", Number(1), BinaryOp("*", Number(2), Number(3)))),
        ("(1 + 2) * 3", BinaryOp("*", BinaryOp("+", Number(1), Number(2)), Number(3))),
        ("1 + 2 + 3", BinaryOp("+", BinaryOp("+", Number(1), Number(2)), Number(3))),
        ("1 + (2 + 3)", BinaryOp("+", Number(1), BinaryOp("+", Number(2), Number(3)))),
        ("  1+2*  3", BinaryOp("+", Number(1), BinaryOp("*", Number(2), Number(3)))),
    ],
)
def test_plus_and_times_examples(text: str, tree) -> None:
    assert parse(text) == tree


# --- Your part: -, / and unary minus ----------------------------------------


# Round trip over the complete language.
@given(expr=expressions(ALL_BINARY, UNARY_MINUS))
def test_full_language_round_trip(expr) -> None:
    assert parse(expr.text) == expr.tree


# Round trip over each new feature in isolation, so a failure points at
# the feature that is still missing.
@given(expr=expressions(("+", "-")))
def test_minus_round_trip(expr) -> None:
    assert parse(expr.text) == expr.tree


@given(expr=expressions(("*", "/")))
def test_divide_round_trip(expr) -> None:
    assert parse(expr.text) == expr.tree


@given(expr=expressions(("+", "*"), UNARY_MINUS))
def test_unary_minus_round_trip(expr) -> None:
    assert parse(expr.text) == expr.tree


# Fixed shapes for the new operators: left-associativity of "-" and
# "/", and how tightly unary minus binds.
@pytest.mark.parametrize(
    ("text", "tree"),
    [
        ("1 - 2 - 3", BinaryOp("-", BinaryOp("-", Number(1), Number(2)), Number(3))),
        ("8 / 4 / 2", BinaryOp("/", BinaryOp("/", Number(8), Number(4)), Number(2))),
        ("1 - 2 * 3", BinaryOp("-", Number(1), BinaryOp("*", Number(2), Number(3)))),
        ("-5", UnaryOp("-", Number(5))),
        ("-1 + 2", BinaryOp("+", UnaryOp("-", Number(1)), Number(2))),
        ("-(1 + 2)", UnaryOp("-", BinaryOp("+", Number(1), Number(2)))),
        ("-2 * 3", BinaryOp("*", UnaryOp("-", Number(2)), Number(3))),
        ("2 * -3", BinaryOp("*", Number(2), UnaryOp("-", Number(3)))),
        ("1 - -2", BinaryOp("-", Number(1), UnaryOp("-", Number(2)))),
        ("--1", UnaryOp("-", UnaryOp("-", Number(1)))),
    ],
)
def test_new_operator_examples(text: str, tree) -> None:
    assert parse(text) == tree


# --- Errors -----------------------------------------------------------------


# Malformed input raises ValueError instead of returning any tree. A
# few obvious shapes; covering the rest of the error space is part of
# the assignment.
@pytest.mark.parametrize(
    "bad_text",
    [
        "",  # nothing to parse
        "1 +",  # missing right operand
        "+ 1",  # "+" has no prefix form
        "* 1",  # neither has "*"
        "(1 + 2",  # unbalanced parentheses
        "1 + 2)",  # trailing token
        "1 2",  # two operands without an operator
        "()",  # empty parentheses
        "1 * * 2",  # doubled binary operator
        "a + 1",  # unknown character
        "1.5 + 2",  # only integer literals exist
    ],
)
def test_invalid_expression_raises_value_error(bad_text: str) -> None:
    with pytest.raises(ValueError):
        parse(bad_text)
