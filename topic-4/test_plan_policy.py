"""Starter test suite for Topic 4: Execution plan policy.

Property-based tests written with Hypothesis. All test data comes from
the composite strategies in ``plan_generators.py`` — tests never build
their inputs inline, they only assert the property the generator
guarantees by construction.

The pools below mirror the three policy categories: the rules passed
to ``evaluate_plan`` consist of the white and black lists only, while
the UNKNOWN_* pools hold values deliberately listed in neither — the
generator uses them to produce plans that must trigger a confirmation.

This suite is intentionally incomplete. It covers only a few obvious
properties; you are expected to extend it (and the generators) — see
topic-4/README.md.
"""

import pytest
from hypothesis import given
from plan_generators import plans
from plan_policy import Decision, evaluate_plan

# The white and black lists: the rules under test.
WHITE_COMMANDS = ["ls", "cat", "cp"]
BLACK_COMMANDS = ["rm"]
WHITE_PATHS = ["/home/user/docs", "/tmp/work"]
BLACK_PATHS = ["/etc", "/var/log"]

# Values listed in neither list. Kept prefix-disjoint from the lists
# above, so an "unknown" path can never be accidentally covered by a
# white- or blacklisted folder.
UNKNOWN_COMMANDS = ["mv", "mkdir"]
UNKNOWN_PATHS = ["/opt/data", "/srv/backup"]

# Paths lying strictly under whitelisted folders: they are not list
# entries themselves, but the folder coverage rule must allow them.
WHITE_SUBPATHS = ["/home/user/docs/report.txt", "/tmp/work/build/out.log"]


def decide(plan_text: str) -> Decision:
    return evaluate_plan(
        plan_text,
        allowed_commands=WHITE_COMMANDS,
        forbidden_commands=BLACK_COMMANDS,
        allowed_paths=WHITE_PATHS,
        forbidden_paths=BLACK_PATHS,
    )


# ALLOWED: a plan built solely from whitelisted commands and paths must
# pass without questions.
@given(plan=plans(WHITE_COMMANDS, [], [], WHITE_PATHS, [], []))
def test_fully_whitelisted_plan_is_allowed(plan) -> None:
    assert decide(plan.text) is Decision.ALLOWED


# ALLOWED, folder coverage: the plan touches only files lying *under*
# whitelisted folders — the paths themselves are not list entries, but
# the segment-wise prefix rule must cover them.
@given(plan=plans(WHITE_COMMANDS, [], [], WHITE_SUBPATHS, [], []))
def test_paths_under_whitelisted_folders_are_allowed(plan) -> None:
    assert decide(plan.text) is Decision.ALLOWED


# FORBIDDEN by command: the generator guarantees at least one
# blacklisted command; whatever else the plan contains, it must be
# rejected.
@given(plan=plans(WHITE_COMMANDS, BLACK_COMMANDS, [], WHITE_PATHS, [], []))
def test_plan_with_blacklisted_command_is_forbidden(plan) -> None:
    assert decide(plan.text) is Decision.FORBIDDEN


# FORBIDDEN by path: same, with a guaranteed blacklisted path.
@given(plan=plans(WHITE_COMMANDS, [], [], WHITE_PATHS, BLACK_PATHS, []))
def test_plan_with_blacklisted_path_is_forbidden(plan) -> None:
    assert decide(plan.text) is Decision.FORBIDDEN


# CONFIRMATION by command: at least one command is listed nowhere and
# nothing is blacklisted — the user must be asked.
@given(plan=plans(WHITE_COMMANDS, [], UNKNOWN_COMMANDS, WHITE_PATHS, [], []))
def test_plan_with_unlisted_command_requires_confirmation(plan) -> None:
    assert decide(plan.text) is Decision.CONFIRMATION_REQUIRED


# CONFIRMATION by path: same, with a guaranteed unlisted path.
@given(plan=plans(WHITE_COMMANDS, [], [], WHITE_PATHS, [], UNKNOWN_PATHS))
def test_plan_with_unlisted_path_requires_confirmation(plan) -> None:
    assert decide(plan.text) is Decision.CONFIRMATION_REQUIRED


# Precedence: when a plan contains both blacklisted and unlisted
# elements, FORBIDDEN must win over CONFIRMATION_REQUIRED.
@given(
    plan=plans(
        WHITE_COMMANDS,
        BLACK_COMMANDS,
        UNKNOWN_COMMANDS,
        WHITE_PATHS,
        BLACK_PATHS,
        UNKNOWN_PATHS,
    )
)
def test_forbidden_wins_over_confirmation(plan) -> None:
    assert decide(plan.text) is Decision.FORBIDDEN


# Syntax errors are a separate channel: an invalid plan raises
# ValueError instead of returning any verdict. A few obvious shapes;
# covering the rest of the error space is part of the assignment.
@pytest.mark.parametrize(
    "bad_plan",
    [
        "python /home/user/docs",  # command not in the command table
        "ls -z /home/user/docs",  # flag not accepted by the command
        "cp /home/user/docs",  # too few paths for cp
        "ls docs",  # relative path
        "rm /home/user/../etc",  # ".." segment is not part of the language
    ],
)
def test_invalid_plan_raises_value_error(bad_plan: str) -> None:
    with pytest.raises(ValueError):
        decide(bad_plan)
