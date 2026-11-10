#!/usr/bin/env python3
"""Step 2a: the Visitor pattern in its textbook form (Gamma et al., 1994).

Hand-written node classes, each with exactly one ``accept`` method that
calls the visitor's method named after the node's class. One visitor class
per operation, one method per node class. ``accept`` is the only thing the
node classes know about visitors, and it never changes again: a new
operation is a new visitor class and nothing else.

This file exists to show the mechanism (double dispatch). The textX model
has no ``accept``, and we cannot add one to generated classes; ``visitor.py``
shows the Python form that does without it.
"""


class State:
    def __init__(self, name, initial=False, transitions=()):
        self.name, self.initial, self.transitions = name, initial, list(transitions)

    def accept(self, visitor):
        # First choice, by the node's class: this `accept` ran because self is a State.
        # Second choice, by the visitor's class: which `visit_State` runs.
        return visitor.visit_State(self)


class Transition:
    def __init__(self, event, target):
        self.event, self.target = event, target

    def accept(self, visitor):
        return visitor.visit_Transition(self)


class DotVisitor:
    """One column of the types x operations table: emit DOT."""

    def visit_State(self, s):
        lines = [f"{s.name} [shape=doublecircle];"] if s.initial else []
        lines += [t.accept(self).replace("SRC", s.name) for t in s.transitions]
        return "\n".join(lines)

    def visit_Transition(self, t):
        return f'SRC -> {t.target} [label="{t.event}"];'


class CountVisitor:
    """Another column: count nodes. Nothing else in this file changed to add it."""

    def visit_State(self, s):
        return 1 + sum(t.accept(self) for t in s.transitions)

    def visit_Transition(self, t):
        return 1


def main():
    red = State("Red", initial=True, transitions=[Transition("tick", "Green")])
    print(red.accept(DotVisitor()))
    print(red.accept(CountVisitor()))


if __name__ == "__main__":
    main()
