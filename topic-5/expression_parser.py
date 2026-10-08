"""Topic 5: Syntax trees for arithmetic expressions — the parser.

Turn the text of an arithmetic expression into a syntax tree built
from the node classes in ``syntax_tree.py``. See topic-5/README.md for
the task description and acceptance criteria.

The module has two stages:

1. ``tokenize`` — the *lexer*: cuts the text into tokens (numbers,
   operators, parentheses) and rejects any other character. It is
   complete; it already knows every symbol of the language.
2. ``parse`` — the *parser*: a recursive-descent parser that reads
   the token list according to the grammar below and builds the tree.
   It currently handles ``+``, ``*``, numbers and parentheses. Your
   task is to extend it with ``-``, ``/`` and unary minus.

The grammar, one function per rule:

    expression := term   (("+" | "-") term)*
    term       := factor (("*" | "/") factor)*
    factor     := "-" factor | primary
    primary    := NUMBER | "(" expression ")"

Each rule function receives the list of tokens still to be read and
returns the tree it built together with the tokens it did not consume.
It looks at the tokens with structural pattern matching: a pattern
such as ``[OperatorToken("+" as op), *rest]`` matches a list that
starts with a ``+`` token and binds ``rest`` to everything after it.
An empty list means the end of the input.

Each rule produces the operators of one precedence level: the deeper
the rule, the tighter its operators bind. The ``(... op ...)*`` loops
fold the operands from left to right, which is exactly what makes the
binary operators left-associative.
"""

from dataclasses import dataclass

from syntax_tree import BinaryOp, Expr, Number, UnaryOp  # noqa: F401  (UnaryOp is for you)

# --- Tokens -----------------------------------------------------------------


@dataclass(frozen=True)
class NumberToken:
    """An integer literal."""

    value: int
    position: int


@dataclass(frozen=True)
class OperatorToken:
    """One of the operator symbols ``+ - * /``."""

    symbol: str
    position: int


@dataclass(frozen=True)
class LeftParenthesis:
    position: int


@dataclass(frozen=True)
class RightParenthesis:
    position: int


type Token = NumberToken | OperatorToken | LeftParenthesis | RightParenthesis
type Tokens = list[Token]


def token_text(token: Token) -> str:
    """The lexeme a token was read from."""
    match token:
        case NumberToken(value):
            return str(value)
        case OperatorToken(symbol):
            return symbol
        case LeftParenthesis():
            return "("
        case RightParenthesis():
            return ")"
    raise TypeError(f"not a token: {token!r}")


def describe(tokens: Tokens) -> str:
    """Describe what comes next in ``tokens``, for error messages."""
    match tokens:
        case []:
            return "end of input"
        case [token, *_]:
            return f"{token_text(token)!r} at position {token.position}"
    raise TypeError(f"not a token list: {tokens!r}")


def tokenize(text: str) -> Tokens:
    """Split ``text`` into tokens.

    Whitespace between tokens is skipped; a number is a maximal run of
    decimal digits. Any other character raises ``ValueError``.

    Example:
        tokenize("12 + 3")
            -> [NumberToken(12, 0), OperatorToken("+", 3), NumberToken(3, 5)]
    """
    tokens: Tokens = []
    index = 0
    while index < len(text):
        match text[index]:
            case char if char.isspace():
                index += 1
            case char if char.isdigit():
                start = index
                while index < len(text) and text[index].isdigit():
                    index += 1
                tokens.append(NumberToken(int(text[start:index]), start))
            case "+" | "-" | "*" | "/" as symbol:
                tokens.append(OperatorToken(symbol, index))
                index += 1
            case "(":
                tokens.append(LeftParenthesis(index))
                index += 1
            case ")":
                tokens.append(RightParenthesis(index))
                index += 1
            case char:
                raise ValueError(f"unexpected character {char!r} at position {index}")
    return tokens


# --- Grammar rules ----------------------------------------------------------


def _expression(tokens: Tokens) -> tuple[Expr, Tokens]:
    # expression := term (("+" | "-") term)*
    #
    # Implemented for "+"; TODO: extend it to "-". Both operators live
    # on the same precedence level, so they belong to the same loop —
    # the pattern below only needs to accept one more symbol.
    left, rest = _term(tokens)
    while True:
        match rest:
            case [OperatorToken("+" as op), *rest]:
                right, rest = _term(rest)
                # Fold to the left: the tree built so far becomes the
                # left operand of the next operator. This is what makes
                # "1 + 2 + 3" parse as (1 + 2) + 3.
                left = BinaryOp(op, left, right)
            case _:
                return left, rest


def _term(tokens: Tokens) -> tuple[Expr, Tokens]:
    # term := factor (("*" | "/") factor)*
    #
    # Implemented for "*"; TODO: extend it to "/".
    left, rest = _factor(tokens)
    while True:
        match rest:
            case [OperatorToken("*" as op), *rest]:
                right, rest = _factor(rest)
                left = BinaryOp(op, left, right)
            case _:
                return left, rest


def _factor(tokens: Tokens) -> tuple[Expr, Tokens]:
    # factor := "-" factor | primary
    #
    # TODO: implement unary minus. The rule is recursive on purpose:
    # "--1" is minus applied to minus applied to 1. Note that the
    # result is a UnaryOp node, never a negative Number.
    return _primary(tokens)


def _primary(tokens: Tokens) -> tuple[Expr, Tokens]:
    # primary := NUMBER | "(" expression ")"
    match tokens:
        case [NumberToken(value), *rest]:
            return Number(value), rest
        case [LeftParenthesis(), *rest]:
            inner, rest = _expression(rest)
            match rest:
                case [RightParenthesis(), *rest]:
                    return inner, rest
                case _:
                    raise ValueError(f"expected ')', found {describe(rest)}")
        case _:
            raise ValueError(f"expected a number or '(', found {describe(tokens)}")


def parse(text: str) -> Expr:
    """Parse ``text`` into a syntax tree.

    The text must be exactly one expression of the language: numbers,
    the binary operators ``+ - * /``, unary minus and parentheses,
    with any amount of whitespace between tokens. Precedence and
    associativity follow the tables in ``syntax_tree.py``. Anything
    else — an empty input, an unknown character, a missing operand,
    an unbalanced parenthesis, trailing tokens — raises ``ValueError``.

    Example:
        parse("1 + 2 * 3")
            -> BinaryOp("+", Number(1), BinaryOp("*", Number(2), Number(3)))
        parse("(1 + 2) * 3")
            -> BinaryOp("*", BinaryOp("+", Number(1), Number(2)), Number(3))
        parse("-2 * 3")
            -> BinaryOp("*", UnaryOp("-", Number(2)), Number(3))
    """
    tree, rest = _expression(tokenize(text))
    # The whole input must be one expression: nothing may follow it.
    if rest:
        raise ValueError(f"expected end of input, found {describe(rest)}")
    return tree
