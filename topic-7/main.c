/* Topic 7: handwritten driver for the generated atm.h / atm.c.
   Build (after `uv run python topic-7/translate_atm.py topic-7/atm.atm --c build`):
       cp topic-7/main.c build/ && cd build && gcc -Wall atm.c main.c -o atm
   Run with events by name:
       ./atm card_inserted pin_ok amount_entered cash_taken card_taken
   Output, one line each: the initial state, then for every event the actions
   performed and the state reached -- the same lines Interpreter.run_lines
   returns, which is what the differential test compares. An undeclared event
   is an error in the input: message on stderr, exit status 1. */
#include <stdio.h>
#include <string.h>
#include "atm.h"

int main(int argc, char **argv) {
    enum state s = initial_state;
    puts(state_name[s]);
    for (int i = 1; i < argc; i++) {
        int e = -1;
        for (int k = 0; k < N_EVENTS; k++)
            if (strcmp(argv[i], event_name[k]) == 0) e = k;
        if (e < 0) { fprintf(stderr, "unknown event %s\n", argv[i]); return 1; }
        s = step(s, (enum event) e);
        puts(state_name[s]);
    }
    return 0;
}
