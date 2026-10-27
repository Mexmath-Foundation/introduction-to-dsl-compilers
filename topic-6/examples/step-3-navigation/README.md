# Step 3: navigating the model

## What it shows
Every semantic rule is a question to the whole graph, and the graph has exactly three
kinds of edge:

| Direction | What it is | How to walk it |
|---|---|---|
| Down · containment | attributes from assignments: lists and nested objects | `m.states`, `s.transitions` |
| Up · `parent` | who contains me; set by textX on every nested object | `t.parent`, `get_parent_of_type('Machine', t)`, `get_model(t)`, `get_metamodel(t)` |
| Across · references | `[State]`, `[Event]`: a link to an object elsewhere | `t.target`, `t.event` |

What the model does **not** have: reverse references (`Red` has no list of "who points
at me") and an "all objects of a class" attribute. Any question of that shape is a
traversal, and textX provides helpers for it:

* `get_children_of_type('Transition', m)`: every object of a class, at any depth;
* `get_children(predicate, m)`: every object matching a test;
* `textx_isinstance(o, mm['State'])`: "is `o` a State?", also for abstract rules.

The helpers walk containment edges only, never references, so they terminate on a
cyclic graph and return objects in document order.

The script first walks one edge of each kind, then answers the six questions of the
lecture table on the Topic 5 traffic light plus one extra state, `Blue`, that nothing
points at. The last section, `get_location`, is not navigation but lives next to it: it is what turns "something is wrong" into "line 14 is wrong" when a
rule raises an error (step 4).

## Files
* [`fsm.tx`](fsm.tx) — identical to `topic-5/examples/step-3-references/fsm.tx`;
* [`light.fsm`](light.fsm) — the Topic 5 traffic light with `state Blue { }` added on line 14;
* [`navigation.py`](navigation.py) — the three edges, the six questions, `get_location`.

## Run
```shell
uv run python topic-6/examples/step-3-navigation/navigation.py
```

Expected output (the file name in the last line is abbreviated):
```
--- down: containment attributes
['Red', 'Green', 'Yellow', 'Blue']
[('tick', 'Yellow'), ('panic', 'Red')]
--- up: parent, and the helpers that climb for you
Green Light
Light
True True
--- across: a reference is the object itself
True
--- every transition in the machine, wherever it is
4 [('Red', 'tick', 'Green'), ('Green', 'tick', 'Yellow'), ('Green', 'panic', 'Red'), ('Yellow', 'tick', 'Red')]
--- who leads into Red: the reverse of a reference
['Green', 'Yellow']
--- states with no way out (dead ends): a predicate
['Blue']
--- unreachable states: follow target from the initial state
['Blue']
--- events nobody uses
[]
--- where an object is in the file
{'line': 14, 'col': 1, 'nchar': 14, 'filename': '.../light.fsm'}
```
