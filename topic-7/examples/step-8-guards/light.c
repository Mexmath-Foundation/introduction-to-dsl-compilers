/* generated from light.fsm by generate_c.py; do not edit */
#include <stdio.h>
#include <string.h>
#include "light.h"

const char *state_name[] = { "Red", "Green", "Yellow" };
const char *event_name[] = { "tick", "panic" };
const enum state initial_state = RED;
int count = 0;
int night = 0;

int set_var(const char *name, int value) {
  if (strcmp(name, "count") == 0) { count = value; return 1; }
  if (strcmp(name, "night") == 0) { night = value; return 1; }
  return 0;
}

enum state step(enum state s, enum event e) {
  switch (s) {
  case RED:
    if (e == TICK && ((count < 3) || (night == 0))) {
      puts("show Go now");
      return GREEN;
    }
    if (e == TICK) {
      puts("show Closed for the night");
      return RED;
    }
    return s;
  case GREEN:
    if (e == TICK) {
      return YELLOW;
    }
    if (e == PANIC && !((night == 1) && ((count * 2) >= 10))) {
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
