"""Semantic rules of the ATM language: copy your topic-6/atm_rules.py over this file.

Every description this topic translates is loaded through ``load_atm`` /
``load_atm_file`` from this module, so the seven rules of Topic 6 apply
before any visitor sees the model: a translator can assume one initial
state, unique names, one transition per event, every state reachable. The
translations themselves check nothing (see "Translation refuses nothing" in
the lecture).

Until you copy your rules in, this is the Topic 6 skeleton: it registers
nothing and accepts every description the grammar accepts. The interface
(``metamodel``, ``load_atm``, ``load_atm_file``) is the one Topic 6 fixed and
must not change; ``atm_translate.py`` imports it.
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
