# Step 2: lists, optionals, separators, boolean assignment

## What it shows
Three more pieces of the assignment syntax, on top of [step 1](../step-1-minimal-grammar/README.md):

* `('events' events+=ID[','])?` — an optional group `( ... )?`, and a list with a
  separator: `ID[',']` means "identifiers separated by commas". The group as a whole may be
  absent; if it is, `events` is an empty list.
* `initial?='initial'` — a boolean assignment: `initial` is `True` if the keyword
  `initial` was present and `False` otherwise. Nothing is ever missing: the attribute
  always exists.

## Files
* [`fsm.tx`](fsm.tx) — the grammar;
* [`light.fsm`](light.fsm) — a program with an event list and an initial state;
* [`run.py`](run.py) — prints the events and the `(name, initial)` pairs.

## Run
```shell
# from the repository root; the script finds its files next to itself
uv run python topic-5/examples/step-2-lists-and-optionals/run.py

# the textx CLI takes explicit paths; from inside the step folder:
cd topic-5/examples/step-2-lists-and-optionals
uv run textx check fsm.tx
uv run textx check light.fsm --grammar fsm.tx
```

Expected output:
```
['tick', 'panic']
[('Red', True), ('Green', False), ('Yellow', False)]
```

Try it: delete the `events tick, panic` line from `light.fsm` and run again; the first
line becomes `[]`.
