"""Hypothesis data generators for Topic 4: Execution plan policy.

The central strategy is ``plans(...)``: it generates a syntactically
valid execution plan of 1 to 4 commands (a single command, a ``;``
sequence, or a ``|`` pipeline) built from the command table in
``command_spec.py``.

The caller controls what the plan is made of by passing six pools,
mirroring the three policy categories of the task:

* ``allowed_commands`` / ``forbidden_commands`` / ``unknown_commands``
  — command names to draw from (must be keys of ``COMMANDS``);
* ``allowed_paths`` / ``forbidden_paths`` / ``unknown_paths``
  — absolute paths to draw path arguments from.

Commands are drawn from the union of the command pools, paths from the
union of the path pools, with one guarantee: **every non-empty
"forbidden" or "unknown" pool contributes at least one element to the
plan** (an empty pool contributes nothing, of course). This makes the
expected verdict known by construction:

* only the "allowed" pools are non-empty -> every element of the plan
  is allowed, so the plan must be ALLOWED;
* a "forbidden" pool is non-empty        -> the plan surely contains a
  blacklisted element, so the plan must be FORBIDDEN — regardless of
  what else it contains;
* "forbidden" pools are empty but an "unknown" pool is non-empty
  -> the plan surely contains an unlisted element and no blacklisted
  one, so the plan must ASK for confirmation.

The generator itself knows nothing about the policy: the pools only
say where values come from. It is the test's job to pass pools that
are consistent with the white/black lists it gives to the evaluator
(e.g. the "unknown" pools must contain values listed in neither).

Students are encouraged to add more generators here (and more tests
that use them).
"""

from typing import NamedTuple

from command_spec import COMMANDS
from hypothesis import strategies as st

# Cap for commands that accept an unbounded number of paths
# (max_paths=None), to keep generated plans short and readable.
MAX_GENERATED_PATHS = 3


class GeneratedPlan(NamedTuple):
    """A rendered plan together with everything that was drawn into it.

    ``command_names`` and ``paths`` list the drawn elements in order of
    appearance, so a test can compute which pools the plan actually
    touched and derive the expected decision.
    """

    text: str
    command_names: list[str]
    paths: list[str]


class _Invocation(NamedTuple):
    """One command invocation before rendering: name, flags, paths."""

    name: str
    flags: list[str]
    paths: list[str]


@st.composite
def absolute_paths(draw: st.DrawFn) -> str:
    # A syntactically valid path of the language: "/" followed by 1-3
    # segments of [a-z0-9._-] characters; "." and ".." segments cannot
    # be produced because a segment never consists of dots only.
    segment = st.from_regex(r"[a-z0-9_-]+(\.[a-z0-9_-]+)?", fullmatch=True)
    segments = draw(st.lists(segment, min_size=1, max_size=3))
    return "/" + "/".join(segments)


def _check_pools(command_pools: list[list[str]], path_pools: list[list[str]]) -> None:
    # Fail fast on misuse: every command must exist in the command
    # table (its spec drives flags and path counts), and at least one
    # pool of each kind must be non-empty — every command in the
    # language requires at least one path, so there must be something
    # to draw from.
    for pool in command_pools:
        for name in pool:
            if name not in COMMANDS:
                raise ValueError(f"unknown command {name!r}: not in the command table")
    if not any(command_pools):
        raise ValueError("all command pools are empty: nothing to draw commands from")
    if not any(path_pools):
        raise ValueError("all path pools are empty: nothing to draw paths from")


@st.composite
def _invocations(draw: st.DrawFn, command_pool: list[str], path_pool: list[str]) -> _Invocation:
    # One syntactically valid invocation: a command from the pool, a
    # subset of its allowed flags (sorted, so rendering is stable), and
    # a spec-conforming number of paths from the path pool.
    name = draw(st.sampled_from(command_pool))
    spec = COMMANDS[name]
    flags = sorted(draw(st.sets(st.sampled_from(sorted(spec.flags))))) if spec.flags else []
    max_paths = spec.max_paths if spec.max_paths is not None else MAX_GENERATED_PATHS
    count = draw(st.integers(min_value=spec.min_paths, max_value=max_paths))
    paths = [draw(st.sampled_from(path_pool)) for _ in range(count)]
    return _Invocation(name=name, flags=flags, paths=paths)


@st.composite
def plans(
    draw: st.DrawFn,
    allowed_commands: list[str],
    forbidden_commands: list[str],
    unknown_commands: list[str],
    allowed_paths: list[str],
    forbidden_paths: list[str],
    unknown_paths: list[str],
) -> GeneratedPlan:
    command_pools = [list(allowed_commands), list(forbidden_commands), list(unknown_commands)]
    path_pools = [list(allowed_paths), list(forbidden_paths), list(unknown_paths)]
    _check_pools(command_pools, path_pools)
    command_pool = [name for pool in command_pools for name in pool]
    path_pool = [path for pool in path_pools for path in pool]

    # The non-"allowed" pools that must contribute at least one element.
    required_command_pools = [p for p in (forbidden_commands, unknown_commands) if p]
    required_path_pools = [p for p in (forbidden_paths, unknown_paths) if p]

    # 1 to 4 invocations. Each required pool is granted its own
    # invocation slot, so the guarantees can never conflict: a plan
    # must be long enough to host one element from every required pool
    # (every invocation carries at least one path, so invocation slots
    # work for path guarantees too).
    min_size = max(1, len(required_command_pools), len(required_path_pools))
    size = draw(st.integers(min_value=min_size, max_value=4))

    # Reserve a distinct slot per required command pool up front and
    # draw that slot's command from the required pool directly; the
    # remaining slots draw from the full union.
    slot_order = draw(st.permutations(range(size)))
    slot_pools = [command_pool] * size
    for index, pool in zip(slot_order, required_command_pools, strict=False):
        slot_pools[index] = list(pool)
    invocations = [draw(_invocations(pool, path_pool)) for pool in slot_pools]

    # Same for paths: a distinct invocation per required path pool gets
    # one of its path arguments overwritten with a draw from that pool.
    slot_order = draw(st.permutations(range(size)))
    for index, pool in zip(slot_order, required_path_pools, strict=False):
        target = invocations[index]
        path_index = draw(st.integers(min_value=0, max_value=len(target.paths) - 1))
        new_paths = list(target.paths)
        new_paths[path_index] = draw(st.sampled_from(list(pool)))
        invocations[index] = target._replace(paths=new_paths)

    separator = draw(st.sampled_from([" ; ", " | "]))
    text = separator.join(" ".join([i.name, *i.flags, *i.paths]) for i in invocations)
    return GeneratedPlan(
        text=text,
        command_names=[i.name for i in invocations],
        paths=[path for i in invocations for path in i.paths],
    )
