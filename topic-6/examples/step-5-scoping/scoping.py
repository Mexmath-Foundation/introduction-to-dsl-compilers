#!/usr/bin/env python3
"""Step 5: scopes, when one global namespace is not enough.

``two_machines.fsm`` holds two machines, and both happen to have a state
``Green``. By default textX looks a ``[State]`` reference up among *all*
State objects in the file (one global namespace per class), so ``-> Green``
inside ``Light`` has two candidates and resolution fails.

What we meant is a *scope*: look for the target among the states of the
machine that contains the transition, like a local variable inside a
function. A scope provider changes where reference resolution searches. It
is not a check we write; it runs in the resolution step, before any
processor.

Three ways to say it:

1. ``fsm.tx`` + ``RelativeName`` registered in Python (section 2);
2. ``fsm_rrel.tx``: the same rule written inside the grammar (section 4);
3. ``fsm_fqn.tx`` + ``FQN()``: dotted names such as ``Door.Open`` (section 5).
"""

from pathlib import Path

from textx import metamodel_from_file
from textx.exceptions import TextXSemanticError
from textx.scoping.providers import FQN, RelativeName

HERE = Path(__file__).resolve().parent


def show(m):
    """Print, for each machine, where the first transition of its first state leads."""
    for mc in m.machines:
        t = mc.states[0].transitions[0]
        print(f"{mc.name}.{mc.states[0].name} -> {t.target.name} (owned by {t.target.parent.name})")


def main():
    print("=== 1. default scope: one global namespace per class")
    mm = metamodel_from_file(HERE / "fsm.tx")
    try:
        mm.model_from_file(HERE / "two_machines.fsm")
    except TextXSemanticError as e:
        print("TextXSemanticError:", e)

    print("\n=== 2. RelativeName: look for the target among the states of MY machine")
    # 'parent.parent.states' is a path read from the Transition: up to its
    # State, up to its Machine, then into that machine's `states`.
    # Registered per attribute, as 'Class.attribute'.
    mm = metamodel_from_file(HERE / "fsm.tx")
    mm.register_scope_providers(
        {
            "Transition.target": RelativeName("parent.parent.states"),
            "Transition.event": RelativeName("parent.parent.events"),
        }
    )
    m = mm.model_from_file(HERE / "two_machines.fsm")
    show(m)
    print("Door keeps its own, unreferenced Green:", [s.name for s in m.machines[1].states])

    print("\n=== 3. with a scope, a reference across machines is an error")
    # cross_machine.fsm differs in one place: Door.Closed points at Red, which
    # is a state of Light. Line 8 is where the reference stands.
    try:
        mm.model_from_file(HERE / "cross_machine.fsm")
    except TextXSemanticError as e:
        print("TextXSemanticError:", e)

    print("\n=== 4. the same rule written in the grammar (RREL), no Python")
    mm = metamodel_from_file(HERE / "fsm_rrel.tx")
    show(mm.model_from_file(HERE / "two_machines.fsm"))

    print("\n=== 5. FQN: dotted names across machines, Door.Open")
    # Only targets get dotted names; events stay local to their machine, so
    # `Transition.event` keeps the RelativeName provider of section 2.
    mm = metamodel_from_file(HERE / "fsm_fqn.tx")
    mm.register_scope_providers(
        {
            "Transition.target": FQN(),
            "Transition.event": RelativeName("parent.parent.events"),
        }
    )
    show(mm.model_from_file(HERE / "dotted_name.fsm"))


if __name__ == "__main__":
    main()
