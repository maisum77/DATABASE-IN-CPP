#ifndef ROW_H
#define ROW_H
#include "value.h"

struct Row {
    Value* head;   // first cell of this row
    Row*   next;   // next row in table
};

#endif