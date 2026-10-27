"""Check ATM descriptions against the grammar and the semantic rules.

Run it from the repository root, with one or more files:

    uv run python topic-6/check_atm.py topic-6/atm.atm
    uv run python topic-6/check_atm.py topic-6/broken/*.atm

For every file it prints either ``OK`` with the number of states and
events, or one ``ERROR`` line in the format of ``textx check``:
``file:line:col: message``. Unlike ``textx check``, it loads the
description through ``load_atm_file`` in ``atm_rules.py``, so the rules
you register there are applied too. With your grammar copied in and the
rules still unwritten, every file in ``broken/`` is reported ``OK``; that
is the gap this topic closes. The exit status is 1 if any file was rejected.
"""

import sys
from pathlib import Path

# Make atm_rules importable no matter where the script is run from.
sys.path.insert(0, str(Path(__file__).parent))

from atm_rules import load_atm_file
from textx.exceptions import TextXError


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(f"usage: {argv[0]} <description.atm> [more.atm ...]")
        return 2
    failures = 0
    for path in argv[1:]:
        try:
            atm = load_atm_file(path)
        except TextXError as error:
            print(f"ERROR: {error}")
            failures += 1
        else:
            print(f"OK: {path}: {len(atm.states)} states, {len(atm.events)} events")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
