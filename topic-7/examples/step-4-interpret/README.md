# Step 4: interpret — the model is the program, the events are its input

## What it shows
The third output of step 1, done properly. `Interpreter` is **not** a visitor over the
model: nothing in it enumerates the tree. It keeps one variable, the current state, and
for each input event does one lookup in that state's transitions, performs the actions
and follows `target`. That is the walk *across* the references (lecture slide 7),
driven by data that arrives at run time — as opposed to the walk *down* the containment
tree that the visitors of steps 2–3 do at "compile time", with no input in sight.

The grammar gains actions: `on panic -> Red do show "Emergency", beep`. One rule
`Action` with a `kind` attribute, the shape the Topic 5 ATM task prescribed, so the
dispatch on it is the one the homework needs.

### Where the Visitor idea re-enters
`perform(action)` calls `getattr(self, "do_" + action.kind)` — one method per kind of
action, chosen by name. It is the move of `Visitor.visit`, with the attribute `kind`
as the key instead of the class name. With a grammar written as `Action: Show | Beep`
textX would generate a class per alternative and the key would be `type(action).__name__`
again. Two grammars, two keys, one mechanism; adding a `dispense` action is one method,
not an `elif`.

### Two decisions that belong to the language, not to Python
Both are visible in `step` and both must be written down for the user of the language:

* an event the machine never declared is an error in the **input** — `ValueError`, with
  no file position, because there is no file to point at. It is not a
  `TextXSemanticError`: the model is fine, the data is not (lecture slide 26);
* a declared event with no transition in the current state is **ignored**: the light
  stays where it is. The Topic 5 test walker does the same; a bank would log it; a strict
  machine would fail. Any of the three is acceptable in the homework, as long as the
  README says which.

### Why not `Machine.run` inside the model, as in Topic 5?
That was the Interpreter pattern (GoF): behaviour as methods of the node classes, via
`classes=[…]`. It is the other axis of the expression problem, not a mistake. Today the
same model is also drawn and translated, and a model object that remembers its own
current state would leak one consumer's run into the others. Keep the model a pure
description; put the behaviour beside it (lecture slide 29).

## Files
* [`fsm.tx`](fsm.tx) — step 3's grammar plus `('do' actions+=Action[','])?` and the `Action` rule;
* [`light.fsm`](light.fsm) — actions on two transitions;
* [`interpret.py`](interpret.py) — `Interpreter.step`, `perform`, `do_show`, `do_beep`, `run`.

## Run
```shell
uv run python topic-7/examples/step-4-interpret/interpret.py
```
```
['Red', 'Green', 'Red', 'Green', 'Yellow', 'Yellow']
["show 'Go now'", "show 'Emergency'", 'beep', "show 'Go now'"]
ValueError: unknown event 'boom'
```
The first line is the trace of `run(["tick", "panic", "tick", "tick", "panic"])`: the
last `panic` arrives in `Yellow`, which has no transition for it, so the state stays
`Yellow` — the second decision above, in action. The second line is the log the actions
wrote, in order; the tests of the homework read the ATM's log the same way. The third is
the first decision: `boom` was never declared.

Step 5 generates C from the same model and checks that the compiled program prints the
same trace and the same actions as this interpreter.
