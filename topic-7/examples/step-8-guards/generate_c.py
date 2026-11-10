#!/usr/bin/env python3
"""Step 8 generator: the step-5 CVisitor plus guards and variables.

Two visitors cooperate. ``VarCollector`` runs first and answers "which
variables does this machine read?" -- the C side must declare them before
the step function can mention them (the order problem of step 5 again, now
across two walks). Then ``CVisitor`` emits as before, calling ``ExprToC`` on
each guard to spell the condition in C. A guard is an extra conjunct in the
transition's ``if``; a transition without a guard keeps the step-5 shape.
"""

from pathlib import Path

from expr import ExprToC, VarCollector, Visitor
from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def c_string(text):
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def C(obj):
    return obj.name.upper()


class CVisitor(Visitor):
    def __init__(self, variables):
        self.variables = sorted(variables)
        self.header, self.decl, self.body = [], [], []

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
            *[f"extern int {v};" for v in self.variables],  # the guards' variables
            "int set_var(const char *name, int value);",
            "enum state step(enum state s, enum event e);",
        ]
        self.decl += [
            "/* generated from light.fsm by generate_c.py; do not edit */",
            "#include <stdio.h>",
            "#include <string.h>",
            '#include "light.h"',
            "",
            "const char *state_name[] = { " + ", ".join(c_string(s.name) for s in m.states) + " };",
            "const char *event_name[] = { " + ", ".join(c_string(e.name) for e in m.events) + " };",
            f"const enum state initial_state = {C(next(s for s in m.states if s.initial))};",
            *[f"int {v} = 0;" for v in self.variables],
            "",
            "int set_var(const char *name, int value) {",
            *[
                f"  if (strcmp(name, {c_string(v)}) == 0) {{ {v} = value; return 1; }}"
                for v in self.variables
            ],
            "  return 0;",
            "}",
        ]
        self.body += ["enum state step(enum state s, enum event e) {", "  switch (s) {"]
        self.generic_visit(m)
        self.body += ["  default: return s;", "  }", "}"]

    def visit_State(self, s):
        self.body.append(f"  case {C(s)}:")
        self.generic_visit(s)
        self.body.append("    return s;")

    def visit_Transition(self, t):
        cond = f"e == {C(t.event)}"
        if t.guard is not None:
            cond += " && " + ExprToC().visit(t.guard)  # the recursive visitor, as text
        self.body.append(f"    if ({cond}) {{")
        self.generic_visit(t)
        self.body.append(f"      return {C(t.target)};")
        self.body.append("    }")

    def visit_Action(self, a):
        if a.kind == "show":
            self.body.append(f"      puts({c_string('show ' + a.message)});")
        else:
            self.body.append('      puts("beep");')


def generate(m):
    vc = VarCollector()
    vc.visit(m)  # walk 1: what must be declared
    v = CVisitor(vc.names)
    v.visit(m)  # walk 2: emit
    return v


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")
    v = generate(m)
    (HERE / "light.h").write_text(v.text_h())
    (HERE / "light.c").write_text(v.text_c())
    print(v.text_c(), end="")


if __name__ == "__main__":
    main()
