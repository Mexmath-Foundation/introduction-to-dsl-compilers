#!/usr/bin/env python3
"""Differential test: the interpreter and the generated C must agree.

Two translations of the same model -- one executed by Python at run time,
one compiled by gcc -- are fed the same input and must print the same
lines. Neither is the oracle; a disagreement means that at least one of
them misreads the model, and the diff says where.

    uv run python difftest.py tick panic tick tick panic
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from generate_c import CVisitor
from interpret import Interpreter
from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def main(events):
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")

    expected = Interpreter(m).run_lines(events)

    v = CVisitor()
    v.visit(m)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "light.h").write_text(v.text_h())
        (tmp / "light.c").write_text(v.text_c())
        shutil.copy(HERE / "main.c", tmp)  # the driver finds "light.h" next to itself
        subprocess.run(
            ["gcc", "-Wall", "-o", tmp / "light", tmp / "light.c", tmp / "main.c"], check=True
        )
        actual = subprocess.run(
            [tmp / "light", *events], capture_output=True, text=True, check=True
        ).stdout.splitlines()

    for e, a in zip(expected, actual, strict=False):  # lengths may differ: that IS a finding
        print(f"{'ok ' if e == a else 'XX '} {e:<24} {a}")
    if expected == actual:
        print(f"same {len(expected)} lines")
        return 0
    print("DIFFERENT")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["tick", "panic", "tick", "tick", "panic"]))
