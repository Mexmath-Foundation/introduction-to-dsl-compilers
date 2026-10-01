"""Topic 4: Execution plan policy.

Implement the policy evaluator for AI-agent execution plans: parse a
plan written in the command language defined by ``command_spec.py``
and decide whether it may run. See topic-4/README.md for the task
description and acceptance criteria.
"""

from enum import Enum

from command_spec import COMMANDS  # noqa: F401  (the command table drives the parser)


class Decision(Enum):
    """The verdict of the policy evaluation."""

    ALLOWED = "allowed"
    FORBIDDEN = "forbidden"
    CONFIRMATION_REQUIRED = "confirmation_required"


def evaluate_plan(
    plan: str,
    allowed_commands: list[str],
    forbidden_commands: list[str],
    allowed_paths: list[str],
    forbidden_paths: list[str],
) -> Decision:
    """Parse ``plan`` and decide whether it may be executed.

    The plan is one command, a ``;`` sequence, or a ``|`` pipeline of
    commands from the command table in ``command_spec.py`` (commands,
    their acceptable flags, and the number of path arguments are all
    defined there; paths are absolute only). A syntactically invalid
    plan — an unknown command, an unknown flag, a wrong number of
    paths, or a malformed path — must raise ``ValueError``.

    The decision is made from every command and every path the plan
    contains, with the strictest verdict winning:

    * ``Decision.FORBIDDEN`` if at least one command is listed in
      ``forbidden_commands`` or at least one path is covered by
      ``forbidden_paths``;
    * otherwise ``Decision.CONFIRMATION_REQUIRED`` if at least one
      command or path is listed in no list at all (neither white nor
      black);
    * otherwise ``Decision.ALLOWED`` — every command is listed in
      ``allowed_commands`` and every path is covered by
      ``allowed_paths``.

    A list entry covers a path if it is equal to the path or is a
    folder the path lies under, comparing whole segments: the entry
    ``/home/user/docs`` covers ``/home/user/docs/report.txt`` but not
    ``/home/user/docsx``.

    Example:
        evaluate_plan(
            "cat /home/user/docs/a.txt | rm -f /tmp/cache",
            allowed_commands=["cat", "rm"],
            forbidden_commands=[],
            allowed_paths=["/home/user/docs"],
            forbidden_paths=["/tmp"],
        ) -> Decision.FORBIDDEN
    """
    raise NotImplementedError
