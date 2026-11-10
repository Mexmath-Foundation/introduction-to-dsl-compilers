#!/usr/bin/env python3
"""Step 4: interpretation. The model is the program; the events are its input.

``Interpreter`` is not a visitor over the model: it does not enumerate the
tree. It keeps one variable, the current state, and for each input event
looks up a transition, performs its actions and follows ``target``. That is
the walk *across* references, driven by data that arrives at run time.

Where the Visitor idea re-enters is the actions: ``perform`` dispatches on
``a.kind`` to ``do_show`` / ``do_beep``, one method per kind of action, the
way ``visit`` dispatched on the class name. With a grammar written as
``Action: Show | Beep`` the dispatch key would be the class name instead.

Two decisions are visible in ``step`` and must be documented for the user
of the language: an event the machine never declared is an error in the
input (``ValueError``); a declared event with no transition in the current
state is ignored. Another language could stop, or log.
"""

from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


class Interpreter:
    def __init__(self, machine):
        self.declared = {e.name: e for e in machine.events}
        self.state = next(s for s in machine.states if s.initial)
        self.log = []  # what the actions did, in order

    def step(self, name):
        """One event in; the new current state out."""
        if name not in self.declared:
            raise ValueError(f"unknown event {name!r}")
        event = self.declared[name]
        taken = next((t for t in self.state.transitions if t.event is event), None)
        if taken is None:  # design decision: a declared event with no transition here
            return self.state
        for action in taken.actions:
            self.perform(action)
        self.state = taken.target
        return self.state

    def perform(self, action):
        """Dispatch on the kind of action: one method per kind, visitor-style."""
        getattr(self, "do_" + action.kind)(action)

    def do_show(self, action):
        self.log.append(f"show {action.message!r}")

    def do_beep(self, action):
        self.log.append("beep")

    def run(self, names):
        """Feed a whole list of events; return the states visited."""
        trace = [self.state.name]
        for name in names:
            trace.append(self.step(name).name)
        return trace


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    i = Interpreter(m)
    print(i.run(["tick", "panic", "tick", "tick", "panic"]))
    print(i.log)
    try:
        i.step("boom")
    except ValueError as e:
        print("ValueError:", e)


if __name__ == "__main__":
    main()
