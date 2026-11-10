# Step 6: templates — text that contains code, instead of code that writes text

## What it shows
The same `light.h` and `light.c` as step 5, produced from two Jinja2 templates instead of
a visitor. A visitor is code that produces text; a template is text that contains code.
`light.c.j2` *looks like* `light.c`: a C programmer reads it as C with holes — `{{ … }}`
inserts a value, `{% for %}` repeats, `| filter` transforms. The visitor of step 5 looks
like Python that happens to print C.

Two rules carry over unchanged:

* **escaping is still the target's business** — `c_string` is registered as a Jinja
  *filter* and every model string passes through it in the template; `C` (the enum
  constant) is a filter too;
* **the model is read-only** — the template reads `m.states`, `s.transitions`,
  `a.kind` and never computes anything the model does not already hold.

One Jinja setting matters for a code generator: `StrictUndefined`. Jinja's default renders
an unknown name as empty text, which in generated code means a silently broken program;
with `StrictUndefined` a typo in the template is an error at render time.

### When which
| Output is… | Use | Because |
|---|---|---|
| mostly fixed text with model values dropped in — a C file, HTML, a config, a report | a template | the shape of the output is visible at a glance |
| computed per node — the three buffers of step 5, name mangling, reachability, anything recursive | a visitor | logic in a template is logic you cannot test |

Most real generators do both: a visitor computes, templates spell. Here both produce the
same bytes (below the first-line comment, which names the generator), and `--check`
proves it by importing step 5's `CVisitor` and comparing.

## Files
* [`fsm.tx`](fsm.tx), [`light.fsm`](light.fsm), [`main.c`](main.c) — unchanged from step 5;
* [`light.h.j2`](light.h.j2), [`light.c.j2`](light.c.j2) — the templates;
* [`generate_jinja.py`](generate_jinja.py) — the Jinja `Environment` with the two filters; `--check` compares with step 5;
* [`light.h`](light.h), [`light.c`](light.c) — rendered output, committed.

## Setup
Jinja2 is a project dependency since this step (`pyproject.toml`); `uv sync` installs it.

## Run
```shell
uv run python topic-7/examples/step-6-templates/generate_jinja.py --check
```
prints `light.c` and ends with
```
visitor == template (below the header comment): True
```
The rendered program builds and runs exactly like step 5's:
```shell
cd topic-7/examples/step-6-templates
gcc -Wall light.c main.c -o light && ./light tick panic
```
```
Red
show Go now
Green
show Say "stop" 100%
beep
Red
```
