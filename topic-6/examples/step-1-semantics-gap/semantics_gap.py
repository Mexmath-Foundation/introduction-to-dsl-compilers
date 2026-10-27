#!/usr/bin/env python3
"""Step 1: what the grammar cannot check.

Every description below is accepted or rejected by the traffic-light
grammar of Topic 5 (``fsm.tx`` next to this file is a copy of
``topic-5/examples/step-3-references/fsm.tx``). Group 1 parses fine and is still a
broken state machine. Group 2 shows that the one semantic check textX
does perform, name uniqueness, is a side effect of reference resolution
rather than a rule of the language: the same defect is caught only when
something refers to the duplicated name.
"""

from pathlib import Path

from textx import metamodel_from_file
from textx.exceptions import TextXSemanticError, TextXSyntaxError

HERE = Path(__file__).resolve().parent


def try_parse(mm, title, text):
    print(f"\n--- {title}")
    try:
        # The triple-quoted texts start with a newline; drop it so that line 1
        # of the text is line 1 in the error positions.
        m = mm.model_from_str(text.lstrip("\n"))
        print(
            "ACCEPTED:",
            [s.name for s in m.states],
            "initial =",
            [s.name for s in m.states if s.initial],
        )
    except TextXSyntaxError as e:
        print("TextXSyntaxError:", e)
    except TextXSemanticError as e:
        print("TextXSemanticError:", e)


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")

    # 1. The grammar is satisfied; the meaning is broken. All ACCEPTED.
    try_parse(
        mm,
        "1a. no initial state",
        """
machine Light
events tick
state Red   { on tick -> Green }
state Green { on tick -> Red }
""",
    )

    try_parse(
        mm,
        "1b. two initial states",
        """
machine Light
events tick
initial state Red   { on tick -> Green }
initial state Green { on tick -> Red }
""",
    )

    try_parse(
        mm,
        "1c. two transitions on the same event in one state",
        """
machine Light
events tick
initial state Red { on tick -> Green  on tick -> Red }
state Green       { on tick -> Red }
""",
    )

    try_parse(
        mm,
        "1d. unreachable state",
        """
machine Light
events tick
initial state Red { on tick -> Red }
state Green       { on tick -> Red }
""",
    )

    # 2. Uniqueness is checked only as a side effect of resolving a reference.
    try_parse(
        mm,
        "2a. duplicate state name, referenced -> caught",
        """
machine Light
events tick
initial state Red { on tick -> Green }
state Green       { on tick -> Red }
state Green       { }
""",
    )

    try_parse(
        mm,
        "2b. duplicate state name, not referenced -> passes",
        """
machine Light
events tick
initial state Red { on tick -> Red }
state Green       { }
state Green       { }
""",
    )

    try_parse(
        mm,
        "2c. duplicate event, referenced -> caught",
        """
machine Light
events tick, tick
initial state Red { on tick -> Red }
""",
    )

    try_parse(
        mm,
        "2d. duplicate event, not referenced -> passes",
        """
machine Light
events tick, panic, panic
initial state Red { on tick -> Red }
""",
    )

    # 3. For contrast: a syntax error never reaches the model at all.
    try_parse(
        mm,
        "3. syntax error, for contrast",
        """
machine Light
events tick
initial state Red { on tick Green }
""",
    )


if __name__ == "__main__":
    main()
