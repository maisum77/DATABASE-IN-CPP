#ifndef VALUE_H
#define VALUE_H

struct Value {
    char     data[32];   //  everything stored as text
    Value*   next;       // singly-linked
};

#endif