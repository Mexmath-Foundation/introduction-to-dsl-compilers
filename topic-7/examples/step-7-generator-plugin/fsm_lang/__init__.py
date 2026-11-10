"""Step 7: the FSM language and its Mermaid generator as a textX plugin.

Until now every script built the metamodel itself and called a visitor by
hand. textX also has a registry: a *language* (a name, a file pattern and a
metamodel factory) and a *generator* (a function for one language and one
target), both announced through Python entry points in ``pyproject.toml``.
Once this package is installed, the ``textx`` command knows our language by
the ``.fsm`` extension and can run the generator without any script:

    textx list-languages          # fsm (*.fsm)  ...
    textx list-generators         # fsm -> mermaid ...
    textx generate light.fsm --target mermaid --overwrite

This is how the built-in ``any -> dot`` generator of lecture 10, slide 10,
is wired too -- the same mechanism, nothing special about textX's own.
"""

from pathlib import Path

from textx import generator, language, metamodel_from_file

from .mermaid import MermaidVisitor

HERE = Path(__file__).resolve().parent


@language("fsm", "*.fsm")
def fsm_language():
    """The traffic-light state machine language (Topic 7 grammar)."""
    return metamodel_from_file(HERE / "fsm.tx")


@generator("fsm", "mermaid")
def fsm_mermaid_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    """Generate a Mermaid stateDiagram-v2 (.mmd) from an .fsm model."""
    # textX gives us the parsed model and where it came from; the visitor is
    # the one of step 3. Everything else here is file handling.
    src = Path(model._tx_filename)
    out = Path(output_path or src.parent) / (src.stem + ".mmd")
    if out.exists() and not overwrite:
        print(f"-- Skipping: {out} exists (use --overwrite)")
        return
    v = MermaidVisitor()
    v.visit(model)
    out.write_text(v.text())
    print(f"-> {out}")
