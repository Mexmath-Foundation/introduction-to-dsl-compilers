# Step 6: PEG pitfalls

## What it shows
textX grammars are PEGs (parsing expression grammars), and PEGs behave differently from
the context-free grammars of textbooks in a few ways that bite in practice. The script
builds each broken grammar from a string with `metamodel_from_str`, shows the error textX
raises, then shows the fix.

1. **Ordered choice.** `|` is not "any of"; it tries alternatives left to right and
   commits to the first that matches. `Op: '<' | '<='` can never match `<=`: `'<'`
   succeeds, then `=` is left over. Fix: list the longer alternative first.
2. **Keywords are not reserved.** `ID` happily matches `end`, so in
   `'begin' items*=Item 'end'` the loop eats the closing keyword as an item. Fix: a
   negative lookahead, `MyID: !Keyword ID;`.
3. **Greedy repetition does not backtrack.** `a+=ID 'last'` consumes `last` as another
   `ID` and never gives it back. Same cure as 2.
4. **Left recursion.** `Expr: Expr '+' INT | INT` is a valid-looking grammar and the
   metamodel builds, but parsing calls `Expr` from `Expr` without consuming anything and
   recurses forever (`RecursionError`). Fix: express precedence levels with repetition
   instead (`terms+=Term['+']`), the same shape as a hand-written recursive-descent
   expression parser.

## Files
* [`pitfalls.py`](pitfalls.py) — the four pairs of broken and fixed grammars.

## Run
```shell
uv run python topic-5/examples/step-6-peg-pitfalls/pitfalls.py
```

Expected output (the `grammar:` echo lines are omitted here; hex addresses vary):
```
--- 1a. ordered choice, broken
input:   '<='
TextXSyntaxError: None:1:2: Expected '<' or '<=' or EOF => '<*='

--- 1b. ordered choice, fixed (longer alternative first)
input:   '<='
OK -> <textx:Model instance at 0x...>

--- 2a. keyword eaten by ID, broken
input:   'begin a b end'
TextXSyntaxError: None:1:14: Expected ID or 'end' => 'in a b end*'

--- 2b. keyword excluded with a negative lookahead, fixed
input:   'begin a b end'
OK -> <textx:Block instance at 0x...>

--- 3. greedy repetition, broken
input:   'x y last'
TextXSyntaxError: None:1:9: Expected ID or 'last' => 'x y last*'

--- 4a. left recursion, broken
input:   '1 + 2'
RecursionError (left recursion)

--- 4b. precedence climbing, fixed
input:   '1 + 2 * (3 + 4)'
OK -> <textx:Expr instance at 0x...>
```

In 4a the `RecursionError` is caught by the script, so no traceback is printed. On some
Python builds the recursion limit is hit inside Arpeggio (the parser library under textX)
rather than in textX itself; it is the same pitfall either way.
