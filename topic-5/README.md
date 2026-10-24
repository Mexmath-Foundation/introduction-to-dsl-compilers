# Topic 5: An ATM Description Language in textX

## TL;DR
Design a small domain-specific language for describing how an ATM behaves, implement its
grammar with [textX](https://textx.github.io/textX/), and then describe an ATM in it. The
language is specified in words below; you turn the words into a grammar ([`atm.tx`](atm.tx))
and write a concrete ATM in the language ([`atm.atm`](atm.atm)). Run
```shell
uv run python topic-5/show_atm.py topic-5/atm.atm
```
to print the model your grammar builds from your description. On the untouched template
this fails with `Expected 'atm'` at `1:1`: the skeleton grammar does not know comments yet,
and `atm.atm` starts with one. The same goes for the other commands below; they start
working as your grammar grows.

This topic covers the language and its grammar only. The Python side (semantic rules the
grammar cannot express, and an interpreter that runs an ATM) comes in later topics and
builds on what you submit here.

The [`examples/`](examples/README.md) folder contains the lecture's live-coding material: a
traffic-light state machine built in six steps. Your ATM is a state machine too, so the
examples show every textX mechanism you need. The ATM language is not a copy of the
examples, though: read the specification carefully.

## The language
An ATM description is a text file (`.atm`). It declares a name, the events the ATM reacts
to, and the states it can be in. Every state lists the transitions that lead out of it,
and every transition may perform actions. This is a description of a **valid** ATM:
```
// A city bank ATM: one withdrawal per session.
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
```

### Lexical elements
* **Identifiers** (`ID`): the names of the ATM, its events and its states. textX's built-in
  `ID` is what you want.
* **Strings** (`STRING`): double-quoted text, used for state labels and `show` messages.
  Use textX's built-in `STRING`; that it also accepts single quotes is fine.
* **Comments**: from `//` to the end of the line, allowed anywhere whitespace is.
* **Keywords**: `atm`, `events`, `initial`, `state`, `on`, `do`, and the four action
  names. A misspelled or unknown action (`open_safe`) is therefore a syntax error. The words
  `counters`, `inc` and `reset` are reserved for a later extension of the language. Do not
  use any keyword as the name of an event or a state; this is a rule for the author of a
  description, your grammar is not required to reject it. Whitespace and line breaks between
  tokens do not matter.

### Structure
* **ATM**: the keyword `atm` and a name, then the events declaration, then one or more
  states, in this order.
* **Events**: the keyword `events` followed by one or more event names separated by
  commas. Every event the ATM reacts to must be declared here.
* **State**: the keyword `state`, a name, an optional label (a string), and a block in
  braces holding zero or more transitions. The keyword `initial` before `state` marks the
  state the ATM starts in.
* **Transition**: `on`, an event name, `->`, a target state name, and optionally `do`
  followed by one or more actions separated by commas.
* **Action**: one of
  * `eject_card` — return the card to the customer;
  * `retain_card` — keep the card;
  * `dispense` — pay out the requested amount;
  * `show "message"` — display a message. `show` takes exactly one message; the other
    actions take none.

The event in a transition and the target state are **references**: they must name a
declared event and a declared state, and in the model they are the corresponding `Event`
and `State` objects, not strings (see [`examples/step-3-references`](examples/step-3-references/README.md)).
A transition that names an undeclared event or state is rejected by textX itself with
`TextXSemanticError`; you get this check for free.

The grammar also decides how many arguments an action takes: `show` without a message, or
`dispense "100"`, is a syntax error.

## The model
The tests parse descriptions with your grammar and inspect the objects textX builds from
it, so the rule names and their attribute names are part of the specification:

| Rule | Attributes |
|------|------------|
| `Atm` | `name`; `events`, a list of `Event`; `states`, a list of `State` in the order written |
| `Event` | `name` |
| `State` | `name`; `initial`, a boolean; `label`, a string, `''` when absent; `transitions`, a list of `Transition` in the order written |
| `Transition` | `event`, the `Event` object; `target`, the `State` object; `actions`, a list of `Action`, possibly empty |
| `Action` | `kind`, one of `eject_card`, `retain_card`, `dispense`, `show`; `message`, the text shown by `show`, `''` for the others |

`name` must stay `name`: link references resolve by it. Every contained object also has
the `parent` attribute textX adds (see [`examples/step-1-minimal-grammar`](examples/step-1-minimal-grammar/README.md)).

One hint about `Action`. The tests read `action.kind` and `action.message`, so every
action must be an object of the single rule `Action`. A rule made of alternatives that are
themselves rules (`Action: Show | Eject | ...`) produces several classes without those
attributes and breaks the tests. Write one rule and assign `kind` in each alternative;
textX allows assigning the same attribute in several alternatives of one rule:
```
Action:
    kind='show' message=STRING
  | kind='eject_card' | kind='retain_card' | kind='dispense'
;
```

## Your ATM
Describe an ATM in [`atm.atm`](atm.atm). The state names and labels are yours to choose; the
tests only look at the events, the actions and where the ATM ends up when they follow the
transitions. The example ATM above is a starting point, not a solution: requirement 7 is
something it does not do. Your ATM must:
1. declare exactly these events: `card_inserted`, `pin_ok`, `pin_wrong`, `amount_entered`,
   `cash_taken`, `card_taken`, `cancel`;
2. have exactly one `initial` state, with a transition on `card_inserted`;
3. on the happy path `card_inserted, pin_ok, amount_entered, cash_taken, card_taken`
   perform `dispense` exactly once and then `eject_card` exactly once, and end up in its
   initial state;
4. on `pin_wrong` show a message (on that very transition) and keep waiting for the PIN,
   so that a correct PIN still leads to a withdrawal;
5. on `cancel` while waiting for the PIN or for the amount, eject the card without
   dispensing anything; after `card_taken` it is ready for the next customer;
6. have at least four states, a label on every state, and no state that cannot be reached
   from the initial state by following transitions;
7. after three wrong PINs in a row, retain the card (`retain_card`) instead of ejecting it,
   and return to the initial state. The language has no counters yet, so count with states.

The tests follow your transitions with a deliberately tiny walker (`walk` in the test
file): an event the current state has no transition for is ignored. Validate your ATM from
the command line as well (the `textx` command takes explicit paths, so it runs from the
repository root like everything else):
```shell
uv run textx check topic-5/atm.tx
uv run textx check topic-5/atm.atm --grammar topic-5/atm.tx
```

## Previewing generated descriptions
Run
```shell
uv run python topic-5/preview_atms.py
```
to print samples of the descriptions the test generators produce: random names, labels,
states with and without transitions, actions with and without arguments. This is what
your grammar will be tested against.

## Testing
The starter suite in [`test_atm_language.py`](test_atm_language.py) has two kinds of tests.

**Example-based tests** parse fixed inputs: a minimal valid description, a few syntax
errors, and your own ATM. You are required to **extend these**: add example-based tests for
more syntax errors (a missing `}`, a label after the brace, a comma missing in the events
list), for the lexical layer (comments in unusual places, unusual whitespace) and for
anything your ATM does that the starter suite does not check. Note that the error tests
pass on the empty skeleton, since a grammar that accepts nothing rejects everything; they
only mean something once the valid-description tests pass too.

**Property-based tests** use [Hypothesis](https://hypothesis.readthedocs.io/). They are
provided as they are; you do not have to write new ones. They must pass, so it is worth
understanding what they do:
* a strategy in [`atm_generators.py`](atm_generators.py) builds a random valid ATM as plain
  Python data (`GeneratedAtm`, with its events, states, transitions and actions);
* `render` writes that data in the DSL;
* the test parses the text with *your* grammar and compares the model with the data it
  was rendered from, so the expected answer is known by construction;
* `atms_with_unknown_target` takes a valid ATM and points one transition at an undeclared
  state, so a test can assert that textX rejects it.

Adding your own strategies is extra credit. This relaxes the rule in the root README: for
this topic, new Hypothesis tests are optional, example-based tests are mandatory.

## What comes next
Later topics continue with this language and your grammar:
* semantic rules the grammar cannot express: exactly one `initial` state, unique names,
  at most one transition per event in a state;
* Python classes for the model and an interpreter that runs an ATM on a sequence of
  events;
* an extension with counters and guards, so that an ATM can retain the card after three
  wrong PINs.

The generators module already contains strategies for these (`atms_with_two_initial_states`,
`atms_with_duplicate_transition`, `simulations`); they are not used by the Topic 5 tests.

## Useful links
* [textX documentation](https://textx.github.io/textX/) — in particular the pages on
  [grammar](https://textx.github.io/textX/grammar/) and
  [metamodel](https://textx.github.io/textX/metamodel/).
* [`examples/`](examples/README.md) — the lecture's live-coding steps.
* [Hypothesis documentation](https://hypothesis.readthedocs.io/) — the property-based
  testing framework used by the starter suite.

## Acceptance criteria
1. [`atm.tx`](atm.tx) implements the language above, with the rule and attribute names from
   "The model", and `uv run textx check topic-5/atm.tx` reports `OK`.
2. [`atm.atm`](atm.atm) describes your ATM and satisfies the requirements in "Your ATM";
   `uv run textx check topic-5/atm.atm --grammar topic-5/atm.tx` reports `OK`.
3. All tests pass: `uv run pytest topic-5`.
4. The starter suite is extended with your own example-based tests, as described in
   "Testing" (new property-based tests are optional for this topic).
5. The solution is submitted as a pull request from the `topic-5` branch (see the root
   [README](../README.md)).

## Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) for this task is forbidden.**
  Both the grammar and the tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult the lecture materials, the examples in this folder and the
  textX documentation linked above.
