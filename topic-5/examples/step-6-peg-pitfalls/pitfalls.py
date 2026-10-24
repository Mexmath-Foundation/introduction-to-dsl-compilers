#!/usr/bin/env python3
"""PEG pitfalls in textX, reproduced on purpose.

Each block builds a deliberately broken grammar, shows the error textX
raises, then shows the fix. Run: uv run python pitfalls.py
"""

from textx import metamodel_from_str
from textx.exceptions import TextXSyntaxError


def show(title, grammar, text):
    print(f"\n--- {title}")
    print("grammar:", grammar.strip())
    print("input:  ", repr(text))
    try:
        mm = metamodel_from_str(grammar)
        m = mm.model_from_str(text)
        print("OK ->", m)
    except TextXSyntaxError as e:
        print("TextXSyntaxError:", e)
    except RecursionError:
        print("RecursionError (left recursion)")


def main():
    # 1. Ordered choice: a prefix alternative listed first shadows the longer one.
    show("1a. ordered choice, broken", "Model: ops+=Op; Op: '<' | '<=' ;", "<=")
    show(
        "1b. ordered choice, fixed (longer alternative first)",
        "Model: ops+=Op; Op: '<=' | '<' ;",
        "<=",
    )

    # 2. Keywords are not reserved: ID happily matches 'end'.
    show(
        "2a. keyword eaten by ID, broken",
        "Block: 'begin' items*=Item 'end'; Item: name=ID;",
        "begin a b end",
    )
    show(
        "2b. keyword excluded with a negative lookahead, fixed",
        "Block: 'begin' items*=Item 'end'; Item: name=MyID; "
        "MyID: !Keyword ID; Keyword: 'begin' | 'end';",
        "begin a b end",
    )

    # 3. Greedy repetition never gives an element back.
    show("3. greedy repetition, broken", "Model: a+=ID 'last' ;", "x y last")

    # 4. Left recursion: metamodel builds, parsing recurses forever.
    show("4a. left recursion, broken", "Expr: Expr '+' INT | INT ;", "1 + 2")
    show(
        "4b. precedence climbing, fixed",
        """
    Expr:   terms+=Term['+'] ;
    Term:   factors+=Factor['*'] ;
    Factor: INT | '(' Expr ')' ;
    """,
        "1 + 2 * (3 + 4)",
    )


if __name__ == "__main__":
    main()
