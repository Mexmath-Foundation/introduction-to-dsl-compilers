"""Semantic rules of the ATM language: the module you write for Topic 6.

The grammar in ``atm.tx`` decides whether a description is *written*
correctly. The rules in this module decide whether it *makes sense*: one
initial state, unique names, one transition per event in a state, every
state reachable, no dead ends, no contradictory actions, no unused
events (see "The rules" in README.md).

The rules are attached to the metamodel as object processors and model
processors, so every description parsed with that metamodel is checked
inside ``model_from_str`` / ``model_from_file`` itself, and a broken
description is rejected with ``TextXSemanticError`` pointing at the
culprit. ``load_atm`` and ``load_atm_file`` are thin wrappers that the
tests and ``check_atm.py`` call.

The skeleton registers nothing: it accepts every description the grammar
accepts. Write the processors in this file and register them in
``metamodel``.
"""

from functools import cache
from pathlib import Path

from textx import metamodel_from_file

# Your rules will also need:
#   from textx import get_location
#   from textx.exceptions import TextXSemanticError

GRAMMAR = Path(__file__).with_name("atm.tx")


@cache
def metamodel():
    """The metamodel of the language, with the semantic rules registered.

    Built once and reused: processors are registered on the metamodel,
    not on a model, so they apply to every description it parses.
    """
    mm = metamodel_from_file(GRAMMAR)
    # textX keeps one object processor per class and every call to
    # register_obj_processors replaces the previous one: register them all
    # in one call, with one function per class.
    # mm.register_obj_processors({"State": ..., "Transition": ...})
    # Model processors run in registration order: rules 1, 2, 4, 7.
    # mm.register_model_processor(...)
    return mm


def load_atm(text: str):
    """Parse a description from a string; raise TextXSemanticError if a rule is broken."""
    return metamodel().model_from_str(text)


def load_atm_file(path: str | Path):
    """Parse a description from a file; errors carry the file name."""
    return metamodel().model_from_file(str(path))
