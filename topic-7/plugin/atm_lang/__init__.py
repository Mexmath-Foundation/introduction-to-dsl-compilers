"""The ATM language as a textX plugin: what `textx generate x.atm --target mermaid` runs.

This package is provided and wired; you do not have to change it. It makes
the ``textx`` command know the ATM language by its ``.atm`` extension and
gives it two generators, both thin wrappers around the functions you write
in ``atm_translate.py``:

    uv run textx list-languages                       # atm (*.atm) ...
    uv run textx list-generators                      # atm -> mermaid, atm -> c
    uv run textx generate topic-7/atm.atm --target mermaid --overwrite
    uv run textx generate topic-7/atm.atm --target c -o build --overwrite

The language factory is ``atm_rules.metamodel`` -- the metamodel *with the
Topic 6 rules registered* -- so ``textx check x.atm`` applies your rules too.

The course keeps each topic as a flat folder (``atm_rules.py``,
``atm_translate.py`` next to this package's parent), which is why the two
imports below need ``topic-7`` on ``sys.path``: an installed plugin has no
other way to find them. A real-world plugin would ship the modules inside
the package instead (as ``examples/step-7-generator-plugin`` does).
"""

import sys
from pathlib import Path

from textx import generator, language

TOPIC = Path(__file__).resolve().parents[2]  # topic-7/
if str(TOPIC) not in sys.path:
    sys.path.insert(0, str(TOPIC))

from atm_rules import metamodel  # noqa: E402
from atm_translate import to_c, to_mermaid  # noqa: E402


@language("atm", "*.atm")
def atm_language():
    """The ATM description language (Topics 5-7), with its semantic rules."""
    return metamodel()


def _target_file(model, output_path, suffix):
    src = Path(model._tx_filename)
    folder = Path(output_path) if output_path else src.parent
    folder.mkdir(parents=True, exist_ok=True)
    return folder / (src.stem + suffix)


@generator("atm", "mermaid")
def atm_mermaid_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    """Generate a Mermaid stateDiagram-v2 (.mmd) of an ATM."""
    out = _target_file(model, output_path, ".mmd")
    if out.exists() and not overwrite:
        print(f"-- Skipping: {out} exists (use --overwrite)")
        return
    out.write_text(to_mermaid(model))
    print(f"-> {out}")


@generator("atm", "c")
def atm_c_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    """Generate atm.h and atm.c of an ATM (drive them with topic-7/main.c)."""
    header = _target_file(model, output_path, ".h").with_name("atm.h")
    source = header.with_name("atm.c")
    if (header.exists() or source.exists()) and not overwrite:
        print(f"-- Skipping: {header} / {source} exist (use --overwrite)")
        return
    h, c = to_c(model)
    header.write_text(h)
    source.write_text(c)
    print(f"-> {header}\n-> {source}")
