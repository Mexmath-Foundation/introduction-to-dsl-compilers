"""Topic 5: Syntax trees for arithmetic expressions — the tree itself.

This module defines the *abstract syntax tree* (AST) of the expression
language: the node classes a parser produces, the operator tables that
fix precedence and associativity, and two helpers that walk a finished
tree — ``render`` turns it back into text, ``pretty`` draws it for
humans.

The node classes and the operator tables are part of the task
specification: the tests compare trees structurally, so do not change
them. Build your parser on top of them.
"""

from dataclasses import dataclass

# Binary operators and their precedence: the higher the number, the
# tighter the operator binds. "+" and "-" share one level, "*" and "/"
# share a higher one. All binary operators are left-associative:
# "1 - 2 - 3" is (1 - 2) - 3, never 1 - (2 - 3).
BINARY_PRECEDENCE: dict[str, int] = {"+": 1, "-": 1, "*": 2, "/": 2}

# Prefix (unary) operators. Unary minus binds tighter than every binary
# operator: "-2 * 3" is (-2) * 3, while -(2 * 3) needs the parentheses.
UNARY_OPERATORS = frozenset({"-"})
UNARY_PRECEDENCE = 3

# A tree is one of three node kinds. The alias is evaluated lazily, so
# it may be declared before the classes it refers to.
type Expr = Number | BinaryOp | UnaryOp


@dataclass(frozen=True)
class Number:
    """A non-negative integer literal — a leaf of the tree.

    The language has no negative literals: ``-5`` is a ``UnaryOp``
    applied to ``Number(5)``, not ``Number(-5)``.
    """

    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"negative literal {self.value}: use UnaryOp('-', Number(...))")


@dataclass(frozen=True)
class BinaryOp:
    """An application of a binary operator: ``left op right``."""

    op: str
    left: Expr
    right: Expr

    def __post_init__(self) -> None:
        if self.op not in BINARY_PRECEDENCE:
            raise ValueError(f"unknown binary operator {self.op!r}")


@dataclass(frozen=True)
class UnaryOp:
    """An application of a prefix operator: ``op operand``."""

    op: str
    operand: Expr

    def __post_init__(self) -> None:
        if self.op not in UNARY_OPERATORS:
            raise ValueError(f"unknown unary operator {self.op!r}")


def precedence(tree: Expr) -> int:
    """How tightly the root of ``tree`` binds; leaves bind tightest of all."""
    match tree:
        case BinaryOp(op=op):
            return BINARY_PRECEDENCE[op]
        case UnaryOp():
            return UNARY_PRECEDENCE
        case Number():
            return UNARY_PRECEDENCE + 1
    raise TypeError(f"not a tree node: {tree!r}")


def render(tree: Expr) -> str:
    """Turn a tree back into text, using the fewest parentheses that preserve it.

    A child is wrapped in parentheses only when leaving them out would
    change the tree: when it binds looser than its parent, or — for the
    right operand of a binary operator — when it binds equally tight,
    because the operators are left-associative. Hence ``render`` is a
    right inverse of a correct parser: ``parse(render(tree)) == tree``.

    Example:
        render(BinaryOp("*", BinaryOp("+", Number(1), Number(2)), Number(3)))
            -> "(1 + 2) * 3"
        render(BinaryOp("+", Number(1), BinaryOp("*", Number(2), Number(3))))
            -> "1 + 2 * 3"
    """
    match tree:
        case Number(value=value):
            return str(value)
        case UnaryOp(op=op, operand=operand):
            text = render(operand)
            if precedence(operand) < UNARY_PRECEDENCE:
                text = f"({text})"
            return f"{op}{text}"
        case BinaryOp(op=op, left=left, right=right):
            level = BINARY_PRECEDENCE[op]
            left_text = render(left)
            if precedence(left) < level:
                left_text = f"({left_text})"
            right_text = render(right)
            if precedence(right) <= level:
                right_text = f"({right_text})"
            return f"{left_text} {op} {right_text}"
    raise TypeError(f"not a tree node: {tree!r}")


def pretty(tree: Expr) -> str:
    """Draw the tree top-down, one node per line, for printing.

    Example:
        pretty(BinaryOp("+", Number(1), BinaryOp("*", Number(2), Number(3))))

        BinaryOp +
        ├── Number 1
        └── BinaryOp *
            ├── Number 2
            └── Number 3
    """
    lines: list[str] = []

    def label(node: Expr) -> str:
        match node:
            case Number(value=value):
                return f"Number {value}"
            case BinaryOp(op=op) | UnaryOp(op=op):
                return f"{type(node).__name__} {op}"
        raise TypeError(f"not a tree node: {node!r}")

    def children(node: Expr) -> list[Expr]:
        match node:
            case BinaryOp(left=left, right=right):
                return [left, right]
            case UnaryOp(operand=operand):
                return [operand]
        return []

    def walk(node: Expr, prefix: str, branch: str, continuation: str) -> None:
        lines.append(f"{prefix}{branch}{label(node)}")
        kids = children(node)
        for index, child in enumerate(kids):
            last = index == len(kids) - 1
            walk(
                child,
                prefix + continuation,
                "└── " if last else "├── ",
                "    " if last else "│   ",
            )

    walk(tree, "", "", "")
    return "\n".join(lines)
