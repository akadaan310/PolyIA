/* Does the optimizer use "division by zero is undefined" to delete a later zero check? */
int guarded(int a, int b) {
    int q = a / b;            /* if b == 0 the behaviour is already undefined here ... */
    if (b == 0) return -1;    /* ... so a compiler may assume b != 0 and drop this test */
    return q;
}
