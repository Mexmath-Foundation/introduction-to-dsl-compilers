# Step 2: containment vs reference

## What it shows
One pair of brackets in the grammar decides whether an attribute holds a **new object
defined on the spot** or a **link to an object defined elsewhere**:

| | `target=State` (containment) | `target=[State]` (reference) |
|---|---|---|
| What must stand in the text | a whole definition: `state Green { … }` | only a name: `Green` |
| What the parser does | creates a new `State` here | looks up an existing `State` by `name` |
| The target's `parent` | this transition | whoever contains the definition |
| Writing `Green` twice | two different objects | two pointers to one object |
| Writing the wrong thing | `TextXSyntaxError` | `TextXSemanticError` |

The rule for choosing: can this thing exist in more than one place? A transition belongs
to exactly one state, so `transitions*=Transition` is containment. A state is defined
once and mentioned by many transitions, so `target=[State]` is a reference. With
containment the language is a tree and a cycle `Red → Green → Red` cannot even be
written; references are what make the model a graph.

Both demo grammars use `event=ID` to stay short. The real traffic light uses
`event=[Event]`, a reference like `target`.

## Files
* [`contain_vs_ref.py`](contain_vs_ref.py) — the two grammars, built from strings, each run
  on its own text and then on the other grammar's text.

## Run
```shell
uv run python topic-6/examples/step-2-containment-vs-reference/contain_vs_ref.py
```

Expected output:
```
=== A: target=State (containment)
machine states: ['Red', 'Blue']
g1.parent.parent.name: Red
same name: True | same object: False
bare name under A: None:1:24: Expected 'state' => 'n tick -> *Green }'

=== B: target=[State] (reference)
machine states: ['Red', 'Green']
t.target is green: True
green.parent is the machine: True
the cycle closes: True
unknown name under B: None:1:24: Unknown object "Green" of class "State"
definition under B: None:1:30: Expected 'on' or '}' => ' -> state *Green { } '
```

`None` is the file name: the texts are parsed from strings. In the last error the `*`
stands before `Green`, not before `state`: `state` is a valid `ID` (Topic 5, step 6), so
it was taken as the target's name, and parsing failed on the word after it.
