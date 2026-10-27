"""Preview the ATM descriptions the Topic 6 generators produce.

Run it from the repository root:

    uv run python topic-6/preview_atms.py

The script prints one generated description per strategy: a well-formed
ATM first, then one for each rule-breaking strategy, with the rule it is
reported for. Feed them to ``check_atm.py`` or read them to see what
your rules will face. It is a playground, not a test.
"""

import sys
from pathlib import Path

# Make the topic modules importable no matter where the script is run from.
sys.path.insert(0, str(Path(__file__).parent))

from atm_rule_generators import (
    atms_with_contradictory_actions,
    atms_with_dead_end,
    atms_with_duplicate_event_name,
    atms_with_duplicate_state_name,
    atms_with_duplicate_transition,
    atms_with_no_initial_state,
    atms_with_two_initial_states,
    atms_with_unreachable_state,
    atms_with_unused_event,
    render,
    well_formed_atms,
)
from hypothesis import HealthCheck, given, settings

STRATEGIES = [
    ("well-formed: passes every rule", well_formed_atms),
    ("rule 1: two initial states", atms_with_two_initial_states),
    ("rule 1: no initial state", atms_with_no_initial_state),
    ("rule 2: duplicate state name", atms_with_duplicate_state_name),
    ("rule 2: duplicate event name", atms_with_duplicate_event_name),
    ("rule 3: two transitions on one event", atms_with_duplicate_transition),
    ("rule 4: unreachable state", atms_with_unreachable_state),
    ("rule 5: dead end", atms_with_dead_end),
    ("rule 6: eject_card and retain_card together", atms_with_contradictory_actions),
    ("rule 7: unused event", atms_with_unused_event),
]


def sample(strategy) -> str:
    """Run the strategy once and return the rendered description."""
    found: list[str] = []

    # Abuse @given as a sampler: stop after the first example.
    @settings(max_examples=1, database=None, suppress_health_check=list(HealthCheck))
    @given(atm=strategy(min_states=2, max_states=4) if strategy is well_formed_atms else strategy())
    def collect(atm) -> None:
        found.append(render(atm))

    collect()
    return found[0]


def main() -> None:
    for title, strategy in STRATEGIES:
        print(f"=== {title}")
        print(sample(strategy))


if __name__ == "__main__":
    main()
