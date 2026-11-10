"""Hypothesis data generators for Topic 7: translation of ATM descriptions.

A copy of the well-formed part of ``topic-6/atm_rule_generators.py`` (the
data types, ``identifiers``, ``actions``, ``well_formed_atms`` and
``render``), so that the topic is self-contained, plus what translation
needs:

* ``event_sequences(atm)`` draws a list of declared event names of a
  generated ATM: the *input* of the interpreter and of the generated
  program. Some events in it will have no transition in the current
  state; the interpreter must ignore those, as the specification says.

The expected behaviour is known by construction: the test file has its own
small ``walk`` over a ``GeneratedAtm`` (the oracle), and the interpreter,
the Mermaid text and the compiled C program must agree with it. Students
are encouraged to add more strategies here (and more tests that use them).
"""

from typing import NamedTuple

from hypothesis import strategies as st

# Every keyword of the language (including the optional extension), kept
# out of generated names: keywords are not reserved in textX.
KEYWORDS = frozenset(
    {
        "atm",
        "events",
        "initial",
        "state",
        "on",
        "do",
        "show",
        "eject_card",
        "retain_card",
        "dispense",
        "counters",
        "inc",
        "reset",
    }
)

SIMPLE_ACTIONS = ("eject_card", "retain_card", "dispense")


class GeneratedAction(NamedTuple):
    kind: str
    message: str  # '' for every kind but "show"


class GeneratedTransition(NamedTuple):
    event: str
    target: str
    actions: list[GeneratedAction]


class GeneratedState(NamedTuple):
    name: str
    initial: bool
    label: str  # '' when the state has no label
    transitions: list[GeneratedTransition]


class GeneratedAtm(NamedTuple):
    name: str
    events: list[str]
    states: list[GeneratedState]

    def initial(self) -> GeneratedState:
        return next(s for s in self.states if s.initial)


# Built from two text strategies rather than `from_regex` as in Topic 5: the
# same identifiers, but Hypothesis shrinks a failing example much faster.
_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
identifiers = st.builds(
    str.__add__,
    st.text(alphabet=_LETTERS, min_size=1, max_size=1),
    st.text(alphabet=_LETTERS + "0123456789", max_size=11),
).filter(lambda name: name not in KEYWORDS)

messages = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126, exclude_characters='"\\'),
    min_size=1,
    max_size=20,
)

actions = st.lists(
    st.one_of(
        st.sampled_from(SIMPLE_ACTIONS).map(lambda kind: GeneratedAction(kind, "")),
        messages.map(lambda message: GeneratedAction("show", message)),
    ),
    max_size=3,
)

# Action lists that do not both eject and retain the card (rule 6).
consistent_actions = actions.filter(
    lambda acts: not ({"eject_card", "retain_card"} <= {a.kind for a in acts})
)


@st.composite
def well_formed_atms(draw: st.DrawFn, min_states: int = 1, max_states: int = 5) -> GeneratedAtm:
    """A random ATM that satisfies every rule of the topic."""
    name = draw(identifiers)
    # Rule 2: unique event names, unique state names (a state and an event may
    # share a name; the rule is per kind).
    events = draw(st.lists(identifiers, min_size=1, max_size=4, unique=True))
    names = draw(st.lists(identifiers, min_size=min_states, max_size=max_states, unique=True))

    # transitions[state][event] = target; one transition per event (rule 3).
    transitions: dict[str, dict[str, str]] = {n: {} for n in names}

    # Rules 4 and 5: a chain names[0] -> names[1] -> ... -> names[-1] makes
    # every state reachable from names[0], and the last state points
    # somewhere, so every state has a way out.
    for here, there in zip(names, [*names[1:], draw(st.sampled_from(names))], strict=True):
        transitions[here][draw(st.sampled_from(events))] = there

    # Extra transitions on events a state does not handle yet.
    for state_name in names:
        for event in draw(st.lists(st.sampled_from(events), unique=True)):
            transitions[state_name].setdefault(event, draw(st.sampled_from(names)))

    # Rule 7: every declared event is used somewhere.
    for event in events:
        if not any(event in handled for handled in transitions.values()):
            transitions[draw(st.sampled_from(names))][event] = draw(st.sampled_from(names))

    states = [
        GeneratedState(
            state_name,
            index == 0,  # rule 1: names[0] is the one initial state
            draw(st.one_of(st.just(""), messages)),
            [
                GeneratedTransition(event, target, draw(consistent_actions))  # rule 6
                for event, target in transitions[state_name].items()
            ],
        )
        for index, state_name in enumerate(names)
    ]
    return GeneratedAtm(name, events, states)


# ----------------------------------------------------------------------------
# Writing generated data in the DSL (identical to Topic 5).


def render_action(action: GeneratedAction) -> str:
    return f'show "{action.message}"' if action.kind == "show" else action.kind


def render(atm: GeneratedAtm) -> str:
    """Write a generated ATM in the DSL."""
    lines = [
        "// generated by atm_translate_generators.py",
        f"atm {atm.name}",
        "",
        "events " + ", ".join(atm.events),
        "",
    ]
    for state in atm.states:
        head = "initial " if state.initial else ""
        head += f"state {state.name}"
        if state.label:
            head += f' "{state.label}"'
        lines.append(head + " {")
        for t in state.transitions:
            line = f"    on {t.event} -> {t.target}"
            if t.actions:
                line += " do " + ", ".join(render_action(a) for a in t.actions)
            lines.append(line)
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Inputs for the interpreter and the generated program.


@st.composite
def event_sequences(draw: st.DrawFn, atm: GeneratedAtm, max_size: int = 8) -> list[str]:
    """A list of declared event names of ``atm``, in any order, possibly empty."""
    return draw(st.lists(st.sampled_from(atm.events), max_size=max_size))
