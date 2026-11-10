# Topic 7: Translating the ATM Language

## TL;DR
After Topics 5 and 6 your ATM description is parsed and checked. Nothing is *done* with it
yet. In this topic you write the three things the course calls translation, each as a
walk over the model your rules have already approved
([`atm_translate.py`](atm_translate.py)):

* **visualize** — `to_mermaid(atm)`: a Mermaid state diagram, pasted into your README so
  that the pull request shows the ATM as a picture;
* **interpret** — `Interpreter(atm)`: run the ATM on a list of events and log what it does;
* **generate** — `to_c(atm)`: a C program with the same behaviour, built with the provided
  [`main.c`](main.c) and compared with the interpreter by a *differential test*.

A fourth, optional: `to_dot(atm)` for Graphviz. The provided plugin
([`plugin/`](plugin/atm_lang/__init__.py)) makes `textx generate atm.atm --target mermaid`
run your code, so the last acceptance criterion needs no reading of the code at all. Run
```shell
uv run pytest topic-7
```
to see what you are up against: on the untouched template every test fails or errors,
first because the template grammar is the Topic 5 skeleton, then because every function
in `atm_translate.py` raises `NotImplementedError`. Closing that gap is the assignment.

The [`examples/`](examples/README.md) folder contains the lecture's live-coding material:
the traffic light in eight steps, from three plain loops to a visitor, the three outputs,
templates, a textX plugin and guards. Steps 2–5 are the ones this task is built on; the
ATM translations are not a copy of them, though — the ATM has labels on every state, four
kinds of actions and more states.

## Starting point: your Topic 6 files
Copy your `topic-6/atm.tx`, `topic-6/atm.atm` and `topic-6/atm_rules.py` over the files of
the same name here. Everything in this topic loads descriptions through
`atm_rules.load_atm` / `load_atm_file`, so the seven rules apply **before** any translation
sees the model: a translator may assume one initial state, unique names, one transition per
event, every state reachable — and checks nothing itself ("translation refuses nothing",
lecture 10). The interface of `atm_rules.py` is the one Topic 6 fixed; `atm_translate.py`
imports it.

