#!/usr/bin/env python3
from pathlib import Path

from textx import get_children_of_type, metamodel_from_file

HERE = Path(__file__).resolve().parent


class State:
    # textX calls __init__ with the grammar attributes as keyword arguments,
    # plus `parent` for contained objects. A class without a matching
    # __init__ fails with TypeError at model construction.
    def __init__(self, parent, name, initial, transitions, label="", timeout=""):
        self.parent = parent
        self.name = name
        self.initial = initial
        self.transitions = transitions
        self.label = label
        self.timeout = timeout

    def next(self, event_name):
        for t in self.transitions:
            if t.event.name == event_name:
                return t.target
        return self  # no transition for this event: stay


class Machine:
    # The root object has no parent, so no `parent` parameter here.
    def __init__(self, name, events, states):
        self.name = name
        self.events = events
        self.states = states

    def run(self, *events):
        s = next(st for st in self.states if st.initial)
        trace = [s.name]
        for e in events:
            s = s.next(e)
            trace.append(s.name)
        return trace


def main():
    # Class names must match rule names. Transition is not overridden: textX keeps
    # generating it, and generated and user classes coexist in one model.
    mm = metamodel_from_file(HERE / "fsm.tx", classes=[State, Machine])
    m = mm.model_from_file(HERE / "light.fsm")

    print(type(m))  # <class '__main__.Machine'>
    print(m.run("tick", "tick", "panic", "tick"))  # ['Red', 'Green', 'Yellow', 'Yellow', 'Red']
    print([t.target.name for t in get_children_of_type("Transition", m)])


if __name__ == "__main__":
    main()
