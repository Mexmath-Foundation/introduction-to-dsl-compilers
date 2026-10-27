#!/usr/bin/env python3
"""Step 2: containment (``target=State``) vs reference (``target=[State]``).

The two grammars below differ in one pair of brackets. Grammar A says a
transition *contains* a state definition; grammar B says it *refers to* a
state defined elsewhere. The script shows what text each one accepts, what
objects it builds, and which error each one raises for the other's text.

Both grammars use ``event=ID`` to stay short. The real traffic light uses
``event=[Event]``, a reference like ``target``.
"""

from textx import metamodel_from_str
from textx.exceptions import TextXSemanticError, TextXSyntaxError

# A: the target is a whole state definition, written inside the transition.
GRAMMAR_A = """
Machine: states+=State ;
State: 'state' name=ID '{' transitions*=Transition '}' ;
Transition: 'on' event=ID '->' target=State ;
"""

# B: the target is a name; textX looks up the State object with that name.
GRAMMAR_B = """
Machine: states+=State ;
State: 'state' name=ID '{' transitions*=Transition '}' ;
Transition: 'on' event=ID '->' target=[State] ;
"""


def main():
    mm_a = metamodel_from_str(GRAMMAR_A)
    mm_b = metamodel_from_str(GRAMMAR_B)

    print("=== A: target=State (containment)")
    # The target must be a whole definition, written inside the transition.
    m = mm_a.model_from_str(
        "state Red  { on tick -> state Green { } }\nstate Blue { on tick -> state Green { } }"
    )
    g1 = m.states[0].transitions[0].target
    g2 = m.states[1].transitions[0].target
    # Green is created *inside* a transition, so it is not a state of the machine...
    print("machine states:", [s.name for s in m.states])  # ['Red', 'Blue']
    print("g1.parent.parent.name:", g1.parent.parent.name)  # Red
    # ...and the two definitions with the same name are two different objects.
    print("same name:", g1.name == g2.name, "| same object:", g1 is g2)  # True | False

    # A bare name is not a definition: syntax error.
    try:
        mm_a.model_from_str("state Red { on tick -> Green }")
    except TextXSyntaxError as e:
        print("bare name under A:", e)

    print("\n=== B: target=[State] (reference)")
    # Definitions at the top level; the transition only names its target.
    m = mm_b.model_from_str("state Red   { on tick -> Green }\nstate Green { on tick -> Red }")
    red, green = m.states
    t = red.transitions[0]
    print("machine states:", [s.name for s in m.states])  # ['Red', 'Green']
    print("t.target is green:", t.target is green)  # True: a reference, not a copy
    print("green.parent is the machine:", green.parent is m)  # True
    print("the cycle closes:", green.transitions[0].target is red)  # True

    # A name with no definition: semantic error (reference resolution fails).
    try:
        mm_b.model_from_str("state Red { on tick -> Green }")
    except TextXSemanticError as e:
        print("unknown name under B:", e)

    # A definition where a name is expected: still a syntax error, but look
    # where the `*` is. `state` is a valid ID (Topic 5, step 6: keywords are
    # not reserved), so it is swallowed as the target name and the parser
    # stumbles on `Green`.
    try:
        mm_b.model_from_str("state Red { on tick -> state Green { } }")
    except TextXSyntaxError as e:
        print("definition under B:", e)


if __name__ == "__main__":
    main()
