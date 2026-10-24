/* GIN-EXP-004: what does this host actually do with x / y?
   Operands come from argv so that the compiler cannot fold the division. */
#include <fenv.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

static void flags(void) {
    printf(" flags=[%s%s%s%s%s]",
           fetestexcept(FE_INVALID) ? "invalid " : "", fetestexcept(FE_DIVBYZERO) ? "divideByZero " : "",
           fetestexcept(FE_OVERFLOW) ? "overflow " : "", fetestexcept(FE_UNDERFLOW) ? "underflow " : "",
           fetestexcept(FE_INEXACT) ? "inexact" : "");
}

int main(int argc, char **argv) {
    if (argc < 4) return 2;
    const char *kind = argv[1];
    if (!strcmp(kind, "int")) {
        int a = atoi(argv[2]), b = atoi(argv[3]);
        if (!strcmp(argv[2], "INT_MIN")) a = INT_MIN;
        int q = a / b;                       /* idiv on x86-64 */
        printf("%d\n", q);
    } else if (!strcmp(kind, "double")) {
        double a = strtod(argv[2], NULL), b = strtod(argv[3], NULL);
        feclearexcept(FE_ALL_EXCEPT);
        volatile double q = a / b;
        printf("%g", q); flags(); printf("\n");
    } else if (!strcmp(kind, "sqrt")) {
        double a = strtod(argv[2], NULL);
        feclearexcept(FE_ALL_EXCEPT);
        volatile double q = sqrt(a);
        printf("%g", q); flags(); printf("\n");
    }
    return 0;
}
