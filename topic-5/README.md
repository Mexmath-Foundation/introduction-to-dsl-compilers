# Topic 5: Syntax Trees for Arithmetic Expressions

## TL;DR
A compiler never works on text. The first thing it does is turn the text into a *syntax
tree* — a structure that makes the meaning of the program explicit — and every later
phase (checking, optimizing, generating code, evaluating) walks that tree. In this topic
you complete a parser that builds syntax trees for arithmetic expressions.

The template already parses `+`, `*`, integer literals and parentheses. You extend it to
the full language: binary `-`, binary `/` and unary `-`. Run
```shell
uv run python topic-5/show_tree.py "1 + 2 * 3" "(1 + 2) * 3"
```
to see the tokens and the tree of any expression.

## The language
An expression is built from non-negative integer literals (`0`, `42`, `007`), the binary
operators `+ - * /`, unary minus, and parentheses. Whitespace between tokens is ignored.

### Precedence and associativity
| Level | Operators | Associativity | Example |
|-------|-----------|---------------|---------|
| 1 (loosest) | binary `+`, `-` | left | `1 - 2 - 3` is `(1 - 2) - 3` |
| 2 | binary `*`, `/` | left | `8 / 4 / 2` is `(8 / 4) / 2` |
| 3 (tightest) | unary `-` | prefix | `-2 * 3` is `(-2) * 3` |

Unary minus binds tighter than any binary operator, so `-(2 * 3)` needs its parentheses.
Unary minus may be stacked (`--1`) and may follow a binary operator (`1 - -2`, `2 * -3`).
The tables are the single source of truth; they live in
[`syntax_tree.py`](syntax_tree.py) as `BINARY_PRECEDENCE` and `UNARY_PRECEDENCE`.

### Grammar
The parser is a *recursive-descent* parser: one function per grammar rule, and each rule
owns the operators of one precedence level — the deeper the rule, the tighter its
operators bind.
```
expression := term   (("+" | "-") term)*
term       := factor (("*" | "/") factor)*
factor     := "-" factor | primary
primary    := NUMBER | "(" expression ")"
```
The `(... op ...)*` loops consume operands from left to right and fold each one into the
tree built so far: that is what makes the binary operators left-associative.

## The syntax tree
The tree is made of three node kinds, defined as frozen dataclasses in
[`syntax_tree.py`](syntax_tree.py):

* `Number(value)` — an integer literal, always a leaf;
* `BinaryOp(op, left, right)` — a binary operator applied to two subtrees;
* `UnaryOp(op, operand)` — a prefix operator applied to one subtree.

Two expressions with the same tree mean the same thing, however they were written:
`1+2*3`, `1 + (2 * 3)` and `((1) + ((2) * (3)))` all produce the tree below. Conversely,
the tree is where precedence becomes visible: there are no parentheses in a tree.
```
$ uv run python topic-5/show_tree.py "1 + 2 * 3" "(1 + 2) * 3"

=== '1 + 2 * 3' ===
BinaryOp +
├── Number 1
└── BinaryOp *
    ├── Number 2
    └── Number 3

=== '(1 + 2) * 3' ===
BinaryOp *
├── BinaryOp +
│   ├── Number 1
│   └── Number 2
└── Number 3
```
Two things to notice:
* **Negative numbers do not exist in the language.** `-5` is `UnaryOp("-", Number(5))`,
  never `Number(-5)`; the `Number` class refuses negative values.
* **Associativity is a tree shape.** `1 + 2 + 3` is `BinaryOp("+", BinaryOp("+", 1, 2), 3)`
  and `1 + (2 + 3)` is a different tree, even though both evaluate to 6.

### Examples
| Expression | Tree |
|------------|------|
| `7` | `Number(7)` |
| `1 + 2 * 3` | `BinaryOp("+", Number(1), BinaryOp("*", Number(2), Number(3)))` |
| `(1 + 2) * 3` | `BinaryOp("*", BinaryOp("+", Number(1), Number(2)), Number(3))` |
| `1 - 2 - 3` | `BinaryOp("-", BinaryOp("-", Number(1), Number(2)), Number(3))` |
| `-1 + 2` | `BinaryOp("+", UnaryOp("-", Number(1)), Number(2))` |
| `-(1 + 2)` | `UnaryOp("-", BinaryOp("+", Number(1), Number(2)))` |
| `2 * -3` | `BinaryOp("*", Number(2), UnaryOp("-", Number(3)))` |
| `--1` | `UnaryOp("-", UnaryOp("-", Number(1)))` |
| `1 +` | `ValueError` — missing right operand |
| `(1 + 2` | `ValueError` — unbalanced parentheses |
| `1 2` | `ValueError` — two operands without an operator |
| `1.5` | `ValueError` — only integer literals exist |

## What is given and what you implement
[`expression_parser.py`](expression_parser.py) has two stages:

1. **`tokenize`** — the lexer. It is complete: it already knows every symbol of the
   language, including `-` and `/`, and rejects any other character with `ValueError`.
