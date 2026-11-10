# textX examples: translation, step by step

The live-coding material of the Topic 7 lecture (lecture 10). The domain is the traffic
light of Topics 5 and 6; the grammar is Topic 5's (`step-3-references` in steps 1–2, `step-4-lexical-elements`
with labels from step 3 on), which steps 4 and 8 extend (actions, then guards). Each folder carries its own copy of the grammar and the
model, so every step stays self-contained and runnable on its own.

The steps follow the lecture: first the three things a model is turned into, written as
plain loops; then the pattern that separates the walk from the operation; then the three
outputs for real, each teaching something about its target language; then the two tools
that make a generator a product (templates, the `textx` command); and finally the case
where the pattern earns its keep, recursion.

| Step | Shows | Concepts |
|------|-------|----------|
| [`step-1-three-loops`](step-1-three-loops/README.md) | DOT, a run, and C from one model, as three loops | down the tree vs across the references; compile time vs run time; what repeats |
| [`step-2-visitor`](step-2-visitor/README.md) | the Visitor pattern in the book's form and in Python on textX classes | `accept` and double dispatch; `getattr` dispatch on the rule name; `generic_visit` over containment attributes |
| [`step-3-visualize`](step-3-visualize/README.md) | `DotVisitor` and `MermaidVisitor` on the light with labels | one walk, two target languages; escaping as the target's lexical layer |
| [`step-4-interpret`](step-4-interpret/README.md) | an external `Interpreter` with actions | the walk across; dispatch on `action.kind`; errors in the input vs errors in the program; the pure model |
| [`step-5-generate-c`](step-5-generate-c/README.md) | `CVisitor`, a handwritten driver, and `difftest.py` | declaration order (three buffers); `c_string` and `puts`; the differential test |
| [`step-6-templates`](step-6-templates/README.md) | the same C from Jinja2 templates | text that contains code; filters for escaping; when a template, when a visitor |
| [`step-7-generator-plugin`](step-7-generator-plugin/README.md) | the language and its Mermaid generator as a textX plugin | `@language`, `@generator`, entry points; `textx generate x.fsm --target mermaid` |
| [`step-8-guards`](step-8-guards/README.md) | guards with an expression grammar; `ExprToC`, `ExprEval`, `VarCollector` | precedence levels as rules; visitors that return values; three grammar traps |

Steps 6–8 go beyond the homework; they are there because the questions "isn't a template
shorter?", "how do I make `textx generate` run my generator?" and "what about expressions?"
come up as soon as a generator leaves the classroom.

## Setup
`uv sync` installs everything: `textX[cli]`, Jinja2 (step 6) and the `fsm-lang` plugin of
step 7, which is an editable path dependency of this project. The C steps (1, 5, 6, 8) need
a C compiler (`gcc` or `cc`); step 3's renderings need Graphviz (`dot`) and the Mermaid CLI
(`mmdc`), both optional — the PNGs are committed.

## Running a step
Every script locates its grammar and model next to itself, so it runs from anywhere,
for example from the repository root:
```shell
uv run python topic-7/examples/step-5-generate-c/difftest.py tick panic tick
```
Each `README.md` quotes the expected output. The lecture slides quote the same code and
output, so the texts of the models are not meant to be edited.
