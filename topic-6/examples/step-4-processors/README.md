# Step 4: object processors and model processors

## What it shows
The rules of step 1 ("exactly one initial state", "one transition per event", "every state
reachable") are each a few lines of Python over the model. The question is where that
Python lives. Checking by hand after `model_from_str` works, but runs only where you
remember to call it and loses the position in the file. textX offers two hooks that run
*inside* `model_from_file`, so the rules become part of the language:

| | Object processor | Model processor |
|---|---|---|
| Registered | per class: `mm.register_obj_processors({'State': fn})` | per metamodel: `mm.register_model_processor(fn)` |
| Called | once per object, depth-first, children before their parent | once per model, after everything else |
| Signature | `fn(obj)`; `fn(text)` for a match rule | `fn(model, metamodel)` |
| Return value | not `None` → **replaces** the object; for a match rule, stored as is¹ | ignored |
| Good for | a rule about **one** object; converting a value | a rule about the **set** of objects |

¹ A processor on a common rule may return nothing and the object stays. A processor on a
match rule receives the matched string and whatever it returns, `None` included, is what
ends up in the model, so it must always return the value; it cannot be check-only.

The script has five sections, each on a fresh metamodel:

0. **Order of calls.** One logging processor per class. The log shows that references are
   already resolved when an object processor runs (`t.target` is a `State`, not a name),
   that children are processed before their parent, and that the model processor comes
   last. A *referenced* object is processed at its own place in the tree, not when the
   reference is met: `Transition -> <State:Green>` is logged before `State Green`, so do
   not read processor-added attributes across a reference. The full order inside `model_from_file`: parse → create objects and set `parent`
   → resolve references → user-class `__init__` → object processors → model processors.
   The exception is a processor on a match rule such as `Duration`, which runs during
   parsing on the matched string.
1. **A processor as a transformer.** `duration_to_seconds` returns a number, so `'30s'`
   becomes `30` in the model. In Topic 5 we left `Duration` as a string and said "later";
   this is later.
2. **A processor as a check.** `one_transition_per_event` on `State` raises
   `TextXSemanticError(msg, **get_location(t))`. The position is the second `on tick`,
   line 5, because that is where the fix goes. Same exception class and format as textX's
   own errors.
3. **Model processors.** `exactly_one_initial` and `all_states_reachable` need the whole
   graph. Registration order is execution order: reachability may assume a start state
   exists because the initial-state check runs first.
4. **One metamodel, many models.** Everything registered once; every model parsed with
   that metamodel is converted and checked. This is the shape `atm_rules.metamodel()` takes in
   the homework.

A processor that checks returns nothing; a processor that converts returns the new value.
Keep the two in separate functions.

## Files
* [`fsm.tx`](fsm.tx) — the Topic 5 grammar with `('after' timeout=Duration)?` restored
  from `step-4-lexical-elements`, so there is a match rule to transform;
* [`light.fsm`](light.fsm) — a two-state light with `after 30s`;
* [`processors.py`](processors.py) — the four processors and the five sections.

## Run
```shell
uv run python topic-6/examples/step-4-processors/processors.py
```

Expected output:
```
=== 0. when is each processor called?
obj Event tick
obj Event panic
obj Transition -> <State:Green>
obj State Red
obj Transition -> <State:Red>
obj Transition -> <State:Red>
obj State Green
obj Machine Light
MODEL processor

=== 1. an object processor that returns a value replaces the value

--- '30s' is stored as 30
ACCEPTED [('Red', 30), ('Green', None)]

=== 2. an object processor that raises: a local check with a position

--- good model passes
ACCEPTED [('Red', '30s'), ('Green', None)]

--- duplicate transition is rejected, pointing at line 5
TextXSemanticError: None:5:5: state "Red" has two transitions on "tick"

=== 3. model processors: whole-graph rules

--- good model passes
ACCEPTED [('Red', '30s'), ('Green', None)]

--- two initial states
TextXSemanticError: None:1:40: expected exactly one initial state, found 2

--- no initial state
TextXSemanticError: None:1:1: expected exactly one initial state, found 0

--- unreachable state: A points at itself, B at nothing
TextXSemanticError: None:4:1: state "B" is unreachable

=== 4. one metamodel, many models

--- model 1: light.fsm
ACCEPTED [('Red', 30), ('Green', None)]

--- model 2: a one-liner
ACCEPTED [('A', 120)]
```

In sections 2 and 3 `timeout` is still the string `'30s'`: those metamodels have no
`Duration` processor. `None` is the file name, because the texts are parsed from strings; `light.fsm` is read
into a string too, so that the same `try_parse` helper serves every case.

Unique state and event names (rule 2 of the homework) has the same shape as section 3
and is deliberately not here: it is yours to write.
