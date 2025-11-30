#include "table.h"

int main() {
    Table t;
    const char cols[3][32] = {"id", "name", "age"};
    t.create(cols, 3);

    const char r1[3][32] = {"3", "Carol", "19"};
    const char r2[3][32] = {"1", "Alice", "20"};
    const char r3[3][32] = {"2", "Bob",   "22"};
    t.insert(r1, 3);
    t.insert(r2, 3);
    t.insert(r3, 3);

    std::cout << "--- original ---\n";
    t.print();

    std::cout << "--- sorted by name ---\n";
    t.sortBy(1);   // column index 1 = name
    t.print();

    std::cout << "--- where age = 20 ---\n";
    t.printWhere(2, "20");

    return 0;
}