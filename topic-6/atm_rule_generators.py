"""Hypothesis data generators for Topic 6: semantic rules of the ATM language.

This module starts as a copy of ``topic-5/atm_generators.py`` (the data
types, ``identifiers``, ``actions`` and ``render``) so that the topic is
self-contained, and adds what the rules need:

* ``well_formed_atms()`` generates a random ATM that satisfies **every**
  rule of the topic by construction: exactly one initial state, unique
  names, at most one transition per event in a state, every state
  reachable from the initial one, every state with a way out, no
  transition that both ejects and retains the card, every declared event
  used. A test parses the rendered text with ``load_atm`` and expects it
  to be accepted.
* nine ``atms_with_*`` strategies, at least one per rule, each take a
  well-formed ATM and break that rule. Where another rule is unavoidably
  broken as well (the two duplicate-name strategies), the docstring says
  so and the order of checking decides which rule is reported; see "The
  rules" in README.md. A test expects ``load_atm`` to reject the text.

As in Topic 5, the generator never needs the grammar: the expected answer
is known by construction. Students are encouraged to add more strategies
here (and more tests that use them).
"""

from typing import NamedTuple

from hypothesis import assume
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


def _replace_state(atm: GeneratedAtm, old: GeneratedState, new: GeneratedState) -> GeneratedAtm:
    return atm._replace(states=[new if s is old else s for s in atm.states])


def _fresh_name(draw: st.DrawFn, taken: list[str]) -> str:
    return draw(identifiers.filter(lambda name: name not in taken))


# ----------------------------------------------------------------------------
# One broken rule each.


@st.composite
def atms_with_two_initial_states(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 1: a second state is marked `initial`."""
    atm = draw(well_formed_atms(min_states=2))
    extra = draw(st.sampled_from([s for s in atm.states if not s.initial]))
    return _replace_state(atm, extra, extra._replace(initial=True))


@st.composite
def atms_with_no_initial_state(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 1: no state is marked `initial`."""
    atm = draw(well_formed_atms())
    return atm._replace(states=[s._replace(initial=False) for s in atm.states])


@st.composite
def atms_with_duplicate_state_name(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 2: a second state with the name of the initial state.

    textX notices a duplicated name only while resolving a reference to
    it, so the duplicated name must be one that no transition targets;
    the initial state is the only state that can be unreferenced and
    still leave the ATM well-formed. Transitions that did target it are
    pointed elsewhere first. The duplicate has a transition (not a dead
    end) and is unreachable, unavoidably: rule 2 is checked before rule
    4, so rule 2 is the one reported.
    """
    atm = draw(well_formed_atms(min_states=2))
    initial = atm.initial()
    others = [s.name for s in atm.states if s is not initial]
    states = [
        s._replace(
            transitions=[
                t._replace(target=draw(st.sampled_from(others))) if t.target == initial.name else t
                for t in s.transitions
            ]
        )
        for s in atm.states
    ]
    duplicate = GeneratedState(
        initial.name,
        False,
        "",
        [GeneratedTransition(draw(st.sampled_from(atm.events)), draw(st.sampled_from(others)), [])],
    )
    return atm._replace(states=[*states, duplicate])


@st.composite
def atms_with_duplicate_event_name(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 2: a new event declared twice.

    Neither declaration is used, so textX does not notice (its uniqueness
    check runs only when a reference is resolved). The event is also
    unused, unavoidably: rule 2 is checked before rule 7, so rule 2 is
    the one reported.
    """
    atm = draw(well_formed_atms())
    event = _fresh_name(draw, atm.events)
    return atm._replace(events=[*atm.events, event, event])


@st.composite
def atms_with_duplicate_transition(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 3: one state has two transitions on the same event."""
    atm = draw(well_formed_atms())
    state = draw(st.sampled_from(atm.states))
    event = draw(st.sampled_from([t.event for t in state.transitions]))
    target = draw(st.sampled_from([s.name for s in atm.states]))
    new_state = state._replace(
        transitions=[*state.transitions, GeneratedTransition(event, target, [])]
    )
    return _replace_state(atm, state, new_state)


@st.composite
def atms_with_unreachable_state(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 4: a new state that nothing points at (it points at itself)."""
    atm = draw(well_formed_atms())
    name = _fresh_name(draw, [s.name for s in atm.states])
    orphan = GeneratedState(
        name, False, "", [GeneratedTransition(draw(st.sampled_from(atm.events)), name, [])]
    )
    return atm._replace(states=[*atm.states, orphan])


@st.composite
def atms_with_dead_end(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 5: a new state with no transitions, reachable from an existing one.

    Emptying an existing state would also cut off whatever was reachable
    only through it (rule 4) and could leave an event unused (rule 7).
    Adding a fresh dead end instead breaks rule 5 alone: it is reached on
    an event its predecessor did not handle yet, so rules 3 and 7 hold.
    """
    atm = draw(well_formed_atms())
    name = _fresh_name(draw, [s.name for s in atm.states])
    with_free_event = [s for s in atm.states if len(s.transitions) < len(atm.events)]
    assume(with_free_event)  # every state handles every event: rare, redraw
    source = draw(st.sampled_from(with_free_event))
    handled = {t.event for t in source.transitions}
    event = draw(st.sampled_from([e for e in atm.events if e not in handled]))
    new_source = source._replace(
        transitions=[*source.transitions, GeneratedTransition(event, name, [])]
    )
    dead_end = GeneratedState(name, False, "", [])
    return _replace_state(atm, source, new_source)._replace(
        states=[*[new_source if s is source else s for s in atm.states], dead_end]
    )


@st.composite
def atms_with_contradictory_actions(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 6: one transition both ejects and retains the card."""
    atm = draw(well_formed_atms())
    state = draw(st.sampled_from(atm.states))
    transition = draw(st.sampled_from(state.transitions))
    pair = [GeneratedAction("eject_card", ""), GeneratedAction("retain_card", "")]
    if draw(st.booleans()):
        pair.reverse()
    new_transition = transition._replace(actions=[*transition.actions, *pair])
    new_state = state._replace(
        transitions=[new_transition if t is transition else t for t in state.transitions]
    )
    return _replace_state(atm, state, new_state)


@st.composite
def atms_with_unused_event(draw: st.DrawFn) -> GeneratedAtm:
    """Rule 7: an event is declared and never used."""
    atm = draw(well_formed_atms())
    return atm._replace(events=[*atm.events, _fresh_name(draw, atm.events)])


# ----------------------------------------------------------------------------
# Writing generated data in the DSL (identical to Topic 5).


def render_action(action: GeneratedAction) -> str:
    return f'show "{action.message}"' if action.kind == "show" else action.kind


def render(atm: GeneratedAtm) -> str:
    """Write a generated ATM in the DSL."""
    lines = [
        "// generated by atm_rule_generators.py",
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
