"""Print the model that your grammar builds from an ATM description.

Run it from the repository root:

    uv run python topic-5/show_atm.py topic-5/atm.atm

The script parses the description with ``atm.tx`` and prints every
state with its transitions and actions, as they came out of textX. Use
it to check that the model has the shape the tests expect; it is a
playground, not a test.
"""

import sys
from pathlib import Path

from textx import metamodel_from_file
from textx.exceptions import TextXError

GRAMMAR = Path(__file__).with_name("atm.tx")


def main(argv: list[str]) -> None:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <description.atm>")
        raise SystemExit(2)
    try:
        atm = metamodel_from_file(GRAMMAR).model_from_file(argv[1])
    except TextXError as error:
        # One line, like `textx check`, instead of a double traceback.
        print(f"ERROR: {error}")
        raise SystemExit(1) from None

    print(f"atm {atm.name}")
    print("events:", ", ".join(e.name for e in atm.events))
    for state in atm.states:
        marker = "initial " if state.initial else ""
        label = f' "{state.label}"' if state.label else ""
        print(f"{marker}state {state.name}{label}")
        for t in state.transitions:
            actions = ", ".join(
                f'{a.kind} "{a.message}"' if a.message else a.kind for a in t.actions
            )
            print(
                f"    on {t.event.name} -> {t.target.name}" + (f" do {actions}" if actions else "")
            )


if __name__ == "__main__":
    main(sys.argv)
