#!/usr/bin/env python3
"""Print the parse shape of every guard in light.fsm: one line per node, indented.

A reader's tool, not part of the pipeline. It shows that textX creates an object for
every precedence level it passed through, which is why the visitors in expr.py treat
"one operand" as "return the operand".
"""

from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def shape(node, depth=0):
    pad = "  " * depth
    cls = type(node).__name__
    if cls == "Int":
        return f"{pad}Int {node.value}"
    if cls == "Var":
        return f"{pad}Var {node.name}"
    if cls == "NotExpr":
        return f"{pad}NotExpr\n" + shape(node.operand, depth + 1)
    ops = " ".join(getattr(node, "ops", []))
    head = f"{pad}{cls}" + (f" [{ops}]" if ops else "")
    return "\n".join([head] + [shape(o, depth + 1) for o in node.operands])


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")
    for s in m.states:
        for t in s.transitions:
            if t.guard is not None:
                print(f"{s.name} / on {t.event.name}:")
                print(shape(t.guard, 1))


if __name__ == "__main__":
    main()
