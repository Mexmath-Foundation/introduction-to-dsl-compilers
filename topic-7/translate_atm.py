"""Translate an ATM description from the command line.

Run it from the repository root:

    uv run python topic-7/translate_atm.py topic-7/atm.atm --mermaid
    uv run python topic-7/translate_atm.py topic-7/atm.atm --dot
    uv run python topic-7/translate_atm.py topic-7/atm.atm --run card_inserted pin_ok
    uv run python topic-7/translate_atm.py topic-7/atm.atm --c build/

``--mermaid`` and ``--dot`` print the text; ``--run`` prints the lines the
interpreter produces for the events that follow it; ``--c`` writes atm.h and
atm.c into the given folder (into which you copy main.c and build). The
description is loaded through ``load_atm_file``, so the Topic 6 rules apply
first; a broken description is reported and nothing is translated.
"""

import sys
from pathlib import Path

# Make the topic's modules importable no matter where the script is run from.
sys.path.insert(0, str(Path(__file__).parent))

from atm_translate import Interpreter, load_atm_file, to_c, to_dot, to_mermaid  # noqa: E402
from textx.exceptions import TextXError  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(f"usage: {argv[0]} <description.atm> --mermaid | --dot | --run EVENT... | --c FOLDER")
        return 2
    try:
        atm = load_atm_file(argv[1])
    except (OSError, TextXError) as error:
        print(f"ERROR: {error}")
        return 1
    mode, rest = argv[2], argv[3:]
    if mode == "--mermaid":
        print(to_mermaid(atm).rstrip("\n"))
    elif mode == "--dot":
        print(to_dot(atm).rstrip("\n"))
    elif mode == "--run":
        try:
            print("\n".join(Interpreter(atm).run_lines(rest)))
        except ValueError as error:  # an undeclared event: wrong input, not a wrong ATM
            print(f"ERROR: {error}")
            return 1
    elif mode == "--c":
        folder = Path(rest[0] if rest else ".")
        folder.mkdir(parents=True, exist_ok=True)
        header, source = to_c(atm)
        (folder / "atm.h").write_text(header)
        (folder / "atm.c").write_text(source)
        print(
            f"wrote {folder / 'atm.h'} and {folder / 'atm.c'}; build: gcc -Wall atm.c main.c -o atm"
        )
    else:
        print(f"unknown mode {mode}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
