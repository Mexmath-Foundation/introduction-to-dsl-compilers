#!/usr/bin/env python3
"""Step 6: the same C, from a template instead of a visitor.

A visitor is code that produces text; a template is text that contains
code. When the output is mostly fixed text with model values dropped in,
the template reads like the output and is the better tool: ``light.c.j2``
looks like light.c. When the output needs computation per node (the three
buffers of step 5, name mangling, cycle detection), the visitor wins.
Most real generators use both: a visitor that computes, templates that
spell.

Two rules carry over unchanged from step 5:
* escaping is still the target's business -- ``c_string`` is registered as a
  Jinja *filter* and every model string passes through it in the template;
* the model is read-only -- the template reads ``m.states`` and friends and
  never computes anything the model does not already hold.

The output must be byte-identical to step 5's below the header comment;
``--check`` proves it.
"""

import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def c_string(text):
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def C(obj):
    return obj.name.upper()


def render(m, source="light.fsm"):
    env = Environment(
        loader=FileSystemLoader(HERE),
        undefined=StrictUndefined,  # a typo in the template is an error, not an empty string
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )
    env.filters["c_string"] = c_string
    env.filters["C"] = C
    return {
        "light.h": env.get_template("light.h.j2").render(m=m, source=source),
        "light.c": env.get_template("light.c.j2").render(m=m, source=source),
    }


def main(argv):
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")
    files = render(m)
    for name, text in files.items():
        (HERE / name).write_text(text)
    print(files["light.c"], end="")

    if "--check" in argv:  # the visitor of step 5 must produce the same bytes
        sys.path.insert(0, str(HERE.parent / "step-5-generate-c"))
        from generate_c import CVisitor

        v = CVisitor()
        v.visit(m)

        def body(text):  # drop the first line: it names the generator
            return text.split("\n", 1)[1]

        same = body(v.text_h()) == body(files["light.h"]) and body(v.text_c()) == body(
            files["light.c"]
        )
        print("visitor == template (below the header comment):", same)
        return 0 if same else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
