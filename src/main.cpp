#include "table.h"

int main() {
    Table t;
    const char cols[3][32] = {"id", "name", "age"};
    t.create(cols, 3);

    const char r1[3][32] = {"1", "Alice", "20"};
    const char r2[3][32] = {"2", "Bob",   "22"};
    t.insert(r1, 3);
    t.insert(r2, 3);

    t.print();
    return 0;
}