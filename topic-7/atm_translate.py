"""Translation of ATM descriptions: the module you write for Topic 7.

Three things are made from a valid ATM model (loaded through ``atm_rules``,
so every description here has passed the seven rules of Topic 6):

* ``to_mermaid(atm)`` -- a Mermaid ``stateDiagram-v2`` of the ATM, the text
  a README renders as a picture;
* ``Interpreter(atm)`` -- runs the ATM on a sequence of events, keeping the
  current state and a log of the actions performed;
* ``to_c(atm)`` -- a C header and a C source: an ``enum`` per kind of name,
  a ``step`` function, name tables, so that ``main.c`` can drive the ATM
  from the command line exactly as the interpreter does.

Plus, optionally, ``to_dot(atm)`` for Graphviz.

The interface below is fixed: the tests, ``translate_atm.py`` and the
``atm_lang`` plugin call it. Everything else -- how many visitors, how the
C text is assembled, what the helpers are called -- is yours. The
``Visitor`` base class is given; it is the one from the lecture
(``examples/step-2-visitor``). The skeleton raises ``NotImplementedError``
everywhere, so every test fails until you write the code.
"""

from __future__ import annotations

from pathlib import Path

from atm_rules import (  # noqa: F401  (re-exported for the plugin and the tests)
    load_atm,
    load_atm_file,
    metamodel,
)

HERE = Path(__file__).resolve().parent


class Visitor:
    """Dispatch on the node's class name; walk containment attributes by default.

    ``visit(node)`` calls ``visit_<ClassName>(node)`` if your subclass defines
    it, else ``generic_visit``, which visits the node's children: its
    containment attributes (``_tx_attrs``), never its references. Methods
    may return a value; ``visit`` passes it on.
    """

    def visit(self, node):
        method = getattr(self, "visit_" + type(node).__name__, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for attr in type(node)._tx_attrs.values():
            if attr.cont and not attr.is_base_type:
                value = getattr(node, attr.name)
                for child in value if attr.mult != "1" else [value]:
                    if child is not None:
                        self.visit(child)


# ----------------------------------------------------------------------------
# Visualize


def to_mermaid(atm) -> str:
    """The ATM as a Mermaid ``stateDiagram-v2``, ready for a Markdown file.

    Required shape (see "Mermaid" in README.md): the first line is
    ``stateDiagram-v2``; the initial state gets ``[*] --> Name``; a state
    with a label gets ``state "label" as Name``; every transition is one
    line ``Source --> Target : event``. Labels must be escaped for Mermaid.
    """
    raise NotImplementedError


def to_dot(atm) -> str:
    """Optional: the ATM in the DOT language for Graphviz. Extra credit."""
    raise NotImplementedError


# ----------------------------------------------------------------------------
# Interpret


class Interpreter:
    """Run an ATM: one variable, the current state; the events are the input.

    * ``step(name)`` consumes one event by name and returns the new current
      state. An event the ATM never declared is an error in the input:
      ``ValueError``. A declared event the current state has no transition
      for is ignored: the state stays, nothing is logged.
    * ``log`` is the list of actions performed so far, one line each:
      ``show <message>`` (the message text, no quotes), ``eject_card``,
      ``retain_card``, ``dispense``.
    * ``run_lines(names)`` returns the lines the generated C program prints
      for the same input: the initial state's name, then for each event the
      actions it performed and the name of the state reached.
    """

    def __init__(self, atm):
        self.atm = atm
        raise NotImplementedError

    def step(self, name: str):
        raise NotImplementedError

    def run_lines(self, names: list[str]) -> list[str]:
        raise NotImplementedError


# ----------------------------------------------------------------------------
# Generate


def to_c(atm) -> tuple[str, str]:
    """The ATM as C: ``(header, source)`` for ``atm.h`` and ``atm.c``.

    The header must declare what ``main.c`` uses (see "C" in README.md):
    ``enum state`` and ``enum event`` with trailing ``N_STATES`` / ``N_EVENTS``
    members, ``extern const char *state_name[]`` and ``event_name[]``,
    ``extern const enum state initial_state`` and
    ``enum state step(enum state s, enum event e)``. The source defines them
    and ``#include "atm.h"``. Actions print exactly the lines the
    interpreter logs. Every model string that lands in C passes through an
    escaping function.
    """
    raise NotImplementedError
