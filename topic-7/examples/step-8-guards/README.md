# Step 8: guards — recursion, and visitors that return values

## What it shows
A transition may now carry a guard: `on tick [count < 3 or night == 0] -> Green`. The
guard is an expression over variables that are supplied from *outside* the model, at run
time. Three things change, one per file:

1. **The grammar gets an expression sub-language** (`fsm.tx`): one rule per precedence
   level, lowest first — `Or`, `And`, `Not`, `Cmp`, `Sum`, `Term`, `Factor` — every level
   of the same shape, a list of operands with the operators between them. textX creates
   an object for every level it passes through, so a bare `3` is
   `Or(And(Cmp(Sum(Term(Int)))))`: five one-operand nodes. `shape.py` prints the tree of
   each guard.
2. **The visitors return values** (`expr.py`). Until now the visitors emitted lines and
   returned nothing; the tree was four levels deep and fixed. An expression tree has
   arbitrary depth, and the natural visitor over it builds a value for each node *from
   the values of its children*: `self.visit(o)` inside a method is the recursion.
   Nothing in the base class changed — `visit` always returned whatever the method
   returned. Same tree, three folds: `ExprToC` → the expression spelled in C,
   `ExprEval(env)` → its value, `VarCollector` → the set of variable names.
3. **Both translations use them** (`interpret.py`, `generate_c.py`). The interpreter grows
   by one method: a transition is taken when its event matches *and* `holds(guard)`;
   transitions are tried in document order, so `on tick [..] -> Green` followed by
   `on tick -> Red` reads as if/else. The generator grows by a walk: `VarCollector`
   first, because C must declare `count` and `night` before `step` can mention them —
   step 5's order problem, now across two visitors — then `CVisitor`, which spells each
   guard with `ExprToC` as an extra conjunct: `if (e == TICK && ((count < 3) || (night == 0)))`.

### Decisions written down
* `ExprToC` parenthesises every compound sub-expression, so C's precedence table is
  never trusted.
* `ExprEval` uses `any`/`all`, which short-circuit like `||`/`&&`, except on a one-operand
  node — `(count + 1)` is an `Or` with one operand, and its *value* must pass through, not
  a bool; `/` is integer division as in C.
* Comparisons chain **left to right in both translations**: `a < b < c` is `(a < b) < c`
  — C's reading, not Python's. One semantics had to be chosen so that the two translations
  agree with each other; it is this one, and it is stated here.
* An unknown variable (a typo in a guard) is a `KeyError` in the interpreter; in C it is
  silently a new variable initialised to 0, because `VarCollector` declares whatever the
  guards mention — the two translations disagree on it. Catching it belongs to lecture 9
  (a check that every `Var` names a declared variable), not to the translators.

### Three grammar traps, all met while writing this step
* **`+=` means one or more.** In textX `operands+=Sum` matches `Sum` *one or more times*,
  so a rule written `operands+=Sum (ops+=CmpOp operands+=Sum)*` accepts `count 3` (two
  operands, no operator) and, worse, reads `3 or night` as three operands with `or` as a
  variable. The list is collected by **repeating a plain `=` assignment** instead —
  `operands=Sum (ops=CmpOp operands=Sum)*`: textX turns an attribute that is assigned more
  than once into a list (the "multiple assignment" rule of its grammar documentation).
  `shape.py` shows the lists it produces.
* **Keywords are IDs.** `ID` matches `or`, `and`, `not`; textX does not reserve keywords.
  With the `=` shape the parser never tries `Var` where a keyword stands, but `[or < 3]`
  would still parse with a variable named `or`. `Var: !Keyword name=ID` rejects it.
* **Do not mix an assignment with a bare rule reference in one rule.**
  `Not: 'not' operand=Not | Cmp;` makes textX create a `Not` object with `operand=None`
  for every plain comparison and drop the `Cmp`. Write an abstract rule and a concrete one:
  `Not: NotExpr | Cmp;` and `NotExpr: 'not' operand=Not;`.

## Files
* [`fsm.tx`](fsm.tx) — step 5's grammar plus `('[' guard=Expr ']')?` and the expression rules;
* [`light.fsm`](light.fsm) — two guarded transitions; variables `count` and `night`;
* [`expr.py`](expr.py) — `Visitor`, `ExprToC`, `ExprEval`, `VarCollector`;
* [`shape.py`](shape.py) — prints each guard's parse tree;
* [`interpret.py`](interpret.py) — step 5's interpreter plus `holds`; takes an `env` dict;
* [`generate_c.py`](generate_c.py) — step 5's generator plus variables and guards; generates `set_var` for the driver;
* [`main.c`](main.c) — the driver; `name=value` arguments set a variable before the next event;
* [`light.h`](light.h), [`light.c`](light.c) — generated, committed;
* [`difftest.py`](difftest.py) — the differential test with variables.

## Run
```shell
uv run python topic-7/examples/step-8-guards/shape.py          # the parse tree of each guard
uv run python topic-7/examples/step-8-guards/interpret.py      # two runs, two environments
uv run python topic-7/examples/step-8-guards/generate_c.py     # writes light.h, light.c
```
`interpret.py`:
```
{'count': 1, 'night': 0} ['Red', 'show Go now', 'Green', 'Yellow', 'Yellow', 'Red']
{'count': 5, 'night': 1} ['Red', 'show Closed for the night', 'Red', 'show Closed for the night', 'Red', 'Red', 'show Closed for the night', 'Red']
```
The generated C and the driver:
```shell
cd topic-7/examples/step-8-guards
gcc -Wall light.c main.c -o light
./light count=5 night=1 tick
```
```
Red
show Closed for the night
Red
```
The differential test (default scenario: three environments, both guards exercised in
both directions):
```shell
uv run python topic-7/examples/step-8-guards/difftest.py
```
```
ok  Red                      Red
ok  show Go now              show Go now
ok  Green                    Green
ok  show Say "stop" 100%     show Say "stop" 100%
ok  beep                     beep
ok  Red                      Red
ok  show Closed for the night show Closed for the night
ok  Red                      Red
ok  show Go now              show Go now
ok  Green                    Green
ok  Green                    Green
ok  Yellow                   Yellow
same 12 lines
```
The eleventh line is the guard blocking a `panic` in `Green` under `count=5 night=1`: the
state stays `Green`.

To see why `ExprToC` parenthesises everything, remove the parentheses in `_chain` and run
the test again. gcc warns twice and the test fails at line 4. Green's guard now reads
`e == PANIC && !night == 1 && count * 2 >= 10`, which C binds as `(!night) == 1`, so the
panic is refused and the C program prints `Green` where the interpreter prints the
action; and Red's `e == TICK && count < 3 || night == 0` would accept a `panic` whenever
`night == 0`. Each expression was correct on its own and broke when pasted into a larger
one — exactly what the parentheses are for.
