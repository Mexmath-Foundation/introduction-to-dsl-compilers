#!/usr/bin/env python3
"""Step 3: visualization as code generation, twice.

Two visitors over the Topic 5 traffic light (now with labels), both on the
``Visitor`` base of step 2:

* ``DotVisitor`` emits DOT for Graphviz: ``dot -Tpng light.dot -o light.png``;
* ``MermaidVisitor`` emits a Mermaid ``stateDiagram-v2``, which GitHub renders
  inside a Markdown file with no tool installed.

The second one costs the same handful of lines as the first: the walk is
shared, only the strings differ. What it adds is a lesson about the target
language: Mermaid has a lexical layer of its own, and a label such as
``Slow down; then stop`` must be escaped (``;`` becomes ``#59;``, ``"``
becomes ``#quot;``) or the diagram will not parse. DOT has the same need
with ``\\"``. A generator writes text in another language and must respect
that language's rules for strings, not just its own.
"""

from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


class Visitor:
    """Same as step 2: dispatch on the class name, walk containment attributes."""

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


class Emitter(Visitor):
    """A visitor that collects lines; `text()` joins them."""

    def __init__(self):
        self.lines = []

    def out(self, line):
        self.lines.append(line)

    def text(self):
        return "\n".join(self.lines) + "\n"


class DotVisitor(Emitter):
    def visit_Machine(self, mc):
        self.out(f"digraph {mc.name} {{")
        self.out("  rankdir=LR;")
        self.out("  node [shape=box, style=rounded];")
        self.generic_visit(mc)
        self.out("}")

    def visit_State(self, s):
        label = dot_string(f"{s.name}\n{s.label}" if s.label else s.name)
        peripheries = ", peripheries=2" if s.initial else ""  # double border = initial
        self.out(f"  {s.name} [label={label}{peripheries}];")
        self.generic_visit(s)

    def visit_Transition(self, t):
        self.out(f"  {t.parent.name} -> {t.target.name} [label={dot_string(t.event.name)}];")


class MermaidVisitor(Emitter):
    def visit_Machine(self, mc):
        self.out("stateDiagram-v2")
        self.out("    direction LR")
        self.generic_visit(mc)

    def visit_State(self, s):
        if s.initial:
            self.out(f"    [*] --> {s.name}")
        if s.label:
            self.out(f'    state "{mermaid_text(s.label)}" as {s.name}')
        self.generic_visit(s)

    def visit_Transition(self, t):
        self.out(f"    {t.parent.name} --> {t.target.name} : {mermaid_text(t.event.name)}")


def dot_string(text):
    """A DOT double-quoted string: escape the quote and the newline."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def mermaid_text(text):
    """Text inside a Mermaid label: quotes and semicolons must become entity codes."""
    return text.replace(";", "#59;").replace('"', "#quot;")  # ";" first: "#quot;" ends in one


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    for cls, name in ((DotVisitor, "light.dot"), (MermaidVisitor, "light.mmd")):
        v = cls()
        v.visit(m)
        (HERE / name).write_text(v.text())
        print(f"=== {name}")
        print(v.text())
    print("render: dot -Tpng -Gdpi=200 light.dot -o light.png")
    print("        mmdc -i light.mmd -o light-mermaid.png -t neutral -s 3")


if __name__ == "__main__":
    main()
