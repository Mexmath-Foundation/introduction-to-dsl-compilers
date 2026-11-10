#!/usr/bin/env python3
"""Step 2: the Visitor pattern in Python, on a textX model.

``Visitor`` is the base class every output of this topic derives from. It
does two things and nothing else:

* **dispatch**: ``visit(node)`` calls ``visit_<ClassName>(node)`` if the
  subclass defines it, else ``generic_visit``. The class of a textX model
  object is named after its grammar rule, so the method names are the rule
  names. This is how ``ast.NodeVisitor`` in the standard library works; no
  ``accept`` method on the nodes is needed, because Python knows an
  object's class at run time;
* **the walk**: ``generic_visit(node)`` visits the node's children, which
  are its *containment* attributes (``_tx_attrs``), never its references.
  Following ``target`` would loop on ``Red -> Green -> Red``. Down the tree,
  each node once, in document order.

``DotVisitor`` and ``CountVisitor`` are two operations on the same walk.
Adding the second changed nothing in the first, in ``Visitor`` or in the
model: that is the point of the pattern.
"""

from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


class Visitor:
    """Dispatch on the node's class name; walk containment attributes by default."""

    def visit(self, node):
        method = getattr(self, "visit_" + type(node).__name__, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for attr in type(node)._tx_attrs.values():
            if attr.cont and not attr.is_base_type:  # a contained object or list, not a str/bool
                value = getattr(node, attr.name)
                children = value if attr.mult != "1" else [value]
                for child in children:
                    if child is not None:
                        self.visit(child)


class DotVisitor(Visitor):
    """Emit the machine in DOT: a node per state, an edge per transition."""

    def __init__(self):
        self.lines = []

    def visit_Machine(self, mc):
        self.lines += [f"digraph {mc.name} {{", "  rankdir=LR;", "  node [shape=circle];"]
        self.generic_visit(mc)  # down to events and states
        self.lines.append("}")

    def visit_State(self, s):
        if s.initial:
            self.lines.append(f"  {s.name} [shape=doublecircle];")
        self.generic_visit(s)  # down to its transitions

    def visit_Transition(self, t):
        self.lines.append(f'  {t.parent.name} -> {t.target.name} [label="{t.event.name}"];')


class CountVisitor(Visitor):
    """Count states and transitions: a second operation, eight lines, no other change."""

    def __init__(self):
        self.states = self.transitions = 0

    def visit_State(self, s):
        self.states += 1
        self.generic_visit(s)

    def visit_Transition(self, t):
        self.transitions += 1


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    v = DotVisitor()
    v.visit(m)
    print("\n".join(v.lines))

    c = CountVisitor()
    c.visit(m)
    print(c.states, "states,", c.transitions, "transitions")


if __name__ == "__main__":
    main()
