#!/usr/bin/env python3
"""Differential test with guards: both sides read the same variables.

    uv run python difftest.py count=5 night=1 tick panic tick

`name=value` arguments set a variable (in the interpreter's env and, through
set_var, in the compiled program) before the next event; everything else is
an event. The generated C is compiled into a temporary directory.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from generate_c import generate
from interpret import Interpreter
from textx import metamodel_from_file

HERE = Path(__file__).resolve().parent


def run_interpreter(m, args):
    env = {}
    i = None
    lines = []
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            env[k] = int(v)
            continue
        if i is None:
            i = Interpreter(m, env)
            lines.append(i.state.name)
        before = len(i.log)
        state = i.step(a)
        lines += i.log[before:] + [state.name]
    if i is None:
        i = Interpreter(m, env)
        lines.append(i.state.name)
    return lines


def main(args):
    mm = metamodel_from_file(HERE / "fsm.tx")
    m = mm.model_from_file(HERE / "light.fsm")
    expected = run_interpreter(m, args)
    v = generate(m)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "light.h").write_text(v.text_h())
        (tmp / "light.c").write_text(v.text_c())
        shutil.copy(HERE / "main.c", tmp)  # the driver finds "light.h" next to itself
        subprocess.run(
            ["gcc", "-Wall", "-o", tmp / "light", tmp / "light.c", tmp / "main.c"], check=True
        )
        actual = subprocess.run(
            [tmp / "light", *args], capture_output=True, text=True, check=True
        ).stdout.splitlines()
    for e, a in zip(expected, actual, strict=False):  # lengths may differ: that IS a finding
        print(f"{'ok ' if e == a else 'XX '} {e:<24} {a}")
    print(f"same {len(expected)} lines" if expected == actual else "DIFFERENT")
    return 0 if expected == actual else 1


if __name__ == "__main__":
    sys.exit(
        main(
            sys.argv[1:]
            or [
                "count=1",
                "night=0",
                "tick",
                "panic",
                "count=5",
                "night=1",
                "tick",
                "count=2",
                "tick",
                "count=5",
                "panic",
                "tick",
            ]
        )
    )
