# Topic 6: Semantic Rules for the ATM Language

## TL;DR
Your Topic 5 grammar decides whether an ATM description is *written* correctly. It cannot
decide whether the description *makes sense*: an ATM with two initial states, two states
of the same name, or a state nobody can reach parses without a complaint. In this topic
you add that second layer. Seven rules of the language, specified in words below, become
Python functions attached to the metamodel as **object processors** and **model
processors** ([`atm_rules.py`](atm_rules.py)), so that a broken description is rejected
inside `model_from_file` itself, with a `TextXSemanticError` that points at the culprit,
the same way textX rejects a reference to an undeclared state. Run
```shell
uv run python topic-6/check_atm.py topic-6/broken/*.atm
```
to see what you are up against: nine descriptions, each reported for one rule. On the
untouched template this fails with `Expected 'atm'` at `1:1`, because the template
grammar is the Topic 5 skeleton; after you copy your own grammar in, every broken file is
reported `OK`. That gap is the assignment.

The [`examples/`](examples/README.md) folder contains the lecture's live-coding material:
the traffic light from Topic 5 in five steps, from what a grammar cannot check to object
and model processors and scopes. Every mechanism you need is there; the ATM rules are not
a copy of the examples, though.

## Starting point: your Topic 5 files
Copy your `topic-5/atm.tx` over [`atm.tx`](atm.tx) and your `topic-5/atm.atm` over
[`atm.atm`](atm.atm). The rules below are written against the model your grammar builds
(rule and attribute names from "The model" in [`topic-5/README.md`](../topic-5/README.md#the-model)),
and the grammar itself should not need changes. The copy keeps this topic self-contained:
the tests, CI and the `topic-6` branch work with the files in this folder only.

## The rules
A description that the grammar accepts is a **valid** ATM only if it satisfies all of
these. The numbers are the numbers of the rules; the order in which they are checked is
given under "Order" below.

| # | Rule | The culprit the error points at | The message names |
|---|------|--------------------------------|-------------------|
| 1 | Exactly one state is `initial`. | the second `initial` state; with none, the `Atm` object, i.e. the `atm` keyword (line 2 when line 1 is a comment) | the word `initial` |
| 2 | State names are unique, and so are event names (a state and an event may share a name; states are checked before events). | the second declaration of the name | the name, and the word `twice` |
| 3 | A state has at most one transition per event. | the second transition on that event | the event |
| 4 | Every state is reachable from the initial state by following transitions. | the unreachable state (the first one in the file) | the state |
| 5 | Every state has at least one transition: the ATM never gets stuck. | the state | the state |
| 6 | A transition does not both `eject_card` and `retain_card`. | the transition | its event |
| 7 | Every declared event is used by at least one transition. | the event, in the `events` list | the event |

**Rule 2 and textX.** textX already rejects `-> Green` when two states are named `Green`,
with `name Green is not unique`, at the position of the *reference*. That is not a
uniqueness check; it is reference resolution finding two candidates and giving up
([`examples/step-1-semantics-gap`](examples/step-1-semantics-gap/README.md)). A duplicated
name that nothing refers to passes. Your rule owns that case, and the tests use it: an
unreferenced duplicate state (which is also unreachable: rule 2 fires first) and an
unreferenced duplicate event (which is also unused: rule 2 fires first). When the
duplicate *is* referenced, textX reports first, with its own message; both are
`TextXSemanticError`, and the user of the language sees no difference.

**Order.** Rules 3, 5 and 6 are about one object and run as object processors, object by
object in file order, before any model processor (a transition is processed before the
state that contains it, so rule 6 fires before rules 3 and 5 of the same state). Rules 1,
2, 4 and 7 are about the whole description and run as model processors, in the order of
their numbers: register them in that order. Rule 4 may then assume exactly one initial
state exists, and a description that breaks several model rules is reported for the
lowest-numbered one.

**One object processor per class.** textX keeps exactly one object processor per class,
and every call to `register_obj_processors` replaces the previous registration. Register
all object processors in one call, and give `State` one function that applies rules 3
and 5 (or a small wrapper that calls both). Registering them in two calls silently keeps
only the second; the tests then report `DID NOT RAISE` with no further hint.

## The errors
Every rejection is a `TextXSemanticError` raised from a processor, with the position of
the culprit and a message a user of the language understands:
```python
from textx import get_location
from textx.exceptions import TextXSemanticError

raise TextXSemanticError(
    f'state "{state.name}" has two transitions on "{t.event.name}"', **get_location(t)
)
```
`get_location(obj)` returns the line, column and file name of any object textX built,
including an `Event` in the `events` list and a `Transition` inside a state; pass the object
the user has to fix. The tests read `error.line`, `error.col`, `error.message` and
`error.filename`, so the position is part of the specification (the table above), the
exact wording is not, beyond the words listed in the last column. A description parsed
from a string (`load_atm`, every Hypothesis test) has `None` as its file name, so an
error prints as `None:3:5: …`.

An object processor that *checks* must return `None`: a processor that returns a value
replaces the object in the model ([`examples/step-4-processors`](examples/step-4-processors/README.md)).
Do not check by hand after `model_from_str` returns: that runs only where you remember to
call it, and anyone who parses with `metamodel()` directly gets a broken model back. The
test `test_rules_are_registered_on_the_metamodel` does exactly that with a broken
description and expects it to be rejected.

## Your module
[`atm_rules.py`](atm_rules.py) is the one file you write. Its interface is fixed, because the
tests and `check_atm.py` call it:

| Function | Does |
|----------|------|
| `metamodel()` | builds the metamodel from `atm.tx` **and registers the rules on it**; cached, so the rules are registered once |
| `load_atm(text)` | parses a description from a string: `metamodel().model_from_str(text)` |
| `load_atm_file(path)` | parses a description from a file, so that errors carry the file name |

Write one function per rule (a rule is a few lines over the model: a loop, a set, a
worklist walk over `target` links) and register them in `metamodel`, keeping in mind that
object processors are registered once, in one call. The skeleton registers nothing and
therefore accepts everything the grammar accepts.

## Your ATM
Your own [`atm.atm`](atm.atm), copied from Topic 5, must pass all seven rules:
```shell
uv run python topic-6/check_atm.py topic-6/atm.atm
```
If it does not, the description is wrong, not the rule; fix the description. The seven
requirements of Topic 5 lead to an ATM that uses every event, has no dead ends and
returns to its initial state, so a correct Topic 5 ATM needs no changes here.

## Broken descriptions
[`broken/`](broken/) holds nine descriptions, one per rule (two for rules 1 and 2). Each
starts with a comment naming the rule it is reported for and the culprit; most are the
example ATM of Topic 5 with one change. Three of them unavoidably break a second rule as
well (the comment says which), and the order of checking decides what is reported. They are the fixtures of the example-based tests, and a good
place to try your rules while writing them:
```shell
uv run python topic-6/check_atm.py topic-6/broken/*.atm
```
A complete solution prints one `ERROR` line per file in the format of `textx check`,
`file:line:col: message`, with the positions from the test table.

## Testing
The starter suite in [`test_atm_rules.py`](test_atm_rules.py) has two kinds of tests.

**Example-based tests** load fixed descriptions: two valid ones (the smallest description
that satisfies every rule, and the example ATM of Topic 5), your own `atm.atm`, and the
nine files in `broken/`, each with the expected line, column and words of the error. You
are required to **extend these**: at least one new broken description per rule, written
by you. Put each new description in `broken/` and add its row to `BROKEN_CASES`;
`test_every_broken_file_has_a_case` keeps the folder and the table in step, so a complete
submission has at least 16 rows. Cover also the cases the starter suite leaves open: a
duplicated name that *is* referenced (the suite only checks that it is rejected: where is
the error, and why there?), a state that is unreachable only because the path to it goes
through another unreachable state, several rules broken at once (which one is reported?).

**Property-based tests** use [Hypothesis](https://hypothesis.readthedocs.io/) with the
strategies in [`atm_rule_generators.py`](atm_rule_generators.py), a copy of the Topic 5
generators extended for this topic:
* `well_formed_atms()` builds a random ATM that satisfies every rule **by construction**
  (read the function: each rule is one or two lines of the construction); the test expects
  `load_atm` to accept it;
* nine `atms_with_*` strategies each take a well-formed ATM and break one rule (the two
  duplicate-name strategies unavoidably break a second one; their docstrings say which);
  the test expects `load_atm` to reject it, and for rule 2 checks that it was rule 2 that
  fired.

Run
```shell
uv run python topic-6/preview_atms.py
```
to print one generated description per strategy, with the rule it breaks.

They are provided as they are and must pass. New strategies are extra credit, as in
Topic 5: example-based tests are mandatory, property-based ones optional.

## What comes next
With the rules in place, everything downstream of `load_atm` can trust the model: an
interpreter that runs an ATM on a sequence of events, and a generator that turns a
description into another language, are the subject of the next topic. Both walk the same
graph your rules walk, and neither has to check anything.

The extension reserved in Topic 5 (`counters`, `inc`, `reset`, and guards such as
`on pin_wrong [attempts < 2] -> EnterPin`) comes with rules of its own: a guard refers to a
declared counter, and a state has at most one *unguarded* transition per event. Adding the
extension to your grammar and those two rules to `atm_rules.py` is extra credit.

## Useful links
* [textX documentation](https://textx.github.io/textX/) — in particular
  [metamodel](https://textx.github.io/textX/metamodel.html) (object and model
  processors), [model](https://textx.github.io/textX/model.html) (`get_children_of_type`,
  `get_location` and the other helpers) and
  [error handling](https://textx.github.io/textX/error_handling.html).
* [`examples/`](examples/README.md) — the lecture's live-coding steps; step 4 is the one
  closest to this task.
* [Hypothesis documentation](https://hypothesis.readthedocs.io/) — the property-based
  testing framework used by the starter suite.

## Acceptance criteria
1. [`atm.tx`](atm.tx) and [`atm.atm`](atm.atm) are your Topic 5 files;
   `uv run python topic-6/check_atm.py topic-6/atm.atm` reports `OK`.
2. [`atm_rules.py`](atm_rules.py) implements the seven rules as object and model processors
   registered in `metamodel()`, with the positions from "The rules";
   `uv run python topic-6/check_atm.py topic-6/broken/*.atm` reports one `ERROR` per file.
3. All tests pass: `uv run pytest topic-6`.
4. The starter suite is extended with your own example-based tests, as described in
   "Testing" (new property-based tests are optional for this topic).
5. The solution is submitted as a pull request from the `topic-6` branch (see the root
   [README](../README.md)).

## Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) for this task is forbidden.**
  Both the rules and the tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult the lecture materials, the examples in this folder and the
  textX documentation linked above.
