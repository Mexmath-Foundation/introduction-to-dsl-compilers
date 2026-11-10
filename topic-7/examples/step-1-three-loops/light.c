enum state { RED, GREEN, YELLOW };
enum event { TICK, PANIC };

enum state step(enum state s, enum event e) {
  switch (s) {
  case RED:
    if (e == TICK) return GREEN;
    return s;
  case GREEN:
    if (e == TICK) return YELLOW;
    if (e == PANIC) return RED;
    return s;
  case YELLOW:
    if (e == TICK) return RED;
    return s;
  }
  return s;
}
