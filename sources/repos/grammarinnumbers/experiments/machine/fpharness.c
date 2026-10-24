/* GIN-EXP-005 hardware oracle: reads "op fmt hexA hexB" lines, prints "hexR flags".
   op in {add, sub, mul, div, sqrt}; fmt in {32, 64}. Flags are read with fenv.h. */
#include <fenv.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#pragma STDC FENV_ACCESS ON

int main(void) {
    char op[8]; int fmt; unsigned long long ha, hb;
    while (scanf("%7s %d %llx %llx", op, &fmt, &ha, &hb) == 4) {
        unsigned long long hr = 0;
        feclearexcept(FE_ALL_EXCEPT);
        if (fmt == 64) {
            volatile double a, b, r; uint64_t ua = ha, ub = hb, ur;
            memcpy((void *)&a, &ua, 8); memcpy((void *)&b, &ub, 8);
            if (!strcmp(op, "add")) r = a + b; else if (!strcmp(op, "sub")) r = a - b;
            else if (!strcmp(op, "mul")) r = a * b; else if (!strcmp(op, "div")) r = a / b; else r = sqrt(a);
            double rr = r; memcpy(&ur, &rr, 8); hr = ur;
        } else {
            volatile float a, b, r; uint32_t ua = (uint32_t)ha, ub = (uint32_t)hb, ur;
            memcpy((void *)&a, &ua, 4); memcpy((void *)&b, &ub, 4);
            if (!strcmp(op, "add")) r = a + b; else if (!strcmp(op, "sub")) r = a - b;
            else if (!strcmp(op, "mul")) r = a * b; else if (!strcmp(op, "div")) r = a / b; else r = sqrtf(a);
            float rr = r; memcpy(&ur, &rr, 4); hr = ur;
        }
        int f = fetestexcept(FE_ALL_EXCEPT);
        printf("%llx %d%d%d%d%d\n", hr, !!(f & FE_INVALID), !!(f & FE_DIVBYZERO), !!(f & FE_OVERFLOW),
               !!(f & FE_UNDERFLOW), !!(f & FE_INEXACT));
    }
    return 0;
}
