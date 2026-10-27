#!/usr/bin/env python3
"""Step 4: object processors and model processors.

A processor is a function textX calls for you while it builds the model.
There are two kinds:

* an *object processor* is registered per class and called once per object,
  depth-first, children before their parent; it may check the object or
  return a replacement value;
* a *model processor* is called once per model after all objects exist and
  all references are resolved; it is where whole-graph rules live.

The grammar is the Topic 5 traffic light with ``'after' timeout=Duration``
restored from ``topic-5/examples/step-4-lexical-elements`` (``Duration`` is a
match rule: a regex, so ``timeout`` is a plain string until section 1).

Each section builds a fresh metamodel, so the processors of one section do
not leak into the next. Section 4 puts them all on one metamodel.
"""

from pathlib import Path

from textx import get_location, metamodel_from_file
from textx.exceptions import TextXSemanticError

HERE = Path(__file__).resolve().parent
GOOD = (HERE / "light.fsm").read_text()


def try_parse(mm, title, text):
    """Parse `text` and report either the states or the semantic error."""
    print(f"\n--- {title}")
    try:
        m = mm.model_from_str(text)
        print("ACCEPTED", [(s.name, s.timeout) for s in m.states])
    except TextXSemanticError as e:
        print("TextXSemanticError:", e)


# ---------------------------------------------------------------------------
# The processors. Each one is a plain function; sections below register them.


def duration_to_seconds(text):
    """Object processor on the match rule `Duration`.

    A processor on a match rule receives the matched *string* while parsing.
    Whatever it returns is stored in the model instead of that string, so
    `s.timeout` becomes a number. The return value is stored as is, `None`
    included, so a match-rule processor must always return the value.
    """
    if text.endswith("ms"):
        return int(text[:-2]) / 1000
    if text.endswith("s"):
        return int(text[:-1])
    if text.endswith("m"):
        return int(text[:-1]) * 60


def one_transition_per_event(state):
    """Object processor on `State`: a local rule, one object at a time.

    It returns nothing, so the state stays as it is; it only raises when the
    rule is broken. `get_location(t)` points at the offending transition, not
    at the state, because that is where the fix goes.
    """
    seen = set()
    for t in state.transitions:
        if t.event.name in seen:
            raise TextXSemanticError(
                f'state "{state.name}" has two transitions on "{t.event.name}"',
                **get_location(t),
            )
        seen.add(t.event.name)


def exactly_one_initial(model, metamodel):
    """Model processor: a rule about the set of states, not about one state.

    Where to point is a design decision: with two initial states the culprit
    is the second one; with none there is no culprit, so point at the start
    of the file (the model object itself).
    """
    initial = [s for s in model.states if s.initial]
    if len(initial) != 1:
        culprit = initial[1] if len(initial) > 1 else model
        raise TextXSemanticError(
            f"expected exactly one initial state, found {len(initial)}",
            **get_location(culprit),
        )


def all_states_reachable(model, metamodel):
    """Model processor: follow `target` from the initial state (a worklist walk).

    It assumes exactly one initial state exists; that holds because
    `exactly_one_initial` is registered first and model processors run in
    registration order.
    """
    start = next(s for s in model.states if s.initial)
    reached, frontier = {start}, [start]
    while frontier:
        for t in frontier.pop().transitions:
            if t.target not in reached:
                reached.add(t.target)
                frontier.append(t.target)
    for s in model.states:
        if s not in reached:
            raise TextXSemanticError(f'state "{s.name}" is unreachable', **get_location(s))


def main():
    # -----------------------------------------------------------------------
    print("=== 0. when is each processor called?")
    # One processor per class, each only logs. The order of the log answers
    # the question from the lecture: are references resolved inside an object
    # processor? Yes: `t.target` is already a State object, not a name.
    mm = metamodel_from_file(HERE / "fsm.tx")
    log = []
    mm.register_obj_processors(
        {
            "Event": lambda e: log.append(f"obj Event {e.name}"),
            "Transition": lambda t: log.append(f"obj Transition -> <State:{t.target.name}>"),
            "State": lambda s: log.append(f"obj State {s.name}"),
            "Machine": lambda m: log.append(f"obj Machine {m.name}"),
        }
    )
    mm.register_model_processor(lambda model, metamodel: log.append("MODEL processor"))
    mm.model_from_str(GOOD)
    print("\n".join(log))

    # -----------------------------------------------------------------------
    print("\n=== 1. an object processor that returns a value replaces the value")
    mm = metamodel_from_file(HERE / "fsm.tx")
    mm.register_obj_processors({"Duration": duration_to_seconds})
    try_parse(mm, "'30s' is stored as 30", GOOD)

    # -----------------------------------------------------------------------
    print("\n=== 2. an object processor that raises: a local check with a position")
    mm = metamodel_from_file(HERE / "fsm.tx")
    mm.register_obj_processors({"State": one_transition_per_event})
    try_parse(mm, "good model passes", GOOD)
    try_parse(
        mm,
        "duplicate transition is rejected, pointing at line 5",
        "machine Light\n"
        "events tick\n"
        "initial state Red {\n"
        "    on tick -> Green\n"
        "    on tick -> Red\n"
        "}\n"
        "state Green { on tick -> Red }\n",
    )

    # -----------------------------------------------------------------------
    print("\n=== 3. model processors: whole-graph rules")
    mm = metamodel_from_file(HERE / "fsm.tx")
    mm.register_model_processor(exactly_one_initial)
    mm.register_model_processor(all_states_reachable)
    try_parse(mm, "good model passes", GOOD)
    try_parse(
        mm, "two initial states", "machine L events t initial state A { } initial state B { }"
    )
    try_parse(mm, "no initial state", "machine L events t state A { }")
    try_parse(
        mm,
        "unreachable state: A points at itself, B at nothing",
        "machine L\nevents t\ninitial state A { on t -> A }\nstate B { }\n",
    )

    # -----------------------------------------------------------------------
    print("\n=== 4. one metamodel, many models")
    # Register everything once; every model parsed with this metamodel is
    # converted and checked. This is the shape the ATM homework asks for.
    mm = metamodel_from_file(HERE / "fsm.tx")
    mm.register_obj_processors({"Duration": duration_to_seconds, "State": one_transition_per_event})
    mm.register_model_processor(exactly_one_initial)
    mm.register_model_processor(all_states_reachable)
    try_parse(mm, "model 1: light.fsm", GOOD)
    try_parse(
        mm, "model 2: a one-liner", "machine L events t initial state A { after 2m on t -> A }"
    )


if __name__ == "__main__":
    main()
