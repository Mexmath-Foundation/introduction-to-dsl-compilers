# Step 4: lexical elements

## What it shows
The lexical layer of a textX grammar, on top of [step 3](../step-3-references/README.md):

* `(label=STRING)?` — a built-in `STRING` match: a quoted literal, stored without the
  quotes. When the optional part is missing, the attribute is `''`.
* `Duration: /\d+(ms|s|m)/ ;` — a *match rule*: a rule whose body is a single regular
  expression (or literal). It does not become a class; the matched text is stored as a
  plain string. When the optional `('after' timeout=Duration)?` group is missing, the
  attribute is `None`.
* `Comment: /\/\/.*$/ ;` — a rule with the special name `Comment` is never referenced by
  other rules; textX picks it up by name and skips whatever it matches anywhere in the
  input. Here it is a `//` line comment.

Note the asymmetry in the missing-value defaults: `''` for a built-in base type such as
`STRING`, `None` for a user-defined match rule.

## Files
* [`fsm.tx`](fsm.tx) — the grammar;
* [`light.fsm`](light.fsm) — now with labels, timeouts and comments;
* [`run.py`](run.py) — prints `name`, `label` and `timeout` of every state.

## Run
```shell
# from the repository root; the script finds its files next to itself
uv run python topic-5/examples/step-4-lexical-elements/run.py

# the textx CLI takes explicit paths; from inside the step folder:
cd topic-5/examples/step-4-lexical-elements
uv run textx check fsm.tx
uv run textx check light.fsm --grammar fsm.tx
```

Expected output:
```
Red 'Stop' '30s'
Green 'Go' '45s'
Yellow '' None
```