## The model you translate
The rule and attribute names are those of "The model" in
[`topic-5/README.md`](../topic-5/README.md#the-model): `Atm.events`, `Atm.states`,
`State.initial`, `State.label` (`''` when absent), `State.transitions`, `Transition.event`,
`Transition.target`, `Transition.actions`, `Action.kind`, `Action.message`. Every contained
object has `parent`. The `Visitor` base class in `atm_translate.py` walks the containment
tree exactly as in the lecture; its methods are named after these rules
(`visit_Atm`, `visit_State`, `visit_Transition`, `visit_Action`).

## Mermaid
`to_mermaid(atm)` returns the text of a Mermaid `stateDiagram-v2`
([documentation](https://mermaid.js.org/syntax/stateDiagram.html)). Required shape — the
tests check these lines, not the rest:

* the first line is `stateDiagram-v2`;
* the initial state gets `[*] --> Name`;
* a state with a label gets `state "label" as Name`;
* every transition is one line `Source --> Target : event`, one per transition, no more.

A label or an event name is user text inside Mermaid syntax: a `"` ends a quoted label
(the diagram fails to parse) and a `;` ends a transition's `: description` (the rest is
silently dropped). Mermaid takes HTML-style entity codes instead, so replace both
everywhere model text goes: `;` → `#59;` and `"` → `#quot;` — **in that order**, because
`#quot;` itself ends in a semicolon. The test with the `Awkward` ATM checks exactly this.
An unescaped quote breaks the diagram in your README with an error message far from the
cause; an unescaped semicolon just loses text.

Paste the output of
```shell
uv run python topic-7/translate_atm.py topic-7/atm.atm --mermaid
```
into this README (see "Your README" below) as a fenced `mermaid` block; GitHub renders it.

## The interpreter
`Interpreter(atm)` keeps one variable, the current state, and a `log`:

| Member | Does |
|---|---|
| `step(name)` | consumes one event by name; performs the actions of the transition taken; returns the new current state (the `State` object) |
| `log` | the actions performed so far, one line each: `show <message>` (the message text, no quotes), `eject_card`, `retain_card`, `dispense` |
| `run_lines(names)` | the lines the generated C program prints for the same input: the current state's name (the initial state on a fresh interpreter), then for each event the action lines it produced and the name of the state reached |

Two decisions are part of the specification, not yours to make, because the generated C
program must behave identically and the tests compare the two:

* an event the ATM never **declared** is an error in the *input*, not in the ATM:
  `step` raises `ValueError`. It carries no file position — there is no file to point at;
* a declared event the current state has **no transition for** is ignored: the state
  stays, nothing is logged. (This is what the Topic 5 test walker did.)

Dispatch on the kind of action the way the lecture did: one method per kind, chosen by
`action.kind` — `do_show`, `do_eject_card`, … — not an `if` ladder.

## C
`to_c(atm)` returns a pair of strings, the contents of `atm.h` and `atm.c`. The handwritten
driver [`main.c`](main.c) is fixed and relies on the header declaring:

```c
enum state { S_Idle, S_EnterPin, ..., N_STATES };      /* one constant per state, in file order */
enum event { E_card_inserted, ..., N_EVENTS };          /* one per event, in file order */
extern const char *state_name[];                        /* "Idle", "EnterPin", ... */
extern const char *event_name[];                        /* "card_inserted", ... */
extern const enum state initial_state;
enum state step(enum state s, enum event e);
```
Prefix the constants (`S_`, `E_`): a state and an event may share a name, and a name may
be a C keyword. `atm.c` includes `"atm.h"`, defines the tables and `step`: a `switch` over
states, an `if` per transition that performs the actions and returns the target, `return s`
otherwise. Actions print exactly the lines the interpreter logs — `puts("show ...")`,
`puts("eject_card")` — so that the two outputs can be compared line by line. Print with
`puts`, never `printf(message)`: a message is data, not a format. Every model string that
lands in C goes through an escaping function for C strings — quotes, backslashes and
newlines; the `Awkward` test checks a message with a quote, a doubled percent sign (which
`printf` would eat) and a backslash (which textX leaves as typed, two characters).

Not everything above is enforced by a test: the enum order, `N_STATES`, the prefixes (only
when a state and an event share a name) and the `do_<kind>` dispatch are checked by
reading your code, not by running it.

The order problem of the lecture (slide 31) is yours too: the enums must be declared
before `step` uses them. Collect into buffers and join after the walk, or walk twice.

Build and run by hand:
```shell
uv run python topic-7/translate_atm.py topic-7/atm.atm --c build
cp topic-7/main.c build/ && cd build && gcc -Wall atm.c main.c -o atm
./atm card_inserted pin_ok amount_entered cash_taken card_taken
```
The tests do the same in a temporary directory (the driver is copied there, so it includes
the freshly generated `atm.h`, not one lying around) and compare with
`Interpreter.run_lines`: on the Topic 5 example, on your ATM, and on generated ATMs with
generated inputs. A C compiler (`cc` or `gcc`) must be on the `PATH`; without one those
tests are skipped — CI has one. Build into `build/`, not into `topic-7/`: `atm.h`, `atm.c`
and `atm.mmd` next to your sources are not meant to be committed.

## The plugin
[`plugin/atm_lang/__init__.py`](plugin/atm_lang/__init__.py) registers the ATM language
(by `.atm` extension, with your Topic 6 rules) and two generators that call your functions.
It is wired into the project (`uv sync` installs it); you do not change it. Once
`to_mermaid` works:
```shell
uv run textx list-generators                                    # atm -> mermaid, atm -> c
uv run textx generate topic-7/atm.atm --target mermaid --overwrite
uv run textx generate topic-7/atm.atm --target c -o build --overwrite
uv run textx check topic-7/atm.atm                              # your rules apply here too
```
The test `test_textx_generate_mermaid_matches_to_mermaid` runs the first `generate` and
compares its output with `to_mermaid`.

## Your ATM
Your own [`atm.atm`](atm.atm) from Topic 6 is what the tests draw, run and compile. The
Topic 5 requirements come back as traces through the interpreter: the happy path dispenses
exactly once, then ejects, and ends in the initial state; a wrong PIN shows a message and a
correct PIN still dispenses; `cancel` ejects without dispensing and `card_taken` returns to
the start; three wrong PINs retain the card without ejecting it and return to the initial
state. A correct Topic 5 ATM passes unchanged.

## Your README
Add a section to **this file** with your ATM: a sentence on what it does, the Mermaid
diagram as a fenced block (the output of `--mermaid`), and the trace of the happy path (the
output of `--run card_inserted pin_ok amount_entered cash_taken card_taken`). The pull
request then shows the ATM without anyone running anything.

## Testing
The starter suite in [`test_atm_translate.py`](test_atm_translate.py) has two kinds of tests.

**Example-based tests** use fixed descriptions: the Topic 5 example `CityBank` (its Mermaid
lines, its happy-path trace, a wrong PIN, an undeclared event, an ignored event), the
`Awkward` ATM with a quote, a semicolon, a percent sign and a backslash in its texts, and your own
`atm.atm` through the interpreter and the compiler. You are required to **extend these**:
at least four tests of your own ATM — the paths the starter does not take (what happens on
`cancel` in each state, on `card_taken` while no card is in, on two wrong PINs then a
correct one, …), each with the exact trace you expect — plus one test that pins down the
two specified decisions on *your* ATM.

**Property-based tests** use [Hypothesis](https://hypothesis.readthedocs.io/) with the
strategies in [`atm_translate_generators.py`](atm_translate_generators.py): `well_formed_atms()`
(a copy of Topic 6's) and `event_sequences(atm)`, a list of the ATM's events. The test file
has its own tiny `walk` over a generated ATM; it is the oracle the interpreter, the Mermaid
text and the compiled program must agree with. They are provided as they are and must pass.
New strategies are extra credit, as before: example-based tests are mandatory,
property-based ones optional. One candidate for the extra credit: a strategy that puts
`"`, `;`, `%`, `\` and a non-ASCII letter into labels and messages, and a test that the
Mermaid text, the C program and the interpreter survive it.

## Extra credit
* `to_dot(atm)` for Graphviz, with the initial state visibly marked and the labels inside
  the nodes; `test_dot_if_implemented` stops skipping once it exists. (Keep the stub if you
  do not do this: the test module imports `to_dot`.)
* A Jinja2 template for `atm.c` (`examples/step-6-templates`) that produces the same text as
  your visitor — prove it with a test.
* The guarded extension of Topic 5 (`counters`, `inc`, `reset`,
  `on pin_wrong [attempts < 2] -> EnterPin`): `examples/step-8-guards` shows the expression
  grammar and the visitors that return values. Then the three-states-for-three-attempts
  ATM collapses to one state and a counter.

## What comes next
Topic 8 is the mini-project: a small language of your own, end to end — a grammar, its
rules, at least one translation, with tests. The briefing is lecture 11. The three
lectures on textX are its toolbox; the ATM is the rehearsal.

## Useful links
* [`examples/`](examples/README.md) — the lecture's live-coding steps; steps 3, 4 and 5 are the ones closest to this task.
* [Mermaid state diagrams](https://mermaid.js.org/syntax/stateDiagram.html) — the notation `to_mermaid` produces.
* [textX: registering languages and generators](https://textx.github.io/textX/registration.html) — what `plugin/` does.
* [Hypothesis documentation](https://hypothesis.readthedocs.io/).

## Acceptance criteria
1. [`atm.tx`](atm.tx), [`atm.atm`](atm.atm) and [`atm_rules.py`](atm_rules.py) are your Topic 6 files;
   `uv run textx check topic-7/atm.atm` reports `OK`.
2. [`atm_translate.py`](atm_translate.py) implements `to_mermaid`, `Interpreter` and `to_c`
   with the shapes above; `uv run textx generate topic-7/atm.atm --target mermaid` writes
   the diagram.
3. All tests pass: `uv run pytest topic-7` (run it on the topic, not on the whole
   repository: `topic-6/` has an `atm_rules.py` of the same name, and a whole-repository
   run may import that one).
4. The starter suite is extended with your own example-based tests, as described in
   "Testing" (new property-based tests are optional).
5. This README contains your ATM's Mermaid diagram and happy-path trace ("Your README").
6. The solution is submitted as a pull request from the `topic-7` branch (see the root
   [README](../README.md)).

## Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) for this task is forbidden.**
  Both the translations and the tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult the lecture materials, the examples in this folder and the
  documentation linked above.
