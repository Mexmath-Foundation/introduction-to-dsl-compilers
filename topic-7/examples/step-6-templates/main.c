/* Handwritten driver for the generated light.c. The events are the input,
   given on the command line by name:  ./light tick panic tick
   Output, one line each: the initial state, then for every event the
   actions performed and the state reached. The same lines the Python
   interpreter prints, so the two can be compared (difftest.py). */
#include <stdio.h>
#include <string.h>
#include "light.h"

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
