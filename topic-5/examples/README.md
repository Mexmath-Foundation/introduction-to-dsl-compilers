# textX examples: a state-machine DSL, step by step

Five incremental versions of the same grammar plus a demo of classic PEG pitfalls.
The domain is a traffic light described as a finite state machine. Each step adds
exactly one textX concept on top of the previous one, so read (and run) them in order.

Every step folder is self-contained and has its own `README.md`:
* `fsm.tx` — the grammar (the *metamodel*);
* `light.fsm` — a program written in the DSL (a *model*);
* `run.py` — what is run in the terminal to inspect the parsed model.

| Step | Adds | Concepts |
|------|------|----------|
| [`step-1-minimal-grammar`](step-1-minimal-grammar/README.md) | `Machine`, `State` | rules become classes, root object, `parent` |
| [`step-2-lists-and-optionals`](step-2-lists-and-optionals/README.md) | `events`, `initial` | `+=` with `[',']` separator, `?=`, optional groups |
| [`step-3-references`](step-3-references/README.md) | `Event`, `Transition` with `[Event]`, `[State]` | link references, semantic vs syntax errors, diagrams |
| [`step-4-lexical-elements`](step-4-lexical-elements/README.md) | `label=STRING`, `Duration` regex, `Comment` | lexical layer, match rules, comments |
| [`step-5-user-classes`](step-5-user-classes/README.md) | Python classes `State`, `Machine` with `run()` | `classes=[...]`, the model as an interpreter |
| [`step-6-peg-pitfalls`](step-6-peg-pitfalls/README.md) | four broken grammars and their fixes | ordered choice, keywords, greedy repetition, left recursion |

## Setup
[textX](https://textx.github.io/textX/) is declared in [`pyproject.toml`](../../pyproject.toml)
as `textX[cli]>=4.0,<5`, so a regular `uv sync` installs it. The `[cli]` extra is what
provides the `textx` command (`textx check`, `textx generate`) used below.
```shell
uv sync
uv run textx version      # textX 4.4.0 (or any 4.x)
```

Optional, for the diagrams in step 3: the [Graphviz](https://graphviz.org/download/)
`dot` binary (`brew install graphviz`, `sudo apt install graphviz`,
`winget install graphviz`). It is not a Python package, do not `pip install graphviz`.
textX writes the `.dot` files itself; `dot` only rasterizes them. Without it the
committed PNGs in `step-3-references/` are the fallback.

## Running a step
Every `run.py` locates its `fsm.tx` and `light.fsm` next to itself, so it can be run from
anywhere, for example from the repository root:
```shell
uv run python topic-5/examples/step-3-references/run.py
```
The scripts are also executable directly (`./topic-5/examples/step-3-references/run.py`)
once the virtual environment is activated.

The `textx` CLI takes explicit paths, so it works from the repository root as well:
```shell
cd topic-5/examples/step-3-references
uv run textx check fsm.tx                      # validate the grammar
uv run textx check light.fsm --grammar fsm.tx  # validate a program against it
```

## Visualizing a metamodel and a model
From `step-3-references/`:
```shell
uv run textx generate fsm.tx --target dot --overwrite                      # -> fsm.dot   (metamodel)
uv run textx generate light.fsm --grammar fsm.tx --target dot --overwrite  # -> light.dot (model)
dot -Tpng -O fsm.dot && dot -Tpng -O light.dot                             # -> *.dot.png
```
`*.dot` and `*.pu` files are git-ignored; the pre-rendered `fsm.dot.png` and
`light.dot.png` are committed as a fallback. A PlantUML export of the metamodel is also
available (`--target plantuml`, paste the resulting `fsm.pu` into https://www.plantuml.com/).

## A note on the files
The grammars are intentionally minimal and are not meant to be "improved": each step
deliberately adds one concept over the previous one, and the lecture notes quote the exact
outputs (including the error positions in step 3). `step-5-user-classes/fsm.tx` and
`light.fsm` are byte-identical copies of the step 4 files: the point of step 5 is that
*only the Python side* changes.
