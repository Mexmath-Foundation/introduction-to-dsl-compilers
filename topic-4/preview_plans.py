"""Preview the execution plans the topic generators can produce.

Run it from the repository root:

    uv run python topic-4/preview_plans.py

For each pool configuration the script prints a handful of distinct
generated plans, so you can see with your own eyes what the parser
will face and how the by-construction guarantees shape the plans:
a FORBID configuration always yields a blacklisted element, an ASK
configuration always yields an unlisted one and never a blacklisted
one, and so on.

Feel free to edit the pools below (or add configurations) while
developing your solution — this script is a playground, not a test.
"""

import sys
from pathlib import Path

# Make the topic modules importable no matter where the script is run from.
sys.path.insert(0, str(Path(__file__).parent))

from hypothesis import HealthCheck, given, settings
from plan_generators import GeneratedPlan, plans

WHITE_CMD = ["ls", "cat", "cp"]
BLACK_CMD = ["rm"]
UNKNOWN_CMD = ["mv", "mkdir"]

WHITE_P = ["/home/user/docs", "/home/user/projects", "/tmp/work"]
BLACK_P = ["/etc/passwd", "/var/log"]
UNKNOWN_P = ["/opt/data", "/srv/backup"]

CASES = [
    (
        "ALLOW: only whitelisted commands and paths",
        dict(
            allowed_commands=WHITE_CMD,
            forbidden_commands=[],
            unknown_commands=[],
            allowed_paths=WHITE_P,
            forbidden_paths=[],
            unknown_paths=[],
        ),
    ),
    (
        "FORBID: at least one blacklisted command",
        dict(
            allowed_commands=WHITE_CMD,
            forbidden_commands=BLACK_CMD,
            unknown_commands=[],
            allowed_paths=WHITE_P,
            forbidden_paths=[],
            unknown_paths=[],
        ),
    ),
    (
        "FORBID: at least one blacklisted path",
        dict(
            allowed_commands=WHITE_CMD,
            forbidden_commands=[],
            unknown_commands=[],
            allowed_paths=WHITE_P,
            forbidden_paths=BLACK_P,
            unknown_paths=[],
        ),
    ),
    (
        "ASK: at least one unknown command, nothing blacklisted",
        dict(
            allowed_commands=WHITE_CMD,
            forbidden_commands=[],
            unknown_commands=UNKNOWN_CMD,
            allowed_paths=WHITE_P,
            forbidden_paths=[],
            unknown_paths=[],
        ),
    ),
    (
        "ASK: at least one unknown path, nothing blacklisted",
        dict(
            allowed_commands=WHITE_CMD,
            forbidden_commands=[],
            unknown_commands=[],
            allowed_paths=WHITE_P,
            forbidden_paths=[],
            unknown_paths=UNKNOWN_P,
        ),
    ),
    (
        "FORBID (mixed): blacklisted and unknown commands and paths all present",
        dict(
            allowed_commands=WHITE_CMD,
            forbidden_commands=BLACK_CMD,
            unknown_commands=UNKNOWN_CMD,
            allowed_paths=WHITE_P,
            forbidden_paths=BLACK_P,
            unknown_paths=UNKNOWN_P,
        ),
    ),
]

SAMPLES_PER_CASE = 8


def preview(title: str, pools: dict[str, list[str]]) -> None:
    samples: list[str] = []

    # Abuse @given as a sampler: run the strategy many times and keep
    # the first few distinct rendered plans.
    @settings(max_examples=120, database=None, suppress_health_check=list(HealthCheck))
    @given(plan=plans(**pools))
    def collect(plan: GeneratedPlan) -> None:
        if len(samples) < SAMPLES_PER_CASE and plan.text not in samples:
            samples.append(plan.text)

    collect()
    print(f"\n=== {title} ===")
    for text in samples:
        print(f"  {text}")


if __name__ == "__main__":
    for title, pools in CASES:
        preview(title, pools)
