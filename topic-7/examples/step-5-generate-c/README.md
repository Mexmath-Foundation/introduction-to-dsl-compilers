# Step 5: generate C — the same walk, a body that writes another language

## What it shows
`CVisitor` is `DotVisitor` of step 3 with different method bodies: every state once,
every transition once, every action once, in document order; `visit_State` writes
`case RED:`, `visit_Transition` writes `if (e == TICK) { … return GREEN; }`,
`visit_Action` writes `puts(...)`. Three things are new, and all three come from the
**target language**, not from the model:

1. **Order.** C wants every name declared before use, and the handwritten driver
   `main.c` needs a header. The model is in document order (each state with its
   transitions). One walk cannot emit in two orders, so the visitor does not emit — it
   **collects**: `header` becomes `light.h`, `decl` the top of `light.c` (name tables,
   initial state), `body` its bottom (the `step` function); the three are joined after
   the walk. Every spelling — the constant `RED`, the string `"Red"` in the table, the
   index the driver prints — is computed from the one `name` attribute, so nothing is
   typed twice and nothing can drift.
2. **Escaping, a third time.** `show "Say \"stop\" 100%"` in the model: textX's `STRING` has
   already turned `\"` into `"` (that, and `\'`, is all it unescapes — a `\\` or `\n`
   arrives as typed, two characters), so the visitor receives the *text* `Say "stop" 100%`.
   C has its own rules for spelling text, so `c_string` re-escapes it, the way
   `dot_string` did for DOT and `mermaid_text` for Mermaid. And `puts`, not `printf`: the
   message is *data*; with `printf` the `%` would be a format directive and the output
   undefined — an injection bug generated into every program.
3. **Behaviour order.** A transition visits its actions *before* emitting the `return`.
   In DOT the order of lines was cosmetic; in C it is the order of execution.

### The differential test
Two translations of one model now exist: the interpreter runs it in Python, gcc runs the C
the visitor wrote. `difftest.py` feeds both the same events and compares their output line
by line: the initial state, then for each event its actions and the state reached.
`run_lines` (interpreter) and `main.c` (driver) agree on that line format *by design* —
a shared output format is part of the test's contract, decided before either side was
written. Neither side is the oracle: a disagreement means at least one of them misreads
the model, and the first differing line says where. Its limit is honest too: a wrong model
(a transition to the wrong state) passes, because both sides faithfully execute the same
wrong model — that is what lecture 9's checks are for.

## Files
* [`fsm.tx`](fsm.tx), [`light.fsm`](light.fsm) — step 4's grammar; the panic message now contains a quote and a percent sign on purpose;
* [`generate_c.py`](generate_c.py) — `CVisitor` with three buffers, `c_string`, `C`; writes `light.h` and `light.c`;
* [`light.h`](light.h), [`light.c`](light.c) — generated; committed so the C side builds without Python;
* [`main.c`](main.c) — handwritten driver: events by name on the command line, one output line per state and per action;
* [`interpret.py`](interpret.py) — step 4's interpreter plus `run_lines`, which prints the same lines as the driver (`do_show` logs `show <message>` without quotes for the same reason);
* [`difftest.py`](difftest.py) — compiles into a temporary directory and compares.

## Run
```shell
uv run python topic-7/examples/step-5-generate-c/generate_c.py      # writes light.h, light.c, prints light.c
```
Build and run the generated program with the driver (any C compiler):
```shell
cd topic-7/examples/step-5-generate-c
gcc -Wall light.c main.c -o light
./light tick panic tick tick panic
```
```
Red
show Go now
Green
show Say "stop" 100%
beep
Red
show Go now
Green
Yellow
Yellow
```
The differential test:
```shell
uv run python topic-7/examples/step-5-generate-c/difftest.py tick panic tick tick panic
```
```
ok  Red                      Red
ok  show Go now              show Go now
ok  Green                    Green
ok  show Say "stop" 100%     show Say "stop" 100%
ok  beep                     beep
ok  Red                      Red
ok  show Go now              show Go now
ok  Green                    Green
ok  Yellow                   Yellow
ok  Yellow                   Yellow
same 10 lines
```
To see the test earn its keep, swap the two lines in `visit_Transition` so that the
`return` is emitted before the actions, and run it again:
```
ok  Red                      Red
XX  show Go now              Green
XX  Green                    Red
XX  show Say "stop" 100%     Green
XX  beep                     Yellow
XX  Red                      Yellow
DIFFERENT
```
The generated C changed state without printing the action — the order bug of point 3,
found by a test that knows nothing about C. This is the test the homework asks for.
