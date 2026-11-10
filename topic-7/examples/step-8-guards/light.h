/* generated from light.fsm by generate_c.py; do not edit */
enum state { RED, GREEN, YELLOW, N_STATES };
enum event { TICK, PANIC, N_EVENTS };
extern const char *state_name[];
extern const char *event_name[];
extern const enum state initial_state;
extern int count;
extern int night;
int set_var(const char *name, int value);
enum state step(enum state s, enum event e);
