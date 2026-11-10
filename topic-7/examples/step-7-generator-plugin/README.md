# Step 7: a language and a generator as a textX plugin

## What it shows
Until now every script built the metamodel itself and called a visitor by hand. textX also
has a **registry**: a *language* — a name, a file pattern and a metamodel factory — and a
*generator* — a function for one (language, target) pair. Both are announced through
Python entry points in the package's `pyproject.toml`, and once the package is installed
the `textx` command knows our language by its extension and can run the generator with no
script of ours in the loop:

```shell
uv run textx list-languages      # fsm (*.fsm)      fsm-lang[0.1.0]  The traffic-light ...
uv run textx list-generators     # fsm -> mermaid   fsm-lang[0.1.0]  Generate a Mermaid ...
uv run textx generate topic-7/examples/step-7-generator-plugin/light.fsm --target mermaid --overwrite
uv run textx check topic-7/examples/step-7-generator-plugin/light.fsm
```

This is exactly how textX's own `any -> dot` (Topic 5; lecture 10, slide 10) is wired: textX
registers its generators through the same two entry-point groups, and `list-generators`
shows them side by side with ours. Nothing in the visitor changed since step 3 — the
plugin is file handling around it.

### The two decorators
```python
@language("fsm", "*.fsm")
def fsm_language():
    return metamodel_from_file(HERE / "fsm.tx")


@generator("fsm", "mermaid")
def fsm_mermaid_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    v = MermaidVisitor()
    v.visit(model)
    ...
```
The generator's signature is fixed by textX (hence the parameters it does not use);
`model._tx_filename` is how it learns where its input came from; `--output-path` and
`--overwrite` arrive as arguments, handled by the CLI. The docstring of each function is
what `list-languages` / `list-generators` print as the description.

### The two entry-point groups
```toml
[project.entry-points.textx_languages]
fsm = "fsm_lang:fsm_language"

[project.entry-points.textx_generators]
fsm_mermaid = "fsm_lang:fsm_mermaid_generator"
```
That is the whole registration API. The grammar travels inside the package
(`fsm_lang/fsm.tx`, declared as package data) so that an installed plugin does not depend
on the repository layout.

## Files
* [`pyproject.toml`](pyproject.toml) — the package `fsm-lang` with the two entry-point groups;
* [`fsm_lang/__init__.py`](fsm_lang/__init__.py) — `fsm_language` and `fsm_mermaid_generator`;
* [`fsm_lang/mermaid.py`](fsm_lang/mermaid.py) — `Visitor`, `Emitter`, `MermaidVisitor`, `mermaid_text` from step 3, unchanged;
* [`fsm_lang/fsm.tx`](fsm_lang/fsm.tx) — step 5's grammar (with actions), packaged;
* [`light.fsm`](light.fsm) — step 5's model, to try the generator on; [`light.mmd`](light.mmd) — what it produces.

## Setup
The plugin is an editable path dependency of the course project (root `pyproject.toml`,
`[tool.uv.sources]`), so `uv sync` installs it — nothing else to do. To install the same
package into any other environment: `pip install -e topic-7/examples/step-7-generator-plugin`.

## Run
From the repository root:
```shell
uv run textx list-generators
uv run textx generate topic-7/examples/step-7-generator-plugin/light.fsm --target mermaid --overwrite
```
```
Generating mermaid target.
.../topic-7/examples/step-7-generator-plugin/light.fsm
-> .../topic-7/examples/step-7-generator-plugin/light.mmd
```
`light.mmd` is the diagram of step 3; the language was recognised from the `.fsm` extension,
the model parsed and checked by textX, and our visitor called with it. Because the language
is registered, textX's built-in generator now works on it without `--grammar` as well:
```shell
uv run textx generate topic-7/examples/step-7-generator-plugin/light.fsm --target dot --overwrite
```

For the homework: `textx generate atm.atm --target mermaid` working from a clean `uv sync`
is the one acceptance criterion that can be checked without reading the code.
