"""Topic 3: Aho–Corasick multi-pattern search.

Implement the Aho–Corasick algorithm for searching a set of patterns
in a string. See topic-3/README.md for the task description and
acceptance criteria.
"""


def find_occurrences(text: str, patterns: list[str]) -> dict[str, list[int]]:
    """Return the starting indices of all occurrences of each pattern in ``text``.

    The result maps every pattern from ``patterns`` to the list of
    0-based starting indices of its occurrences in ``text``, in
    ascending order. Occurrences may overlap. A pattern that does not
    occur in ``text`` is mapped to an empty list.

    Example:
        find_occurrences("ushers", ["he", "she", "hers"])
            -> {"he": [2], "she": [1], "hers": [2]}
    """
    raise NotImplementedError
