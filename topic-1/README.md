# Topic 1: Naive Substring Search

## Task
Implement the **naive (brute-force) algorithm** for searching a substring in a string.

The function to implement is `find_occurrences` in [`naive_search.py`](naive_search.py):

```python
def find_occurrences(text: str, pattern: str) -> list[int]: ...
```

It must return the 0-based starting indices of **all** occurrences of `pattern` in `text`, in ascending order:

* Occurrences may overlap: `find_occurrences("aaaa", "aa")` returns `[0, 1, 2]`.
* If `pattern` does not occur in `text`, return an empty list.
* Think carefully about the edge cases (empty inputs, pattern longer than text, etc.) and make a deliberate, documented decision on how your implementation handles them.

You are also required to **extend the test suite** in [`test_naive_search.py`](test_naive_search.py).
The provided tests are **intentionally incomplete**: they cover only a few obvious cases.
Passing them does **not** mean your solution is correct or complete.

Your extended test suite must include property-based tests written with the
[Hypothesis](https://hypothesis.readthedocs.io/) framework, in addition to example-based tests.
Tests must verify the properties of the algorithm, not hardcoded input/output pairs only.

## Acceptance criteria
1. `find_occurrences` is implemented as the naive algorithm — do not call built-in search helpers (`str.find`, `str.index`, `in`, `re`, etc.) to do the searching for you.
2. All tests pass: `uv run pytest topic-1`.
3. The starter test suite is extended with your own tests:
   * additional example-based tests for edge cases;
   * property-based tests using Hypothesis.
4. Code is readable, typed, and documented where behavior is not obvious.
5. The solution is submitted as a pull request from the `topic-1` branch (see the root [README](../README.md)).

## Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) for this task is forbidden.**
  Both the implementation and the tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult textbooks and lecture materials to understand the algorithm.
