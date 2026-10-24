# Step 3: link references

## What it shows
The core of the lecture. So far every attribute held a value (a string, a boolean, a
contained object). A *link reference* `[Type]` holds a pointer to an object defined
**elsewhere** in the model:

* `Event` is now a rule, so events are objects, not strings;
* `State` contains zero or more `Transition`s (`transitions*=Transition`, note `*=`);
* `Transition: 'on' event=[Event] '->' target=[State]` — `event` and `target` are
  references. textX parses an `ID`, then after parsing resolves it to the `Event` / `State`
  object whose `name` attribute matches. `t.target is m.states[1]` is `True`: it is the
  same Python object.

This also separates two kinds of errors:
* **syntax error** (`TextXSyntaxError`) — the text does not match the grammar
  (a missing `->`);
* **semantic error** (`TextXSemanticError`) — the text parses, but a reference cannot be
  resolved (a typo in a state name).

Link references resolve by an attribute literally called `name`; do not rename it.

## Files
* [`fsm.tx`](fsm.tx) — the grammar;
* [`light.fsm`](light.fsm) — three states with transitions between them;
* [`run.py`](run.py) — follows the references, then provokes both error kinds by
  patching the program text in memory;
* [`fsm.dot.png`](fsm.dot.png), [`light.dot.png`](light.dot.png) — pre-rendered diagrams
  of the metamodel and the model (see below).

## Run
```shell
# from the repository root; the script finds its files next to itself
uv run python topic-5/examples/step-3-references/run.py

# the textx CLI takes explicit paths; from inside the step folder:
cd topic-5/examples/step-3-references
uv run textx check fsm.tx
uv run textx check light.fsm --grammar fsm.tx
```

Expected output:
```
Event tick
State Green
True
Red Light
SEMANTIC: None:8:16: Unknown object "Yelow" of class "State"
SYNTAX: None:5:13: Expected '->' => '  on tick *Green } st'
```

`None` is the file name: `model_from_str` has none. The `*` in the syntax error marks
the position where parsing failed. The positions `8:16` and `5:13` depend on the exact
text of `light.fsm`; the lecture notes quote them.

## Diagrams
textX can draw both the metamodel (classes and their relations) and a concrete model:
```shell
uv run textx generate fsm.tx --target dot --overwrite                      # -> fsm.dot
uv run textx generate light.fsm --grammar fsm.tx --target dot --overwrite  # -> light.dot
dot -Tpng -O fsm.dot                                                       # -> fsm.dot.png
dot -Tpng -O light.dot                                                     # -> light.dot.png
```
The second pair of commands needs the Graphviz `dot` binary. Without it, open the `.dot`
files in any online Graphviz viewer, or look at the committed PNGs.

What to look for:
* `fsm.dot.png` — four class boxes `Machine`, `Event`, `State`, `Transition`.
  Diamond-headed edges (`states 1..*`, `transitions 0..*`, `events 1..*`) are
  **containment**; plain arrows `event` and `target` from `Transition` are **references**.
* `light.dot.png` — `Light:Machine`, the three `State` objects (`Red` with
  `initial:bool=True`), four `:Transition` objects and exactly two `Event` objects.
  All four `event` arrows converge on `tick:Event` and `panic:Event`: references share
  objects, they do not copy them.

An optional PlantUML export of the metamodel: `uv run textx generate fsm.tx --target plantuml --overwrite`
writes `fsm.pu`, which can be pasted into https://www.plantuml.com/.
