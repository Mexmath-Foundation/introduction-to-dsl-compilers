# Step 5: user-supplied classes

## What it shows
`fsm.tx` and `light.fsm` are **byte-identical copies** of the
[step 4](../step-4-lexical-elements/README.md) files. Only the Python side changes: instead
of letting textX generate classes for `State` and `Machine`, we supply our own and pass
them with `metamodel_from_file('fsm.tx', classes=[State, Machine])`. The model then
consists of *our* objects, so we can give them behavior: `State.next(event)` follows a
transition and `Machine.run(*events)` executes the state machine. The parsed model becomes
an interpreter.

Rules of the game:
* class names must match rule names;
* textX calls `__init__` with every grammar attribute as a keyword argument, plus `parent`
  for contained (non-root) objects. A class whose `__init__` does not accept them fails
  with `TypeError` at model construction. The explicit signature in `run.py` is the
  "class spec" shown on the slide; a `**kwargs` + `setattr` loop would also work;
* rules that are not overridden (`Transition`, `Event`) keep their generated classes;
  generated and user classes coexist in one model;
* `get_children_of_type('Transition', m)` walks the whole model and collects every
  object of a class by name, whoever defined the class.

## Files
* [`fsm.tx`](fsm.tx) — identical to step 4;
* [`light.fsm`](light.fsm) — identical to step 4;
* [`run.py`](run.py) — the `State` and `Machine` classes, and a run of the machine.

## Run
```shell
# from the repository root; the script finds its files next to itself
uv run python topic-5/examples/step-5-user-classes/run.py

# the textx CLI takes explicit paths; from inside the step folder:
cd topic-5/examples/step-5-user-classes
uv run textx check fsm.tx
uv run textx check light.fsm --grammar fsm.tx
```

Expected output:
```
<class '__main__.Machine'>
['Red', 'Green', 'Yellow', 'Yellow', 'Red']
['Green', 'Yellow', 'Red', 'Red']
```

Reading the trace: start in `Red` (the initial state), `tick` → `Green`, `tick` →
`Yellow`, `panic` has no transition in `Yellow` so the machine stays, `tick` → `Red`.
