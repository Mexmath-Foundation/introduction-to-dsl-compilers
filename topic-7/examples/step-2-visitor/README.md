# Step 2: the Visitor pattern — the book's form, and the Python form on a textX model

## What it shows
Step 1 left two loops with the same skeleton and a different body. The Visitor pattern
(Gamma, Helm, Johnson, Vlissides, *Design Patterns*, 1994, chapter 5) is the name for
separating the two: the **walk** over the structure is written once; each **operation**
is a class with one method per kind of node, and the right method is chosen by the node's
class. Two files, two forms of the same idea.

### 2a · `gof_form.py` — the textbook form, on hand-written classes
Each node class gets exactly one method, `accept(visitor)`, whose body is one line:
`return visitor.visit_State(self)`. That line is **double dispatch**: the first choice is
made by the node's class (this `accept` ran because the object is a `State`), the second
by the visitor's class (which `visit_State` runs). Two virtual calls in a row, no `if`
anywhere. `accept` knows nothing about any operation and never changes again: adding
`CountVisitor` next to `DotVisitor` touched no node class — the sentence from the book.

Why the pattern needs `accept` at all: in Java or C++ an overload `visit(State)` /
`visit(Transition)` is chosen by the argument's *static* type, so a visitor holding a
`Node` reference cannot pick the right one; the node has to supply its own type by calling
back. Python knows an object's class at run time, so the Python form can do without it —
which matters, because the textX classes are generated and we cannot add `accept` to them.

### 2b · `visitor.py` — the Python form, on the textX model
`Visitor` is the base class every output of this topic derives from. It does two things:

* **dispatch** — `visit(node)` looks up `visit_<ClassName>` with `getattr` and falls back
  to `generic_visit`. A textX object's class is named after its grammar rule, so the
  method names are the rule names: `visit_Machine`, `visit_State`, `visit_Transition`.
  This is exactly how `ast.NodeVisitor` in the standard library works;
* **the walk** — `generic_visit(node)` visits the node's children, found through the
  metamodel: `type(node)._tx_attrs` lists the attributes of the class, and the visitor
  follows the ones that are **containment** (`attr.cont`) and not base types. It never
  follows a reference: following `target` would loop on `Red -> Green -> Red`. Down the
  tree, each node once, in document order — the walk of step 1's `to_dot` and `to_c`,
  written once.

`DotVisitor` is `to_dot` from step 1 cut into three methods, one per node class, each
calling `generic_visit` where the loop used to recurse. `CountVisitor` is a second
operation: a handful of lines, and nothing else in the file changed.

`_tx_attrs` is textX-internal (the leading underscore says so); it is used here because
it is the shortest way to ask "which attributes contain children?". The public
alternative is `textx.get_children(lambda _: True, node)` — but that returns all
descendants at once, which takes the recursion out of the visitor's hands.

## Files
* [`fsm.tx`](fsm.tx), [`light.fsm`](light.fsm) — unchanged from step 1;
* [`gof_form.py`](gof_form.py) — hand-written `State` and `Transition` with `accept`; `DotVisitor` and `CountVisitor` as the book has them; the mechanism is a few lines;
* [`visitor.py`](visitor.py) — the `Visitor` base class (dispatch + walk) and the same two visitors on the real textX model.

## Run
```shell
uv run python topic-7/examples/step-2-visitor/gof_form.py
```
```
Red [shape=doublecircle];
Red -> Green [label="tick"];
2
```
```shell
uv run python topic-7/examples/step-2-visitor/visitor.py
```
```
digraph Light {
  rankdir=LR;
  node [shape=circle];
  Red [shape=doublecircle];
  Red -> Green [label="tick"];
  Green -> Yellow [label="tick"];
  Green -> Red [label="panic"];
  Yellow -> Red [label="tick"];
}
3 states, 4 transitions
```
The DOT text is byte-for-byte what step 1's `to_dot` produced (because the initial state
comes first in `light.fsm`: step 1 emits all `doublecircle` lines before any edge, the
visitor emits state by state); only the shape of the code changed. What was gained is on the lecture's slide 20: a new output is a new class, the
walk is written once, the generated classes stay untouched, and the node's class — not an
`if` ladder — selects the code.
