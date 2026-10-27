# Step 1: what the grammar cannot check

## What it shows
The traffic-light grammar from Topic 5
([`step-3-references`](../../../topic-5/examples/step-3-references/README.md)) accepts
every description in group 1 below, and each one is a broken state machine. Parsing guarantees exactly one thing: the text has the right *shape* and
every reference points at an existing object. Whether the model *makes sense* is not the
grammar's business, because a PEG rule only ever looks at one place in the text, while
these rules compare different places or walk the whole graph:

| | Description | Accepted, yet |
|---|---|---|
| 1a | no `initial` state | nowhere to start; an interpreter fails on the first step |
| 1b | two `initial` states | two starts; an interpreter silently takes the first |
| 1c | two transitions on `tick` in one state | nondeterministic; the second transition is dead |
| 1d | `Green` is never a target | unreachable state; nothing fails, the light is just never green |

Note 1c: the defect sits inside one block, and the grammar still cannot see it.
`transitions*=Transition` accepts any list; comparing its elements is not something a
rule can express.

Group 2 is about the one semantic check textX *does* perform. Two states named `Green`
are rejected in 2a but accepted in 2b; the only difference is a transition `-> Green`.
textX did not check "names are unique"; it tried to resolve a reference, found two
candidates, and gave up. The error position proves it: `3:32` is the position of the
reference, not of the second declaration. Delete the reference and the error
disappears while the defect stays. A rule of the language cannot behave like that, so
this is not a rule of the language; it is a side effect, and uniqueness is still ours to
check (rule 2 of the homework).

Case 3 is a real syntax error for contrast: a different exception class, raised before
any object exists.

## Files
* [`fsm.tx`](fsm.tx) — identical to `topic-5/examples/step-3-references/fsm.tx`;
* [`semantics_gap.py`](semantics_gap.py) — the nine descriptions, parsed one after another.

## Run
```shell
uv run python topic-6/examples/step-1-semantics-gap/semantics_gap.py
```

Expected output:
```
--- 1a. no initial state
ACCEPTED: ['Red', 'Green'] initial = []

--- 1b. two initial states
ACCEPTED: ['Red', 'Green'] initial = ['Red', 'Green']

--- 1c. two transitions on the same event in one state
ACCEPTED: ['Red', 'Green'] initial = ['Red']

--- 1d. unreachable state
ACCEPTED: ['Red', 'Green'] initial = ['Red']

--- 2a. duplicate state name, referenced -> caught
TextXSemanticError: None:3:32: name Green is not unique.

--- 2b. duplicate state name, not referenced -> passes
ACCEPTED: ['Red', 'Green', 'Green'] initial = ['Red']

--- 2c. duplicate event, referenced -> caught
TextXSemanticError: None:3:24: name tick is not unique.

--- 2d. duplicate event, not referenced -> passes
ACCEPTED: ['Red'] initial = ['Red']

--- 3. syntax error, for contrast
TextXSyntaxError: None:3:29: Expected '->' => '{ on tick *Green } '
```

`None` is the file name: the descriptions are parsed from strings. This step is the
starting point of the Topic 6 lecture; the fixes (object and model processors) are the next steps.
