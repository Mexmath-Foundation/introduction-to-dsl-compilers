"""Topic 1: Naive substring search.

Implement the naive (brute-force) algorithm for searching a substring
in a string. See topic-1/README.md for the task description and
acceptance criteria.
"""


def find_occurrences(text: str, pattern: str) -> list[int]:
    """Return the starting indices of all occurrences of ``pattern`` in ``text``.

    Occurrences may overlap. Indices are 0-based and returned in
    ascending order. If ``pattern`` does not occur in ``text``, return
    an empty list.

    Example:
        find_occurrences("abcabc", "abc") -> [0, 3]
        find_occurrences("aaaa", "aa")    -> [0, 1, 2]
    """
    raise NotImplementedError
