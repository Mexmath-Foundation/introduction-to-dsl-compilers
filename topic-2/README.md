# Topic 2: Knuth–Morris–Pratt Substring Search

## Task
Implement the **Knuth–Morris–Pratt (KMP) algorithm** for searching a substring in a string.

The function to implement is `find_occurrences` in [`kmp_search.py`](kmp_search.py):

```python
def find_occurrences(text: str, pattern: str) -> list[int]: ...
```

It must return the 0-based starting indices of **all** occurrences of `pattern` in `text`, in ascending order:

* Occurrences may overlap: `find_occurrences("aaaa", "aa")` returns `[0, 1, 2]`.
* If `pattern` does not occur in `text`, return an empty list.
* Think carefully about the edge cases (empty inputs, pattern longer than text, etc.) and make a deliberate, documented decision on how your implementation handles them.

The observable behavior is the same as in Topic 1, but the implementation must be the KMP algorithm
with its characteristic linear-time complexity.

You are also required to **extend the test suite** in [`test_kmp_search.py`](test_kmp_search.py).
The provided tests are **intentionally incomplete**: they cover only a few obvious cases.
Passing them does **not** mean your solution is correct or complete.

Your extended test suite must include property-based tests written with the
[Hypothesis](https://hypothesis.readthedocs.io/) framework, in addition to example-based tests.
Tests must verify the properties of the algorithm, not hardcoded input/output pairs only.

Test data generation is kept separate from the tests: all inputs are produced by the
composite strategies in [`kmp_generators.py`](kmp_generators.py), and the tests only
assert the property each generator guarantees by construction. Follow the same structure
in your own tests — generate data in the generators module, not inside the test functions.
You are **encouraged to add more generators and more tests** of your own.

## Acceptance criteria
1. `find_occurrences` is implemented as the KMP algorithm — including the prefix-function (failure-function) preprocessing step. Do not call built-in search helpers (`str.find`, `str.index`, `in`, `re`, etc.) to do the searching for you.
2. All tests pass: `uv run pytest topic-2`.
3. The starter test suite is extended with your own tests:
   * example-based tests for edge cases;
   * further Hypothesis property-based tests covering properties the starter suite does not.
4. Code is readable, typed, and documented where behavior is not obvious.
5. The solution is submitted as a pull request from the `topic-2` branch (see the root [README](../README.md)).

## Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) for this task is forbidden.**
  Both the implementation and the tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult textbooks and lecture materials to understand the algorithm.
