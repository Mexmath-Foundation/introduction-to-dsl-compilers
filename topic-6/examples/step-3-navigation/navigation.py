#!/usr/bin/env python3
"""Step 3: walking the model.

The model is a graph with three kinds of edge: down (containment attributes
such as ``m.states``), up (``parent``) and across (references such as
``t.target``). There are no reverse references and no "all objects of a
class" attribute, so every question of the form "all X in the model" or "who
refers to Y" is a traversal; textX provides helpers for those.

``light.fsm`` is the Topic 5 traffic light plus ``state Blue { }``, a state
nothing points at, so that the dead-end and reachability questions have
something to find.
"""

from pathlib import Path

from textx import (
    get_children,
    get_children_of_type,
    get_location,
    get_metamodel,
    get_model,
    get_parent_of_type,
    metamodel_from_file,
    textx_isinstance,
)

HERE = Path(__file__).resolve().parent


def main():
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    print("--- down: containment attributes")
    print([s.name for s in m.states])
    print([(t.event.name, t.target.name) for t in m.states[1].transitions])

    print("--- up: parent, and the helpers that climb for you")
    t = m.states[1].transitions[1]  # Green: on panic -> Red
    print(t.parent.name, t.parent.parent.name)  # Green Light
    print(get_parent_of_type("Machine", t).name)  # Light
    print(get_model(t) is m, get_metamodel(t) is mm)  # True True

    print("--- across: a reference is the object itself")
    print(t.target is m.states[0])  # True

    print("--- every transition in the machine, wherever it is")
    all_t = get_children_of_type("Transition", m)
    print(len(all_t), [(x.parent.name, x.event.name, x.target.name) for x in all_t])

    print("--- who leads into Red: the reverse of a reference")
    print([x.parent.name for x in all_t if x.target.name == "Red"])

    print("--- states with no way out (dead ends): a predicate")

    def is_dead_end(o):
        return textx_isinstance(o, mm["State"]) and not o.transitions

    print([s.name for s in get_children(is_dead_end, m)])

    print("--- unreachable states: follow target from the initial state")
    start = next(s for s in m.states if s.initial)
    reached, frontier = {start}, [start]
    while frontier:
        for x in frontier.pop().transitions:
            if x.target not in reached:
                reached.add(x.target)
                frontier.append(x.target)
    print([s.name for s in m.states if s not in reached])

    print("--- events nobody uses")
    used = {x.event for x in all_t}
    print([e.name for e in m.events if e not in used])

    print("--- where an object is in the file")
    print(get_location(m.states[3]))


if __name__ == "__main__":
    main()
