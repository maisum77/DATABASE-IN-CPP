#include <iostream>
#include <cstring>
using namespace std;
#include "value.h"

void printRow(Value* head) {
    for (Value* p = head; p; p = p->next)
            cout << p->data << '\t';
     cout << '\n';
}

int main() {
    /* hand-made row: (1 Alice 20) */
    Value v3 = {"20", nullptr};
    Value v2 = {"Alice", &v3};
    Value v1 = {"1", &v2};

    cout << "First row:\n";
    printRow(&v1);
    return 0;
}