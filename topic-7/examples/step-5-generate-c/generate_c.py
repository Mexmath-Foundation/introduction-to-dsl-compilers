#!/usr/bin/env python3
"""Step 5: generation. A visitor that writes C.

Same walk as the DOT visitor of step 3 (down the containment tree, every
state and transition once), different body: C instead of edges. Three things
are new, and all three come from the *target*, not from the model:

1. Declaration order. C wants the enums and the name tables before the
   function that uses them; the model interleaves states and transitions.
   The visitor therefore keeps three buffers -- ``header`` (light.h),
   ``decl`` and ``body`` (top and bottom of light.c) -- and appends each
   fragment to the one it belongs to. They are joined only at the end.
2. Escaping. ``show "..."`` becomes a C string literal, so backslashes,
   quotes and newlines must be escaped the way C's lexer expects. The model
   holds the message *as text*; the target decides how text is spelled.
   ``puts`` is used instead of ``printf`` so that a ``%`` in a message can
   never be read as a format directive.
3. A name for everything the C side has to refer to: ``RED`` for the enum
   constant, ``"Red"`` in the name table. The visitor computes both from the
   one ``name`` attribute; nothing is typed twice.
"""

from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


class Visitor:
    def visit(self, node):
        method = getattr(self, "visit_" + type(node).__name__, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for attr in type(node)._tx_attrs.values():
            if attr.cont and not attr.is_base_type:
                value = getattr(node, attr.name)
                for child in value if attr.mult != "1" else [value]:
                    if child is not None:
                        self.visit(child)


def c_string(text):
    """Spell ``text`` as a C string literal: the target's lexical layer."""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def C(obj):
    """The enum constant for a state or an event: RED, TICK."""
    return obj.name.upper()


class CVisitor(Visitor):
    def __init__(self):
        self.header = []  # light.h: what the driver needs to know
        self.decl = []  # light.c, top: the name tables
        self.body = []  # light.c, bottom: the step function

    def text_h(self):
        return "\n".join(self.header) + "\n"

    def text_c(self):
        return "\n".join(self.decl + [""] + self.body) + "\n"

    def visit_Machine(self, m):
        states = ", ".join(C(s) for s in m.states)
        events = ", ".join(C(e) for e in m.events)
        self.header += [
            "/* generated from light.fsm by generate_c.py; do not edit */",
            f"enum state {{ {states}, N_STATES }};",
            f"enum event {{ {events}, N_EVENTS }};",
            "extern const char *state_name[];",
            "extern const char *event_name[];",
            "extern const enum state initial_state;",
            "enum state step(enum state s, enum event e);",
        ]
        self.decl += [
            "/* generated from light.fsm by generate_c.py; do not edit */",
            "#include <stdio.h>",
            '#include "light.h"',
            "",
            "const char *state_name[] = { " + ", ".join(c_string(s.name) for s in m.states) + " };",
            "const char *event_name[] = { " + ", ".join(c_string(e.name) for e in m.events) + " };",
            f"const enum state initial_state = {C(next(s for s in m.states if s.initial))};",
        ]
        self.body += [
            "enum state step(enum state s, enum event e) {",
            "  switch (s) {",
        ]
        self.generic_visit(m)  # states, in document order
        self.body += ["  default: return s;", "  }", "}"]

    def visit_State(self, s):
        self.body.append(f"  case {C(s)}:")
        self.generic_visit(s)  # the transitions of this state
        self.body.append("    return s;")

    def visit_Transition(self, t):
        self.body.append(f"    if (e == {C(t.event)}) {{")
        self.generic_visit(t)  # the actions, before the state changes
        self.body.append(f"      return {C(t.target)};")
        self.body.append("    }")

    def visit_Action(self, a):
        if a.kind == "show":
            self.body.append(f"      puts({c_string('show ' + a.message)});")
        else:
            self.body.append('      puts("beep");')


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")
    v = CVisitor()
    v.visit(m)
    (HERE / "light.h").write_text(v.text_h())
    (HERE / "light.c").write_text(v.text_c())
    print(v.text_c(), end="")


if __name__ == "__main__":
    main()
