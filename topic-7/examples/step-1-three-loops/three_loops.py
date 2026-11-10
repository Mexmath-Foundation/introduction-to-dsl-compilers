#!/usr/bin/env python3
"""Step 1: three outputs from one model, each as a plain loop.

The traffic light of Topic 5 (``fsm.tx``, ``light.fsm``) is read once and
turned into three things: a DOT diagram, a run on a list of events, and a
C program. Each function is the obvious loop. Read them side by side and
look at what repeats and what differs; that is the question the Visitor
pattern answers in step 2.
"""

from pathlib import Path

from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def to_dot(m):
    """Visualize: emit the machine in the DOT language, one line per node and edge."""
    lines = [f"digraph {m.name} {{", "  rankdir=LR;", "  node [shape=circle];"]
    for s in m.states:
        if s.initial:
            lines.append(f"  {s.name} [shape=doublecircle];")
    for s in m.states:
        for t in s.transitions:
            lines.append(f'  {s.name} -> {t.target.name} [label="{t.event.name}"];')
    lines.append("}")
    return "\n".join(lines)


def run(m, events):
    """Interpret: follow the transitions for a list of event names; return the states visited."""
    declared = {e.name for e in m.events}
    state = next(s for s in m.states if s.initial)
    trace = [state.name]
    for name in events:
        if name not in declared:
            raise ValueError(f"unknown event {name!r}")
        taken = next((t for t in state.transitions if t.event.name == name), None)
        if taken is not None:  # an event with no transition here is ignored
            state = taken.target
        trace.append(state.name)
    return trace


def to_c(m):
    """Translate: emit a C step function, a switch over states with an if per transition."""

    def S(obj):  # a state or event name as a C identifier
        return obj.name.upper()

    states = ", ".join(S(s) for s in m.states)
    events = ", ".join(S(e) for e in m.events)
    out = [
        f"enum state {{ {states} }};",
        f"enum event {{ {events} }};",
        "",
        "enum state step(enum state s, enum event e) {",
        "  switch (s) {",
    ]
    for s in m.states:
        out.append(f"  case {S(s)}:")
        for t in s.transitions:
            out.append(f"    if (e == {S(t.event)}) return {S(t.target)};")
        out.append("    return s;")
    out += ["  }", "  return s;", "}"]
    return "\n".join(out)


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    print("=== to_dot")
    print(to_dot(m))
    print("\n=== run")
    print(run(m, ["tick", "tick", "panic", "tick", "tick", "tick"]))
    try:
        run(m, ["tick", "boom"])
    except ValueError as e:
        print("ValueError:", e)
    print("\n=== to_c")
    print(to_c(m))
    # Write it next to main.c; `gcc light.c main.c -o light && ./light` prints the
    # same trace as run() above, as enum indices: 0 1 2 2 0 1 2.
    (HERE / "light.c").write_text(to_c(m) + "\n")


if __name__ == "__main__":
    main()
