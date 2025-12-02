#include "table.h"

int main() {
    Table t;
    const char cols[3][32] = {"id", "name", "age"};
    t.create(cols, 3);

    t.insert((const char [3][32]){"10", "Alice", "20"}, 3);
    t.insert((const char [3][32]){"20", "Bob",   "22"}, 3);

    std::cout << "---- memory ----\n";
    t.print();

    t.save("db.bin");
    std::cout << "saved\n";

    Table t2;
    t2.create(cols, 3);
    t2.load("db.bin");
    std::cout << "---- loaded ----\n";
    t2.print();
}