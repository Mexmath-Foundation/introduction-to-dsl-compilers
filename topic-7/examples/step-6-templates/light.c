/* generated from light.fsm by generate_jinja.py; do not edit */
#include <stdio.h>
#include "light.h"

const char *state_name[] = { "Red", "Green", "Yellow" };
const char *event_name[] = { "tick", "panic" };
const enum state initial_state = RED;

enum state step(enum state s, enum event e) {
  switch (s) {
  case RED:
    if (e == TICK) {
      puts("show Go now");
      return GREEN;
    }
    return s;
  case GREEN:
    if (e == TICK) {
      return YELLOW;
    }
    if (e == PANIC) {
      puts("show Say \"stop\" 100%");
      puts("beep");
      return RED;
    }
    return s;
  case YELLOW:
    if (e == TICK) {
      return RED;
    }
    return s;
  default: return s;
  }
}
