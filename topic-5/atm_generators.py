"""Hypothesis data generators for Topic 5: ATM description language.

The central strategy is ``atms()``: it generates a random *valid* ATM
description as plain Python data (``GeneratedAtm``), and ``render``
writes that data in the DSL. A test parses the rendered text with the
student's grammar and compares the model with the data it was rendered
from — the expected answer is known by construction, the generator
never needs the grammar.

Validity is guaranteed by construction too: names are identifiers that
are not keywords of the language, state and event names are unique,
exactly one state is initial, every transition targets a declared state
on a declared event, and a state has at most one transition per event.
The ``atms_with_*`` strategies deliberately break exactly one of these
guarantees, so a test can assert that the description is rejected.

Only ``atms`` and ``atms_with_unknown_target`` are used by the Topic 5
starter suite. The other strategies (two initial states, duplicate
transitions, event sequences for a simulation) are ready for the later
topics that build semantic checks and an interpreter on this language.

Students are encouraged to add more generators here (and more tests
that use them).
"""

from typing import NamedTuple

from hypothesis import strategies as st

# Every keyword of the language (including the optional extension), kept
# out of generated names: keywords are not reserved in textX, and what
# happens with a state called `on` is an exercise, not a test fixture.
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

# Actions that take no argument; `show` takes a message.
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

    def state(self, name: str) -> GeneratedState:
        return next(s for s in self.states if s.name == name)


class GeneratedSimulation(NamedTuple):
    """An ATM together with a sequence of its own (declared) events."""

    atm: GeneratedAtm
    events: list[str]


# Identifiers of the language, minus the keywords.
identifiers = st.from_regex(r"[A-Za-z_][A-Za-z0-9_]{0,11}", fullmatch=True).filter(
    lambda name: name not in KEYWORDS
)

# Text of labels and messages: printable ASCII without the two characters
# that would need escaping inside a double-quoted string.
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


@st.composite
def atms(draw: st.DrawFn, min_states: int = 1, max_states: int = 5) -> GeneratedAtm:
    name = draw(identifiers)
    events = draw(st.lists(identifiers, min_size=1, max_size=4, unique=True))
    names = draw(st.lists(identifiers, min_size=min_states, max_size=max_states, unique=True))
    initial = draw(st.integers(min_value=0, max_value=len(names) - 1))

    states = []
    for index, state_name in enumerate(names):
        # A subset of the events, each handled by exactly one transition.
        handled = draw(st.lists(st.sampled_from(events), unique=True))
        transitions = [
            GeneratedTransition(event, draw(st.sampled_from(names)), draw(actions))
            for event in handled
        ]
        label = draw(st.one_of(st.just(""), messages))
        states.append(GeneratedState(state_name, index == initial, label, transitions))
    return GeneratedAtm(name, events, states)


@st.composite
def simulations(draw: st.DrawFn, max_events: int = 12) -> GeneratedSimulation:
    atm = draw(atms())
    events = draw(st.lists(st.sampled_from(atm.events), max_size=max_events))
    return GeneratedSimulation(atm, events)


@st.composite
def atms_with_unknown_event(draw: st.DrawFn) -> tuple[GeneratedAtm, str]:
    """A valid ATM and an event name it does not declare."""
    atm = draw(atms())
    unknown = draw(identifiers.filter(lambda name: name not in atm.events))
    return atm, unknown


@st.composite
def atms_with_unknown_target(draw: st.DrawFn) -> GeneratedAtm:
    """One transition points at a state that is not declared."""
    atm = draw(atms())
    names = [s.name for s in atm.states]
    unknown = draw(identifiers.filter(lambda name: name not in names))
    return _with_transition(
        draw, atm, GeneratedTransition(draw(st.sampled_from(atm.events)), unknown, [])
    )


@st.composite
def atms_with_two_initial_states(draw: st.DrawFn) -> GeneratedAtm:
    """Two states are marked `initial`."""
    atm = draw(atms(min_states=2))
    extra = draw(st.sampled_from([s for s in atm.states if not s.initial]))
    states = [s._replace(initial=True) if s is extra else s for s in atm.states]
    return atm._replace(states=states)


@st.composite
def atms_with_duplicate_transition(draw: st.DrawFn) -> GeneratedAtm:
    """One state has two transitions on the same event."""
    atm = draw(atms())
    event = draw(st.sampled_from(atm.events))
    state = draw(st.sampled_from(atm.states))
    names = [s.name for s in atm.states]
    duplicates = [
        GeneratedTransition(event, draw(st.sampled_from(names)), []),
        GeneratedTransition(event, draw(st.sampled_from(names)), []),
    ]
    new_state = state._replace(transitions=[*state.transitions, *duplicates])
    states = [new_state if s is state else s for s in atm.states]
    return atm._replace(states=states)


def _with_transition(
    draw: st.DrawFn, atm: GeneratedAtm, transition: GeneratedTransition
) -> GeneratedAtm:
    # Put `transition` into a random state, replacing any transition that
    # state already had on the same event (so the one-per-event rule holds).
    state = draw(st.sampled_from(atm.states))
    kept = [t for t in state.transitions if t.event != transition.event]
    new_state = state._replace(transitions=[*kept, transition])
    states = [new_state if s is state else s for s in atm.states]
    return atm._replace(states=states)


def render_action(action: GeneratedAction) -> str:
    return f'show "{action.message}"' if action.kind == "show" else action.kind


def render(atm: GeneratedAtm) -> str:
    """Write a generated ATM in the DSL."""
    lines = [
        "// generated by atm_generators.py",
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
