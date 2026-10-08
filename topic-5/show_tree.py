"""Show the token stream and the syntax tree of an arithmetic expression.

Run it from the repository root with one or more expressions:

    uv run python topic-5/show_tree.py "1 + 2 * 3" "(1 + 2) * 3"

or without arguments to see a built-in set of examples. For each
expression the script prints the tokens, the tree drawn top-down,
the tree as a Python value (what the tests compare), and the text
``render`` produces from the tree — the fewest parentheses that
preserve it. An invalid expression prints the parser's error.

With the ``--generate`` flag the script instead prints a sample of the
expressions the test generators produce for the full language, so you
can see what your parser will face.

Feel free to edit the examples below — this script is a playground,
not a test.
"""

import sys
from pathlib import Path

# Make the topic modules importable no matter where the script is run from.
sys.path.insert(0, str(Path(__file__).parent))

from expression_parser import parse, token_text, tokenize
from hypothesis import HealthCheck, given, settings
from syntax_tree import pretty, render
from tree_generators import GeneratedExpression, expressions

EXAMPLES = [
    "1 + 2 * 3",
    "(1 + 2) * 3",
    "1 + 2 + 3",
    "1 - 2 - 3",
    "-2 * 3",
    "-(2 * 3)",
    "1 + (2",
]

SAMPLES = 10


def show(text: str) -> None:
    print(f"\n=== {text!r} ===")
    try:
        tokens = tokenize(text)
        print("tokens: " + " ".join(f"{type(t).__name__}({token_text(t)})" for t in tokens))
        tree = parse(text)
    except ValueError as error:
        print(f"error:  {error}")
        return
    print(pretty(tree))
    print(f"value:  {tree!r}")
    print(f"render: {render(tree)}")


def show_generated() -> None:
    samples: list[str] = []

    # Abuse @given as a sampler: run the strategy many times and keep
    # the first few distinct rendered expressions.
    @settings(max_examples=200, database=None, suppress_health_check=list(HealthCheck))
    @given(expr=expressions(("+", "-", "*", "/"), ("-",)))
    def collect(expr: GeneratedExpression) -> None:
        if len(samples) < SAMPLES and expr.text not in samples and " " in expr.text:
            samples.append(expr.text)

    collect()
    print("=== generated expressions over the full language ===")
    for text in samples:
        print(f"  {text}")


if __name__ == "__main__":
    arguments = sys.argv[1:]
    if arguments == ["--generate"]:
        show_generated()
    else:
        for example in arguments or EXAMPLES:
            show(example)
