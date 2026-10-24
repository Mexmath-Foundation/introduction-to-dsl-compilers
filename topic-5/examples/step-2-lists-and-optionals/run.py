#!/usr/bin/env python3
from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    print(m.events)  # ['tick', 'panic']
    print(
        [(s.name, s.initial) for s in m.states]
    )  # [('Red', True), ('Green', False), ('Yellow', False)]


if __name__ == "__main__":
    main()
