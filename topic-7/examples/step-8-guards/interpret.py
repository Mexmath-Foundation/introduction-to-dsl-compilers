#!/usr/bin/env python3
"""Step 8 interpreter: the step-5 interpreter plus guards.

The only change is in ``step``: a transition is taken if its event matches
AND its guard is absent or evaluates to true in the environment the caller
supplied. The guard is evaluated by ``ExprEval`` -- the recursive visitor of
expr.py -- so the interpreter itself stays as short as before. Transitions
are tried in document order; the first one whose guard holds wins, which is
how `on tick [..] -> Green` followed by `on tick -> Red` reads as if/else.
"""

from pathlib import Path

from expr import ExprEval
from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


class Interpreter:
    def __init__(self, machine, env):
        self.declared = {e.name: e for e in machine.events}
        self.state = next(s for s in machine.states if s.initial)
        self.env = env  # variable values the guards may read
        self.log = []

    def holds(self, guard):
        return guard is None or bool(ExprEval(self.env).visit(guard))

    def step(self, name):
        if name not in self.declared:
            raise ValueError(f"unknown event {name!r}")
        event = self.declared[name]
        taken = next(
            (t for t in self.state.transitions if t.event is event and self.holds(t.guard)), None
        )
        if taken is None:
            return self.state
        for action in taken.actions:
            self.perform(action)
        self.state = taken.target
        return self.state

    def perform(self, action):
        getattr(self, "do_" + action.kind)(action)

    def do_show(self, action):
        self.log.append(f"show {action.message}")

    def do_beep(self, action):
        self.log.append("beep")

    def run_lines(self, names):
        lines = [self.state.name]
        for name in names:
            before = len(self.log)
            state = self.step(name)
            lines += self.log[before:] + [state.name]
        return lines


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")
    for env in ({"count": 1, "night": 0}, {"count": 5, "night": 1}):
        print(env, Interpreter(m, env).run_lines(["tick", "tick", "panic", "tick"]))


if __name__ == "__main__":
    main()
