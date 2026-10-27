# textX examples: semantic constraints, step by step

The live-coding material of the Topic 6 lecture. The domain is the same traffic-light
state machine as in [`topic-5/examples/`](../../topic-5/examples/README.md); the grammar
is the one from `step-3-references` there (step 4 restores `Duration`, step 5 wraps it in
`machine … { }` blocks). Each folder carries its own copy of the grammar, so every step
stays self-contained.

The steps follow the lecture: first the problem (what parsing does not check), then the
two tools a check is built from (a way to tell containment from reference, and a way to
walk the graph), then the hooks that make the check part of the language, and finally
the one case where resolution itself has to change.

| Step | Shows | Concepts |
|------|-------|----------|
| [`step-1-semantics-gap`](step-1-semantics-gap/README.md) | nine descriptions the grammar accepts or rejects | syntax vs semantics; what reference resolution does and does not check |
| [`step-2-containment-vs-reference`](step-2-containment-vs-reference/README.md) | two grammars that differ in one pair of brackets | `target=State` vs `target=[State]`; tree vs graph; which error each one raises |
| [`step-3-navigation`](step-3-navigation/README.md) | six questions to the traffic light, one grammar | `parent`, `get_parent_of_type`, `get_model`, `get_children_of_type`, `get_children`, `textx_isinstance`, `get_location` |
| [`step-4-processors`](step-4-processors/README.md) | the step 1 rules moved into the language | object processors (check or transform), model processors, order of calls, `TextXSemanticError` with a position |
| [`step-5-scoping`](step-5-scoping/README.md) | two machines in one file, both with a `Green` | scope providers: `RelativeName`, RREL in the grammar, `FQN` |

Step 5 goes beyond the homework; it is there because the question "how do I get local
names?" comes up as soon as a language has blocks.

## Setup
Same as Topic 5: `uv sync` installs `textX[cli]`; nothing else is needed for these steps.

## Running a step
Every script locates its grammar and programs next to itself, so it runs from anywhere,
for example from the repository root:
```shell
uv run python topic-6/examples/step-1-semantics-gap/semantics_gap.py
```
Each `README.md` quotes the expected output, including error positions. The lecture
slides quote the same positions, so the texts of the programs are not meant to be edited.
