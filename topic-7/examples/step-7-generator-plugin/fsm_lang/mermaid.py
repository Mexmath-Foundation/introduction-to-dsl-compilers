"""The Mermaid visitor of step 3, unchanged, now inside a package."""


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


class Emitter(Visitor):
    def __init__(self):
        self.lines = []

    def out(self, line):
        self.lines.append(line)

    def text(self):
        return "\n".join(self.lines) + "\n"


def mermaid_text(text):
    """Text inside a Mermaid label: quotes and semicolons must become entity codes."""
    return text.replace(";", "#59;").replace('"', "#quot;")  # ";" first: "#quot;" ends in one


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
