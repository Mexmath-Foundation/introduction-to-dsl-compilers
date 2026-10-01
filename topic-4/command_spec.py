"""Topic 4: The command table — the complete specification of the command language.

This module defines the *closed* set of shell commands that can appear
in an execution plan, together with the complete list of acceptable
flags and the number of path arguments for each command. Anything not
described here is not part of the language: an unknown command, an
unknown flag, or a wrong number of paths makes a plan invalid.

The table is deliberately minimal. The goal of the topic is parsing
and policy evaluation, not modelling the real `ls` with its dozens of
flags — each command carries only the few flags needed to make the
exercise interesting.

This file is part of the task specification: do not change it, build
your parser on top of it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    """The grammar of a single command.

    A command invocation is valid when:
    * every flag it uses is listed in ``flags`` (flags are optional,
      may appear in any order, but must precede the path arguments);
    * the number of path arguments is between ``min_paths`` and
      ``max_paths`` inclusive (``max_paths`` is ``None`` when the
      command accepts any number of paths above the minimum).
    """

    name: str
    flags: frozenset[str]
    min_paths: int
    max_paths: int | None


# The complete command language: name -> specification.
COMMANDS: dict[str, CommandSpec] = {
    # List a directory. The path is mandatory: the language accepts
    # absolute paths only, so there is no implicit "current directory".
    # -l: long listing, -a: include hidden entries.
    "ls": CommandSpec(name="ls", flags=frozenset({"-l", "-a"}), min_paths=1, max_paths=1),
    # Print one or more files.
    # -n: number the output lines.
    "cat": CommandSpec(name="cat", flags=frozenset({"-n"}), min_paths=1, max_paths=None),
    # Copy: all paths but the last are sources, the last is the destination.
    # -r: copy directories recursively.
    "cp": CommandSpec(name="cp", flags=frozenset({"-r"}), min_paths=2, max_paths=2),
    # Move/rename: the first path is the source, the second the destination.
    "mv": CommandSpec(name="mv", flags=frozenset(), min_paths=2, max_paths=2),
    # Remove one or more files or directories.
    # -r: remove directories recursively, -f: do not complain about missing files.
    "rm": CommandSpec(name="rm", flags=frozenset({"-r", "-f"}), min_paths=1, max_paths=None),
    # Create one or more directories.
    # -p: create missing parent directories along the way.
    "mkdir": CommandSpec(name="mkdir", flags=frozenset({"-p"}), min_paths=1, max_paths=None),
}
