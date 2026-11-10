/* Handwritten driver. Arguments are events by name, or `name=value` to set
   a guard variable before the next event:  ./light count=5 night=1 tick panic
   Output, one line each: the initial state, then for every event the actions
   performed and the state reached -- the lines interpret.py prints too. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "light.h"

int main(int argc, char **argv) {
    enum state s = initial_state;
    puts(state_name[s]);
    for (int i = 1; i < argc; i++) {
        char *eq = strchr(argv[i], '=');
        if (eq) {                                   /* count=5 */
            *eq = '\0';
            if (!set_var(argv[i], atoi(eq + 1))) { fprintf(stderr, "unknown variable %s\n", argv[i]); return 1; }
            continue;
        }
        int e = -1;
        for (int k = 0; k < N_EVENTS; k++)
            if (strcmp(argv[i], event_name[k]) == 0) e = k;
        if (e < 0) { fprintf(stderr, "unknown event %s\n", argv[i]); return 1; }
        s = step(s, (enum event) e);
        puts(state_name[s]);
    }
    return 0;
}
