"""Preview the ATM descriptions the topic generators can produce.

Run it from the repository root:

    uv run python topic-5/preview_atms.py

The script prints a few generated descriptions, so you can see with your
own eyes what your grammar will face: random names, labels, empty and
non-empty transition lists, actions with and without arguments. Edit the
strategy parameters below while developing; it is a playground, not a
test.
"""

import sys
from pathlib import Path

# Make the topic modules importable no matter where the script is run from.
sys.path.insert(0, str(Path(__file__).parent))

from atm_generators import GeneratedAtm, atms, render
from hypothesis import HealthCheck, given, settings

SAMPLES = 3


def main() -> None:
    samples: list[str] = []

    # Abuse @given as a sampler: run the strategy a few times and keep
    # the first distinct rendered descriptions.
    @settings(max_examples=50, database=None, suppress_health_check=list(HealthCheck))
    @given(atm=atms(min_states=2, max_states=4))
    def collect(atm: GeneratedAtm) -> None:
        text = render(atm)
        if len(samples) < SAMPLES and text not in samples:
            samples.append(text)

    collect()
    for index, text in enumerate(samples, start=1):
        print(f"=== sample {index}")
        print(text)


if __name__ == "__main__":
    main()
