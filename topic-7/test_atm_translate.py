"""Starter test suite for Topic 7: translation of ATM descriptions.

The suite drives the three translations in ``atm_translate.py`` --
``to_mermaid``, ``Interpreter`` and ``to_c`` -- and the ``atm_lang`` plugin
behind ``textx generate``. Two kinds of tests, as in Topics 5 and 6:

* **example-based** tests use fixed descriptions: the Topic 5 example
  (``CITY_BANK``), a description with awkward labels, and your own
  ``atm.atm``, whose behaviour is checked through the interpreter -- the
  Topic 5 requirements, re-read as traces;
* **property-based** tests use ``well_formed_atms`` and ``event_sequences``
  from ``atm_translate_generators.py``: the test file's own small ``walk``
  over a generated ATM is the oracle, and the interpreter, the Mermaid text
  and the compiled C program must agree with it.

The C tests compile with ``cc``/``gcc`` and are skipped when no C compiler
is installed. They are provided as they are and must pass. You are expected
to add example-based tests of your own -- see "Testing" in README.md.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from atm_translate import Interpreter, load_atm, load_atm_file, to_c, to_dot, to_mermaid
from atm_translate_generators import (
    GeneratedAtm,
    event_sequences,
    render,
    well_formed_atms,
)
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

TOPIC = Path(__file__).parent
SAMPLE_ATM = TOPIC / "atm.atm"
DRIVER = TOPIC / "main.c"
CC = shutil.which("cc") or shutil.which("gcc")

# The example from "The language" in topic-5/README.md.
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

HAPPY_PATH = ["card_inserted", "pin_ok", "amount_entered", "cash_taken", "card_taken"]

# Labels and messages that the target languages must escape: a quote, a semicolon,
# a percent sign and a backslash (textX keeps the backslash as typed: two characters).
AWKWARD = """\
atm Awkward
events go
initial state A "Insert \\"card\\"; wait" {
    on go -> B do show "Say \\"stop\\" 100%% sure; a\\b"
}
state B {
    on go -> A
}
"""


# ----------------------------------------------------------------------------
# The oracle: a walk over a *generated* ATM, independent of the model objects.


def walk(atm: GeneratedAtm, names: list[str]) -> list[str]:
    """The lines ``Interpreter.run_lines`` and the C program must produce."""
    states = {s.name: s for s in atm.states}
    current = atm.initial()
    lines = [current.name]
    for name in names:
        taken = next((t for t in current.transitions if t.event == name), None)
        if taken is not None:
            for a in taken.actions:
                lines.append(f"show {a.message}" if a.kind == "show" else a.kind)
            current = states[taken.target]
        lines.append(current.name)
    return lines


# ----------------------------------------------------------------------------
# Mermaid


def test_mermaid_header_and_initial_state():
    text = to_mermaid(load_atm(CITY_BANK))
    assert text.splitlines()[0].strip() == "stateDiagram-v2"
    assert "[*] --> Idle" in text


def test_mermaid_lists_every_transition_of_city_bank():
    text = to_mermaid(load_atm(CITY_BANK))
    for line in [
        "Idle --> EnterPin : card_inserted",
        "EnterPin --> EnterPin : pin_wrong",
        "ChooseAmount --> ReturnCard : cancel",
        "ReturnCard --> Idle : card_taken",
    ]:
        assert line in text


def test_mermaid_labels_are_quoted_and_escaped():
    text = to_mermaid(load_atm(AWKWARD))
    assert 'state "Insert #quot;card#quot;#59; wait" as A' in text
    assert "B" in text  # a state without a label still appears (through its transitions)


TRANSITION_LINE = re.compile(r"^\s*(\w+) --> (\w+) : (\w+)\s*$")


@settings(deadline=None)
@given(atm=well_formed_atms())
def test_mermaid_has_one_arrow_per_transition(atm):
    text = to_mermaid(load_atm(render(atm)))
    arrows = [
        TRANSITION_LINE.match(line).groups()
        for line in text.splitlines()
        if TRANSITION_LINE.match(line)
    ]
    expected = [(s.name, t.target, t.event) for s in atm.states for t in s.transitions]
    assert sorted(arrows) == sorted(expected)
    assert f"[*] --> {atm.initial().name}" in text


# ----------------------------------------------------------------------------
# Interpreter


def test_happy_path_trace_of_city_bank():
    atm = load_atm(CITY_BANK)
    assert Interpreter(atm).run_lines(HAPPY_PATH) == [
        "Idle",
        "EnterPin",
        "ChooseAmount",
        "dispense",
        "TakeCash",
        "eject_card",
        "ReturnCard",
        "show Thank you",
        "Idle",
    ]


def test_wrong_pin_shows_a_message_and_waits():
    i = Interpreter(load_atm(CITY_BANK))
    i.step("card_inserted")
    assert i.step("pin_wrong").name == "EnterPin"
    assert i.log == ["show Wrong PIN, try again"]
    assert i.step("pin_ok").name == "ChooseAmount"


def test_undeclared_event_is_an_error_in_the_input():
    i = Interpreter(load_atm(CITY_BANK))
    with pytest.raises(ValueError):
        i.step("boom")


def test_declared_event_without_transition_is_ignored():
    i = Interpreter(load_atm(CITY_BANK))
    assert i.step("cash_taken").name == "Idle"  # Idle has no transition on cash_taken
    assert i.log == []


@settings(deadline=None)
@given(data=st.data(), atm=well_formed_atms())
def test_interpreter_agrees_with_the_oracle(data, atm):
    names = data.draw(event_sequences(atm))
    assert Interpreter(load_atm(render(atm))).run_lines(names) == walk(atm, names)


# ----------------------------------------------------------------------------
# Your ATM, through the interpreter: the Topic 5 requirements as traces.


@pytest.fixture(scope="module")
def sample():
    return load_atm_file(SAMPLE_ATM)


def test_sample_happy_path_dispenses_then_ejects_and_returns_to_initial(sample):
    lines = Interpreter(sample).run_lines(HAPPY_PATH)
    actions = [line for line in lines if line in ("dispense", "eject_card", "retain_card")]
    assert actions == ["dispense", "eject_card"]
    assert lines[-1] == lines[0]  # back in the initial state


def test_sample_wrong_pin_shows_message_and_a_correct_pin_still_dispenses(sample):
    i = Interpreter(sample)
    i.step("card_inserted")
    before = len(i.log)
    i.step("pin_wrong")
    assert any(line.startswith("show ") for line in i.log[before:])
    lines = i.run_lines(["pin_ok", "amount_entered"])
    assert "dispense" in lines


def test_sample_cancel_ejects_without_dispensing(sample):
    for prefix in (["card_inserted"], ["card_inserted", "pin_ok"]):
        lines = Interpreter(sample).run_lines([*prefix, "cancel", "card_taken"])
        assert "eject_card" in lines and "dispense" not in lines
        assert lines[-1] == lines[0]


def test_sample_three_wrong_pins_retain_the_card(sample):
    lines = Interpreter(sample).run_lines(["card_inserted", "pin_wrong", "pin_wrong", "pin_wrong"])
    assert "retain_card" in lines and "eject_card" not in lines
    assert lines[-1] == lines[0]


def test_sample_mermaid_mentions_every_state(sample):
    text = to_mermaid(sample)
    for state in sample.states:
        assert re.search(rf"\b{re.escape(state.name)}\b", text)


# ----------------------------------------------------------------------------
# C: the generated program must print what the interpreter prints.


def run_c(atm, names: list[str]) -> list[str]:
    header, source = to_c(atm)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "atm.h").write_text(header)
        (tmp / "atm.c").write_text(source)
        shutil.copy(DRIVER, tmp)  # the driver finds "atm.h" next to itself, not a stale copy
        subprocess.run([CC, "-Wall", "-o", tmp / "atm", tmp / "atm.c", tmp / "main.c"], check=True)
        return subprocess.run(
            [tmp / "atm", *names], capture_output=True, text=True, check=True
        ).stdout.splitlines()


needs_cc = pytest.mark.skipif(CC is None, reason="no C compiler (cc/gcc) on PATH")


@needs_cc
def test_c_program_prints_the_happy_path_of_city_bank():
    atm = load_atm(CITY_BANK)
    assert run_c(atm, HAPPY_PATH) == Interpreter(atm).run_lines(HAPPY_PATH)


@needs_cc
def test_c_program_escapes_messages():
    atm = load_atm(AWKWARD)
    # puts prints the text as it is; printf(message) would eat one % and the backslash
    # escaping is c_string's job: the interpreter and the C program must agree.
    assert run_c(atm, ["go"]) == ["A", 'show Say "stop" 100%% sure; a\\b', "B"]
    assert Interpreter(atm).run_lines(["go"]) == run_c(atm, ["go"])


@needs_cc
def test_c_program_runs_your_atm(sample):
    assert run_c(sample, HAPPY_PATH) == Interpreter(sample).run_lines(HAPPY_PATH)


@needs_cc
@settings(max_examples=12, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.data(), atm=well_formed_atms())
def test_c_program_agrees_with_the_oracle(data, atm):
    names = data.draw(event_sequences(atm))
    assert run_c(load_atm(render(atm)), names) == walk(atm, names)


# ----------------------------------------------------------------------------
# DOT (optional): skipped until to_dot is implemented.


def test_dot_if_implemented():
    try:
        text = to_dot(load_atm(CITY_BANK))
    except NotImplementedError:
        pytest.skip("to_dot not implemented (optional)")
    assert text.startswith("digraph")
    assert "Idle" in text and "->" in text


# ----------------------------------------------------------------------------
# The plugin: `textx generate x.atm --target mermaid` runs to_mermaid.


def textx_cli() -> str | None:
    exe = Path(sys.executable).with_name("textx")
    return str(exe) if exe.exists() else shutil.which("textx")


@pytest.mark.skipif(textx_cli() is None, reason="textx command not found")
def test_textx_generate_mermaid_matches_to_mermaid(sample):
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [
                textx_cli(),
                "generate",
                str(SAMPLE_ATM),
                "--target",
                "mermaid",
                "-o",
                tmp,
                "--overwrite",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(TOPIC)},
        )
        assert result.returncode == 0, result.stdout + result.stderr
        produced = (Path(tmp) / "atm.mmd").read_text()
    assert produced == to_mermaid(sample)
