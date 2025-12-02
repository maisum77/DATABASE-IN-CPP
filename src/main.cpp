#include "table.h"
using namespace std;


int main() {
    Table t;
    const char cols[3][32] = {"id", "name", "age"};
    t.create(cols, 3);

    /* insert */
    const char r1[3][32] = {"10", "Alice", "20"};
    const char r2[3][32] = {"20", "Bob",   "22"};
    t.insert(r1, 3);
    t.insert(r2, 3);
    std::cout << "---- memory ----\n";
    t.print();

    /* persist */
    t.save("db.bin");
    std::cout << "saved to db.bin\n";

    /* clear memory & reload */
    Table t2;
    t2.create(cols, 3);
    t2.load("db.bin");
    std::cout << "---- loaded ----\n";
    t2.print();

    return 0;
}