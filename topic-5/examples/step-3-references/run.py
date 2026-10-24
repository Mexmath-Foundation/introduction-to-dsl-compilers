#!/usr/bin/env python3
from pathlib import Path

from textx import metamodel_from_file
from textx.exceptions import TextXSemanticError, TextXSyntaxError

HERE = Path(__file__).resolve().parent


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    t = m.states[0].transitions[0]
    print(type(t.event).__name__, t.event.name)  # Event tick
    print(type(t.target).__name__, t.target.name)  # State Green
    print(t.target is m.states[1])  # True  -- a reference, not a string
    print(t.parent.name, t.parent.parent.name)  # Red Light

    source = (HERE / "light.fsm").read_text()

    # semantic error: typo in a state name
    try:
        mm.model_from_str(source.replace("-> Yellow", "-> Yelow"))
    except TextXSemanticError as e:
        print("SEMANTIC:", e)  # ...:8:16: Unknown object "Yelow" of class "State"

    # syntax error: missing arrow
    try:
        mm.model_from_str(source.replace("on tick -> Green", "on tick Green"))
    except TextXSyntaxError as e:
        print("SYNTAX:", e)  # ...:5:13: Expected '->' => '  on tick *Green'


if __name__ == "__main__":
    main()
