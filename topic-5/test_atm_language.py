"""Starter test suite for Topic 5: ATM description language.

Two kinds of tests. The property-based ones use Hypothesis: all
generated data comes from the composite strategies in
``atm_generators.py``; the tests render it in the DSL, parse it with the
student's grammar and assert the property the generator guarantees by
construction. They are provided as they are and must pass. The
example-based ones parse fixed inputs, including the student's own ATM
in ``atm.atm``; you are expected to add more of those — see
topic-5/README.md.

Descriptions are parsed with the classes textX generates from the
grammar; the tests only rely on the rule and attribute names fixed in
the README.
"""

from functools import cache
from pathlib import Path

import pytest
from atm_generators import atms, atms_with_unknown_target, render
from hypothesis import given
from textx import metamodel_from_file
from textx.exceptions import TextXSemanticError, TextXSyntaxError

TOPIC = Path(__file__).parent
GRAMMAR = TOPIC / "atm.tx"
SAMPLE_ATM = TOPIC / "atm.atm"

REQUIRED_EVENTS = [
    "card_inserted",
    "pin_ok",
    "pin_wrong",
    "amount_entered",
    "cash_taken",
    "card_taken",
    "cancel",
]


@cache
def metamodel():
    return metamodel_from_file(GRAMMAR)


def load_atm(text: str):
    """Parse a description with the grammar under test."""
    return metamodel().model_from_str(text)


def load_sample():
    return load_atm(SAMPLE_ATM.read_text())


