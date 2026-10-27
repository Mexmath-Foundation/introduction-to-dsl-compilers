# Step 5: scopes

## What it shows
This step is the one piece of today's material that is *not* a check we write. It
changes how reference resolution itself searches.

Topic 5: a `[State]` reference is looked up among **all** `State` objects in the file,
one global namespace per class. That is fine for one traffic light. Put two machines in
one file (the grammar is extended with `Model: machines+=Machine;` and braces around a
machine) and both may legitimately have a state `Green`; now `-> Green` inside `Light`
has two candidates and textX gives up with `name Green is not unique`. The same mechanism
as the "side effect" of step 1, seen from the other side.

What we meant is a **scope**: look for the target among the states of the machine that
contains the transition, the way a function's local variables shadow everything outside.
textX calls the lookup rule a *scope provider*. It is registered per reference attribute
and runs in the resolution step, before any processor; the checks of step 4 still come
after it and see the resolved objects.

| Need | Looks like in the DSL | textX tool | Here |
|---|---|---|---|
| one namespace for everything | `on tick -> Green` | the default, `[State]` | section 1 (fails on two machines) |
| names local to an enclosing block | `machine Light { … -> Green }` | `RelativeName('parent.parent.states')` in Python, or `[State:ID\|parent(Machine).states]` in the grammar (RREL) | sections 2–4 |
| dotted names across blocks | `on tick -> Door.Open` | `FQN: ID+['.'];`, `[State:FQN]` and the `FQN()` provider | section 5 |
| names from another file | `import "common.fsm"` | `importURI` providers | textX docs, [Scoping](https://textx.github.io/textX/scoping.html) |
| nested scopes with shadowing | `{ x … { x … } }` | RREL with `^` | textX docs, [RREL](https://textx.github.io/textX/rrel.html) |

A scope works in both directions: it finds the `Green` you meant (section 2) and refuses
the `Red` that belongs to another machine (section 3), exactly like a local variable.

For the homework the first row is all you need. If your end-of-course language has blocks
with local names, the second row is two lines in the grammar.

## Files
* [`fsm.tx`](fsm.tx) — two machines per file, default lookup;
* [`fsm_rrel.tx`](fsm_rrel.tx) — the same grammar with the lookup rule written after `|`;
* [`fsm_fqn.tx`](fsm_fqn.tx) — the same grammar with `FQN` names for targets;
* [`two_machines.fsm`](two_machines.fsm) — `Light` and `Door`, both with a `Green`;
* [`cross_machine.fsm`](cross_machine.fsm) — one change on line 8, `Door.Closed` points at
  `Red`, a state of `Light`;
* [`dotted_name.fsm`](dotted_name.fsm) — one change on line 3, `Light.Red` points at
  `Door.Open`;
* [`scoping.py`](scoping.py) — the five sections.

## Run
```shell
uv run python topic-6/examples/step-5-scoping/scoping.py
```

Expected output (the file names are abbreviated):
```
=== 1. default scope: one global namespace per class
TextXSemanticError: .../two_machines.fsm:3:38: name Green is not unique.

=== 2. RelativeName: look for the target among the states of MY machine
Light.Red -> Green (owned by Light)
Door.Closed -> Open (owned by Door)
Door keeps its own, unreferenced Green: ['Closed', 'Open', 'Green']

=== 3. with a scope, a reference across machines is an error
TextXSemanticError: .../cross_machine.fsm:8:39: Unknown object "Red" of class "State"

=== 4. the same rule written in the grammar (RREL), no Python
Light.Red -> Green (owned by Light)
Door.Closed -> Open (owned by Door)

=== 5. FQN: dotted names across machines, Door.Open
Light.Red -> Open (owned by Door)
Door.Closed -> Open (owned by Door)
```

`3:38` and `8:39` are the positions of the *references* (`Green` on line 3, `Red` on
line 8), not of any declaration: resolution is what fails.
