# Topic 3: Aho–Corasick Multi-Pattern Search

## Task
Implement the **Aho–Corasick algorithm** for searching a set of patterns in a string.

The function to implement is `find_occurrences` in [`aho_corasick.py`](aho_corasick.py):

```python
def find_occurrences(text: str, patterns: list[str]) -> dict[str, list[int]]: ...
```

It must return a dictionary that maps **every** pattern from `patterns` to the list of 0-based
starting indices of its occurrences in `text`, in ascending order:

* Occurrences may overlap: `find_occurrences("aaaa", ["aa"])` returns `{"aa": [0, 1, 2]}`.
* A pattern that does not occur in `text` must be mapped to an empty list.
* Patterns may be substrings of each other; all matches must still be reported.
* Think carefully about the edge cases (empty inputs, duplicated patterns, etc.) and make a deliberate, documented decision on how your implementation handles them.

The implementation must be the Aho–Corasick algorithm: a single pass over `text` using an automaton
built from all patterns — not a loop that searches each pattern independently.

You are also required to **extend the test suite** in [`test_aho_corasick.py`](test_aho_corasick.py).
The provided tests are **intentionally incomplete**: they cover only a few obvious cases.
Passing them does **not** mean your solution is correct or complete.

Your extended test suite must include property-based tests written with the
[Hypothesis](https://hypothesis.readthedocs.io/) framework, in addition to example-based tests.
Tests must verify the properties of the algorithm, not hardcoded input/output pairs only.

Test data generation is kept separate from the tests: all inputs are produced by the
composite strategies in [`aho_generators.py`](aho_generators.py), and the tests only
assert the property each generator guarantees by construction. Follow the same structure
in your own tests — generate data in the generators module, not inside the test functions.
You are **encouraged to add more generators and more tests** of your own.

## Acceptance criteria
1. `find_occurrences` is implemented as the Aho–Corasick algorithm — including the trie and failure-link construction. Do not call built-in search helpers (`str.find`, `str.index`, `in`, `re`, etc.) to do the searching for you, and do not run a single-pattern search once per pattern.
2. All tests pass: `uv run pytest topic-3`.
3. The starter test suite is extended with your own tests:
   * example-based tests for edge cases;
   * further Hypothesis property-based tests covering properties the starter suite does not.
4. Code is readable, typed, and documented where behavior is not obvious.
5. The solution is submitted as a pull request from the `topic-3` branch (see the root [README](../README.md)).

## Rules
* **Using AI code generation (ChatGPT, Claude, Copilot, or any similar tool) for this task is forbidden.**
  Both the implementation and the tests must be written by you.
* Do not copy solutions from other students or from the internet.
* You may (and should) consult textbooks and lecture materials to understand the algorithm.
