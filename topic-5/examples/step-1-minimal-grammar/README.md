# Step 1: a minimal grammar

## What it shows
The smallest useful textX grammar: two rules, `Machine` and `State`. Every rule in a
grammar becomes a Python class in the *metamodel*, and every object parsed from a program
is an instance of one of those classes.

* `'machine' name=ID` — a string literal matches a keyword; `name=ID` stores the matched
  identifier in the attribute `name`.
* `states+=State` — one or more `State` objects, collected into the list `states`.
* The first rule is the root: `model_from_file` returns a `Machine`.
* Every contained object gets a `parent` attribute pointing at its container.

## Files
* [`fsm.tx`](fsm.tx) — the grammar;
* [`light.fsm`](light.fsm) — a program: one machine with two states;
* [`run.py`](run.py) — loads the metamodel, parses the program, prints what came out.

## Run
```shell
# from the repository root; the script finds its files next to itself
uv run python topic-5/examples/step-1-minimal-grammar/run.py

# the textx CLI takes explicit paths; from inside the step folder:
cd topic-5/examples/step-1-minimal-grammar
uv run textx check fsm.tx                      # .../fsm.tx: OK.
uv run textx check light.fsm --grammar fsm.tx  # .../light.fsm: OK.
```

Expected output (the hex address in line 3 varies):
```
Machine Light
['Red', 'Green']
<textx:fsm.State class at ...>
True
['name', 'states']
['Machine', 'State', 'ID', 'STRING', 'BOOL', 'INT', 'FLOAT', 'STRICTFLOAT', 'NUMBER', 'BASETYPE', 'OBJECT']
```

The last line lists every class in the metamodel: the two from the grammar plus textX's
built-in base types (`ID`, `STRING`, `INT`, ...).

`textx check fsm.tx` validates the grammar itself (textX's own grammar is a registered
language); `textx check light.fsm --grammar fsm.tx` validates a program against it.