def walk(atm, events: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Follow the transitions of ``atm`` for ``events``.

    Returns the names of the states visited (starting with the initial
    one) and the ``(kind, message)`` pairs of the actions performed. An
    event without a transition in the current state is ignored. This is
    a deliberately tiny interpreter that exists only to test your ATM; a
    later topic turns it into a real one.
    """
    state = next(s for s in atm.states if s.initial)
    states, actions = [state.name], []
    for event in events:
        taken = next((t for t in state.transitions if t.event.name == event), None)
        if taken is not None:
            state = taken.target
            actions.extend((a.kind, a.message) for a in taken.actions)
        states.append(state.name)
    return states, actions


def non_show_actions(actions: list[tuple[str, str]]) -> list[str]:
    return [kind for kind, _ in actions if kind != "show"]


# Round trip: whatever the generator wrote must come back as a model
# with the same name, events, states, labels, transitions and actions,
# in the same order.
@given(atm=atms())
def test_description_round_trips(atm) -> None:
    model = load_atm(render(atm))
    assert model.name == atm.name
    assert [e.name for e in model.events] == atm.events
    assert [(s.name, s.initial, s.label) for s in model.states] == [
        (s.name, s.initial, s.label) for s in atm.states
    ]
    for state, expected in zip(model.states, atm.states, strict=True):
        assert [
            (t.event.name, t.target.name, [(a.kind, a.message) for a in t.actions])
            for t in state.transitions
        ] == [(t.event, t.target, list(t.actions)) for t in expected.transitions]


# References are objects, not names: a transition's target *is* the
# state object declared under that name, and its event *is* the
# declared event object. Containment is recorded in `parent`.
@given(atm=atms())
def test_references_resolve_to_model_objects(atm) -> None:
    model = load_atm(render(atm))
    states = {s.name: s for s in model.states}
    events = {e.name: e for e in model.events}
    for state in model.states:
        assert state.parent is model
        for t in state.transitions:
            assert t.parent is state
            assert t.target is states[t.target.name]
            assert t.event is events[t.event.name]


# A reference to an undeclared state: the text parses, but textX cannot
# resolve the reference and reports a semantic error itself.
@given(atm=atms_with_unknown_target())
def test_unknown_target_state_is_semantic_error(atm) -> None:
    with pytest.raises(TextXSemanticError):
        load_atm(render(atm))


# Syntax errors: the text does not match the grammar. A few obvious
# shapes, built on a minimal valid description; covering the rest of the
# error space is part of the assignment.
MINIMAL = "atm A\nevents e\ninitial state S {\n    on e -> S\n}\n"


def test_minimal_description_is_valid() -> None:
    model = load_atm(MINIMAL)
    assert [s.name for s in model.states] == ["S"]


@pytest.mark.parametrize(
    "bad_text",
    [
        MINIMAL.replace("on e -> S", "on e S"),  # missing arrow
        MINIMAL.replace("state S {", "state S"),  # missing braces
        MINIMAL.replace("initial state S {\n    on e -> S\n}\n", ""),  # no states at all
        MINIMAL.replace("events e\n", ""),  # no events declaration
        MINIMAL.replace("on e -> S", "on e -> S do"),  # `do` without actions
        MINIMAL.replace("on e -> S", "on e -> S do open_safe"),  # unknown action
        MINIMAL.replace("on e -> S", "on e -> S do show"),  # `show` without a message
        MINIMAL.replace("on e -> S", 'on e -> S do dispense "100"'),  # `dispense` with one
    ],
)
def test_invalid_description_is_syntax_error(bad_text: str) -> None:
    with pytest.raises(TextXSyntaxError):
        load_atm(bad_text)


# Your ATM (atm.atm) must satisfy the requirements in README.md. These
# tests know nothing about your state names: they look at the structure
# of the model, at the actions and at where the ATM ends up.
def test_sample_atm_is_valid_for_the_textx_cli() -> None:
    # The same check as `textx check atm.atm --grammar atm.tx`.
    metamodel().model_from_file(SAMPLE_ATM)


def test_sample_atm_declares_the_required_events() -> None:
    atm = load_sample()
    assert sorted(e.name for e in atm.events) == sorted(REQUIRED_EVENTS)


def test_sample_atm_has_exactly_one_initial_state_waiting_for_a_card() -> None:
    atm = load_sample()
    assert sum(1 for s in atm.states if s.initial) == 1
    initial = next(s for s in atm.states if s.initial)
    assert any(t.event.name == "card_inserted" for t in initial.transitions)


def test_sample_atm_states_are_labelled_and_reachable() -> None:
    atm = load_sample()
    assert len(atm.states) >= 4
    assert all(s.label for s in atm.states)
    initial = next(s for s in atm.states if s.initial)
    reached = {initial.name}
    frontier = [initial]
    while frontier:
        state = frontier.pop()
        for t in state.transitions:
            if t.target.name not in reached:
                reached.add(t.target.name)
                frontier.append(t.target)
    assert reached == {s.name for s in atm.states}


def test_sample_atm_happy_path_dispenses_once_and_returns_the_card() -> None:
    states, actions = walk(
        load_sample(), ["card_inserted", "pin_ok", "amount_entered", "cash_taken", "card_taken"]
    )
    assert non_show_actions(actions) == ["dispense", "eject_card"]
    assert states[-1] == states[0]


def test_sample_atm_wrong_pin_shows_a_message() -> None:
    _, before = walk(load_sample(), ["card_inserted"])
    _, after = walk(load_sample(), ["card_inserted", "pin_wrong"])
    # The actions added by the `pin_wrong` step itself include a `show`.
    assert "show" in [kind for kind, _ in after[len(before) :]]


@pytest.mark.parametrize("wrong_pins", [1, 2])
def test_sample_atm_wrong_pin_can_be_retried(wrong_pins: int) -> None:
    events = ["card_inserted", *(["pin_wrong"] * wrong_pins)]
    events += ["pin_ok", "amount_entered", "cash_taken", "card_taken"]
    states, actions = walk(load_sample(), events)
    assert non_show_actions(actions) == ["dispense", "eject_card"]
    assert states[-1] == states[0]


def test_sample_atm_retains_the_card_after_three_wrong_pins() -> None:
    states, actions = walk(load_sample(), ["card_inserted", "pin_wrong", "pin_wrong", "pin_wrong"])
    assert non_show_actions(actions) == ["retain_card"]
    assert states[-1] == states[0]


@pytest.mark.parametrize(
    "events",
    [
        ["card_inserted", "cancel", "card_taken"],
        ["card_inserted", "pin_ok", "cancel", "card_taken"],
    ],
)
def test_sample_atm_cancel_returns_the_card_without_cash(events: list[str]) -> None:
    states, actions = walk(load_sample(), events)
    assert non_show_actions(actions) == ["eject_card"]
    assert states[-1] == states[0]
