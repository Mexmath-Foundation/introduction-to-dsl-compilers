"""Starter test suite for Topic 6: semantic rules of the ATM language.

The suite drives ``load_atm`` / ``load_atm_file`` from ``atm_rules.py``
and expects a ``TextXSemanticError`` for every description that breaks a
rule, pointing at the culprit (see "The rules" in README.md).

Two kinds of tests, as in Topic 5. The property-based ones use the
strategies in ``atm_rule_generators.py``: ``well_formed_atms`` must be
accepted, each ``atms_with_*`` must be rejected. They are provided as
they are and must pass. The example-based ones load fixed descriptions:
two valid ones (the smallest possible and the Topic 5 example), the nine
broken ones in ``broken/`` with
the expected position of each error, and your own ``atm.atm``. You are
expected to add more of those — see "Testing" in README.md.
"""

from pathlib import Path

import pytest
from atm_rule_generators import (
    atms_with_contradictory_actions,
    atms_with_dead_end,
    atms_with_duplicate_event_name,
    atms_with_duplicate_state_name,
    atms_with_duplicate_transition,
    atms_with_no_initial_state,
    atms_with_two_initial_states,
    atms_with_unreachable_state,
    atms_with_unused_event,
    render,
    well_formed_atms,
)
from atm_rules import load_atm, load_atm_file, metamodel
from hypothesis import given
from hypothesis import strategies as st
from textx.exceptions import TextXSemanticError

TOPIC = Path(__file__).parent
BROKEN = TOPIC / "broken"
SAMPLE_ATM = TOPIC / "atm.atm"

# The smallest description that satisfies every rule.
MINIMAL = "atm A\nevents e\ninitial state S {\n    on e -> S\n}\n"

# The example from "The language" in topic-5/README.md: a valid ATM.
CITY_BANK = """\
atm CityBank

events card_inserted, pin_ok, pin_wrong, amount_entered, cash_taken, card_taken, cancel

initial state Idle "Insert your card" {
    on card_inserted -> EnterPin
}

state EnterPin "Enter your PIN" {
    on pin_ok -> ChooseAmount
    on pin_wrong -> EnterPin do show "Wrong PIN, try again"
    on cancel -> ReturnCard do eject_card
}

state ChooseAmount "Choose the amount" {
    on amount_entered -> TakeCash do dispense
    on cancel -> ReturnCard do eject_card
}

state TakeCash "Take your cash" {
    on cash_taken -> ReturnCard do eject_card
}

state ReturnCard "Take your card" {
    on card_taken -> Idle do show "Thank you"
}
"""


# ----------------------------------------------------------------------------
# Valid descriptions are accepted, and the model is the usual one.


@pytest.mark.parametrize("text", [MINIMAL, CITY_BANK], ids=["minimal", "city_bank"])
def test_valid_description_is_accepted(text: str) -> None:
    atm = load_atm(text)
    assert sum(1 for s in atm.states if s.initial) == 1


@given(atm=well_formed_atms())
def test_well_formed_description_is_accepted(atm) -> None:
    model = load_atm(render(atm))
    assert [s.name for s in model.states] == [s.name for s in atm.states]


def test_sample_atm_passes_every_rule() -> None:
    atm = load_atm_file(SAMPLE_ATM)
    assert len(atm.states) >= 4


# ----------------------------------------------------------------------------
# Broken descriptions are rejected, with the position of the culprit.
# (file in broken/, line, column, words the message must contain)

BROKEN_CASES = [
    ("two_initial_states.atm", 10, 1, ["initial"]),
    ("no_initial_state.atm", 3, 1, ["initial"]),
    ("duplicate_state_name.atm", 17, 1, ["Welcome", "twice"]),
    ("duplicate_event_name.atm", 5, 109, ["receipt_requested", "twice"]),
    ("duplicate_transition.atm", 14, 5, ["cancel"]),
    ("unreachable_state.atm", 29, 1, ["Maintenance"]),
    ("dead_end.atm", 22, 1, ["TakeCash"]),
    ("contradictory_actions.atm", 13, 5, ["cancel"]),
    ("unused_event.atm", 4, 90, ["receipt_requested"]),
]


@pytest.mark.parametrize(
    ("name", "line", "col", "words"), BROKEN_CASES, ids=[c[0] for c in BROKEN_CASES]
)
def test_broken_description_is_rejected_at_the_culprit(
    name: str, line: int, col: int, words: list[str]
) -> None:
    with pytest.raises(TextXSemanticError) as info:
        load_atm_file(BROKEN / name)
    error = info.value
    assert (error.line, error.col) == (line, col)
    for word in words:
        assert word in error.message
    assert error.filename and error.filename.endswith(name)


def test_every_broken_file_has_a_case() -> None:
    assert sorted(p.name for p in BROKEN.glob("*.atm")) == sorted(c[0] for c in BROKEN_CASES)


# The rules must live on the metamodel (object and model processors), not
# in a check that runs after parsing: parsing a broken description with
# the metamodel itself, without load_atm, is rejected as well.
def test_rules_are_registered_on_the_metamodel() -> None:
    with pytest.raises(TextXSemanticError):
        metamodel().model_from_file(str(BROKEN / "two_initial_states.atm"))


# ----------------------------------------------------------------------------
# One rule broken per strategy; load_atm must reject every one of them.
# A duplicated name also makes the duplicate unreachable or unused, so
# for rule 2 the message must show that it was rule 2 that fired.


@pytest.mark.parametrize(
    ("strategy", "word"),
    [
        (atms_with_two_initial_states, "initial"),
        (atms_with_no_initial_state, "initial"),
        (atms_with_duplicate_state_name, "twice"),
        (atms_with_duplicate_event_name, "twice"),
        (atms_with_duplicate_transition, None),
        (atms_with_unreachable_state, None),
        (atms_with_dead_end, None),
        (atms_with_contradictory_actions, None),
        (atms_with_unused_event, None),
    ],
    ids=lambda value: getattr(value, "__name__", None),
)
@given(data=st.data())
def test_broken_rule_is_rejected(strategy, word: str | None, data: st.DataObject) -> None:
    atm = data.draw(strategy())
    with pytest.raises(TextXSemanticError) as info:
        load_atm(render(atm))
    assert word is None or word in info.value.message


# A duplicated name that *is* referenced is caught by textX itself, with
# its own message; your rule owns the unreferenced case. Both are
# TextXSemanticError, so a user of the language sees no difference.
def test_referenced_duplicate_is_caught_either_way() -> None:
    text = CITY_BANK + '\nstate TakeCash "Again" {\n    on cash_taken -> ReturnCard\n}\n'
    with pytest.raises(TextXSemanticError):
        load_atm(text)
