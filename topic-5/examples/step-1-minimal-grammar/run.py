#!/usr/bin/env python3
from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    print(type(m).__name__, m.name)  # Machine Light
    print([s.name for s in m.states])  # ['Red', 'Green']
    print(type(m.states[0]))  # <class 'textx:fsm.State ...'>
    print(m.states[0].parent is m)  # True
    print([k for k in m.__dict__ if not k.startswith("_tx")])  # ['name', 'states']
    print([c.__name__ for c in mm])  # metamodel classes


if __name__ == "__main__":
    main()