2. **`parse`** — the parser. The rule functions implement the grammar above with
   `+` and `*` only; the places to extend are marked with `TODO`:
   * `_expression` — add binary `-` next to `+`;
   * `_term` — add binary `/` next to `*`;
   * `_factor` — add unary `-` (the rule is recursive: `--1` must work).

Tokens are small frozen dataclasses (`NumberToken`, `OperatorToken`, `LeftParenthesis`,
`RightParenthesis`), and every rule function takes the list of tokens still to be read and
returns the tree it built together with the tokens it did not consume. The rules inspect
the list with *structural pattern matching*:
```python
match rest:
    case [OperatorToken("+" as op), *rest]:  # starts with "+": bind the rest
        ...
    case _:  # anything else, including []
        ...
```
An empty list is the end of the input, so there is no special end token. Read the
implemented rules first. Adding `-` and `/` is a matter of accepting one more symbol in a
pattern once you see how `+` and `*` are folded; unary minus is the one place where you
build a `UnaryOp` node, and the one place where you must decide what the operand of the
minus is (hint: the grammar says).

Any malformed input must raise `ValueError`: empty input, a missing operand, an
unbalanced parenthesis, a token left over after the expression, an unknown character.
Syntax errors are a separate channel from trees — garbage must never come back as a
tree.

## Helpers you can lean on
[`syntax_tree.py`](syntax_tree.py) also contains two tree walkers, both fully implemented:
* `render(tree)` turns a tree back into text, placing the **fewest** parentheses that
  preserve the tree. For a correct parser `parse(render(tree)) == tree` for every tree —
  this is the property the test generators are built on.
* `pretty(tree)` draws the tree as in the listing above.

Walking a tree with `match` statements, as these helpers do, is the pattern every later
compiler phase follows; it is worth reading them. The tokenizer and the rule functions
use `match` in the same way, on characters and on token lists.

## Previewing generated expressions
Run
```shell
uv run python topic-5/show_tree.py --generate
```
to print a sample of the expressions the test generators produce for the full language —
the kind of input your finished parser will face. Edit the examples at the top of the
script while developing; it is a playground, not a test.

## Testing
You are required to **extend the test suite** in
[`test_expression_parser.py`](test_expression_parser.py). The provided tests are
**intentionally incomplete**: they cover only a few obvious properties. Passing them does
**not** mean your solution is correct or complete.

The suite is in two halves. The first half exercises the given part (`+`, `*`, numbers,
parentheses) and passes as is; the second half exercises `-`, `/` and unary minus and
fails until you implement them.

Test data generation is kept separate from the tests: all inputs are produced by the
composite strategies in [`tree_generators.py`](tree_generators.py). The central strategy,
`expressions(binary_operators, unary_operators)`, generates a random tree over the given
operators and renders it to text, returning both — the tree is the expected result of
parsing the text, so the test only asserts `parse(text) == tree`. Follow the same
structure in your own tests: generate data in the generators module, not inside the test
functions.

Ideas for generators and properties the starter suite does not cover:
* texts with random whitespace inserted between tokens — the tree must not change;
* fully parenthesized texts — redundant parentheses must not change the tree either;
* `render(parse(text)) == text` for generated texts;
* texts broken in one known place (a dropped `)`, a doubled operator, a trailing token)
  — every one of them must raise `ValueError`.

## Useful links
* [Abstract syntax tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) — the
  concept in general.
* [Recursive descent parser](https://en.wikipedia.org/wiki/Recursive_descent_parser) —
  the parsing technique used by the template.
* [Crafting Interpreters, "Parsing Expressions"](https://craftinginterpreters.com/parsing-expressions.html)
  — a gentle, thorough walkthrough of exactly this kind of parser (in Java, but the
  structure is identical).
* [Python `match` statement](https://docs.python.org/3/tutorial/controlflow.html#match-statements)
  — structural pattern matching, used by the tree walkers in `syntax_tree.py`.
* [Hypothesis documentation](https://hypothesis.readthedocs.io/) — the property-based
  testing framework used by the test suite; see
  [`st.recursive`](https://hypothesis.readthedocs.io/en/latest/reference/strategies.html#hypothesis.strategies.recursive)
  for how the tree generator is built.

## Acceptance criteria
1. `parse` in [`expression_parser.py`](expression_parser.py) handles the full language:
   `+`, `-`, `*`, `/`, unary `-`, integer literals and parentheses, with the precedence
   and associativity above, and raises `ValueError` for malformed input.
2. The node classes and operator tables in [`syntax_tree.py`](syntax_tree.py) are used
   as given: the tests compare trees structurally.
3. All tests pass: `uv run pytest topic-5`.
4. The starter test suite is extended with your own tests:
   * example-based tests for edge cases;
   * further Hypothesis property-based tests covering properties the starter suite does not.
5. Code is readable, typed, and documented where behavior is not obvious.
6. The solution is submitted as a pull request from the `topic-5` branch (see the root
   [README](../README.md)).

## Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) for this task is forbidden.**
  Both the implementation and the tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult textbooks, lecture materials, and the documentation linked
  above to understand syntax trees and recursive-descent parsing.
