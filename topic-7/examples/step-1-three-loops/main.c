/* Drives the step function generated into light.c by three_loops.py.
   Build and run from this folder:  gcc light.c main.c -o light && ./light
   Prints the states visited as enum indices: 0 1 2 2 0 1 2 is
   Red Green Yellow Yellow Red Green Yellow, the trace run() printed. */
#include <stdio.h>

enum state { RED, GREEN, YELLOW };
enum event { TICK, PANIC };
enum state step(enum state s, enum event e);

int main(void) {
    enum event input[] = { TICK, TICK, PANIC, TICK, TICK, TICK };
    enum state s = RED;
    printf("%d", s);
    for (int i = 0; i < 6; i++) {
        s = step(s, input[i]);
        printf(" %d", s);
    }
    printf("\n");
    return 0;
}
