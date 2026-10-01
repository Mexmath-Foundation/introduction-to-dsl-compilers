# Topic 4: Execution Plan Policy

## TL;DR
An AI agent wants to run shell commands on your computer. Before anything executes, its
*execution plan* — one command, a `;` sequence, or a `|` pipeline — must pass a policy
check. You implement `evaluate_plan` in [`plan_policy.py`](plan_policy.py): parse the plan
written in a small, fully specified command language (see
[`command_spec.py`](command_spec.py)) and return one of three verdicts:

* `Decision.ALLOWED` — every command and every path is whitelisted;
* `Decision.FORBIDDEN` — at least one command or path is blacklisted;
* `Decision.CONFIRMATION_REQUIRED` — nothing is blacklisted, but at least one command or
  path is listed in no list at all, so the user must be asked.

A syntactically invalid plan raises `ValueError` instead of returning a verdict.
Run `uv run python topic-4/preview_plans.py` to see what the plans look like.

## The command language
The language is deliberately small and closed. The single source of truth is the command
table in [`command_spec.py`](command_spec.py) — that file is part of the specification:
build on top of it, do not change it.

| Command | Flags | Paths |
|---------|--------------|-----------|
| `ls` | `-l`, `-a` | exactly 1 |
| `cat` | `-n` | 1 or more |
| `cp` | `-r` | exactly 2 |
| `mv` | *(none)* | exactly 2 |
| `rm` | `-r`, `-f` | 1 or more |
| `mkdir` | `-p` | 1 or more |

### Grammar
* A **plan** is one or more command invocations joined by `;` (a sequence) or `|`
  (a pipeline).
* An **invocation** is a command name, then its flags (optional, any order, each at most
  once), then its path arguments: `rm -r -f /tmp/cache /tmp/logs`.
* All tokens — names, flags, paths, and the separators `;` and `|` — are separated by
  single spaces.

### Paths
* Paths are **absolute only**: they start with `/` and consist of segments made of
  `A-Z a-z 0-9 . _ -` characters.
* The segments `.` and `..` are **not** part of the language — a plan containing them is
  syntactically invalid. (Think about why the policy check would be unsound otherwise.)

### What makes a plan invalid
A plan that violates the language raises `ValueError`: an unknown command, a flag the
command does not accept, a wrong number of paths, a malformed or relative path, a
dangling separator. Syntax errors are a separate channel from policy verdicts — garbage
must never come back as "allowed".

## The policy
`evaluate_plan` receives the plan text and four lists: whitelisted commands, blacklisted
commands, whitelisted paths, blacklisted paths. The verdict is computed from **every**
command and **every** path in the plan, and the strictest verdict wins:

1. `FORBIDDEN` — if at least one command is blacklisted **or** at least one path is
   covered by a blacklisted entry;
2. otherwise `CONFIRMATION_REQUIRED` — if at least one command or path appears in no
   list at all;
3. otherwise `ALLOWED`.

A list entry covers a path if it is equal to it **or** is a folder the path lies under,
comparing whole segments: `/home/user/docs` covers `/home/user/docs/report.txt`, but it
does **not** cover `/home/user/docsx`.

### Examples
With these rules:

```python
allowed_commands = ["ls", "cat", "cp"]
forbidden_commands = ["rm"]
allowed_paths = ["/home/user/docs", "/tmp/work"]
forbidden_paths = ["/etc", "/var/log"]
```

| Plan | Verdict | Why |
|------|---------|-----|
| `ls -l /home/user/docs` | `ALLOWED` | command and path are whitelisted |
| `cat /home/user/docs/notes.txt \| cp /home/user/docs/a.txt /tmp/work/b.txt` | `ALLOWED` | all paths lie under whitelisted folders |
| `rm -r /tmp/work` | `FORBIDDEN` | `rm` is blacklisted — the whitelisted path does not help |
| `cat /etc/passwd` | `FORBIDDEN` | `/etc/passwd` is covered by the blacklisted `/etc` |
| `mkdir /home/user/docs/new` | `CONFIRMATION_REQUIRED` | `mkdir` is listed nowhere |
| `ls /opt/data` | `CONFIRMATION_REQUIRED` | `/opt/data` is listed nowhere |
| `mkdir /opt/data ; rm /opt/data` | `FORBIDDEN` | `rm` is blacklisted; forbidden wins over confirmation |
| `ls docs` | `ValueError` | relative paths are not part of the language |
| `cp /tmp/work` | `ValueError` | `cp` requires exactly two paths |
| `ls -z /etc` | `ValueError` | `ls` does not accept `-z` (checked before any policy) |

## Previewing generated plans
Run
```shell
uv run python topic-4/preview_plans.py
```
to print samples of the plans the test generators produce for every pool configuration —
all-whitelisted, guaranteed-blacklisted, guaranteed-unlisted, and mixed. Edit the pools in
the script while developing; it is a playground, not a test.

## Testing
You are required to **extend the test suite** in
[`test_plan_policy.py`](test_plan_policy.py). The provided tests are **intentionally
incomplete**: they cover only a few obvious properties. Passing them does **not** mean
your solution is correct or complete.

Test data generation is kept separate from the tests: all inputs are produced by the
composite strategies in [`plan_generators.py`](plan_generators.py), and the tests only
assert the property each generator guarantees by construction. Follow the same structure
in your own tests — generate data in the generators module, not inside the test functions.
You are **encouraged to add more generators and more tests** of your own, including tests
for the syntax-error space (the starter suite samples it only briefly).

## Useful links
* [Python `re` module documentation](https://docs.python.org/3/library/re.html) — the
  regular expression library available to you.
* [Regular Expression HOWTO](https://docs.python.org/3/howto/regex.html) — a gentler
  introduction than the reference page.
* [regex101](https://regex101.com/) — interactive playground for developing and debugging
  patterns (choose the Python flavor).
* [Hypothesis documentation](https://hypothesis.readthedocs.io/) — the property-based
  testing framework used by the test suite.

## Acceptance criteria
1. `evaluate_plan` is implemented in [`plan_policy.py`](plan_policy.py) and conforms to
   the semantics above: the three verdicts with the strictest-wins precedence,
   `ValueError` for invalid plans, and folder coverage by whole path segments.
2. All tests pass: `uv run pytest topic-4`.
3. The starter test suite is extended with your own tests:
   * example-based tests for edge cases;
   * further Hypothesis property-based tests covering properties the starter suite does not.
4. Code is readable, typed, and documented where behavior is not obvious.
5. The solution is submitted as a pull request from the `topic-4` branch (see the root
   [README](../README.md)).

## Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) for this task is forbidden.**
  Both the implementation and the tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult textbooks, lecture materials, and the documentation linked
  above to understand regular expressions and the parsing approach.
