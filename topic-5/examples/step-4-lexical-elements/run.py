#!/usr/bin/env python3
from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    for s in m.states:
        print(s.name, repr(s.label), repr(s.timeout))
    # Red 'Stop' '30s'
    # Green 'Go' '45s'
    # Yellow '' None     <- missing optional parts: '' for STRING, None for a user match rule


if __name__ == "__main__":
    main()
