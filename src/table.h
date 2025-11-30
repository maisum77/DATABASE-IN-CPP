#ifndef TABLE_H
#define TABLE_H
#include "row.h"
#include <iostream>
#include <cstring>
using namespace std;

class Table {
public:
    /* ---- data ---- */
    char   colNames[10][32]{};
    int    colCount{0};
    Row*   firstRow{nullptr};
    Row*   lastRow{nullptr};

    /* ---- create table ---- */
    void create(const char cols[][32], int n) {
        colCount = n;
        for (int i = 0; i < n; ++i) {
            strcpy(colNames[i], cols[i]);
        }
    }

    /* ---- insert row ---- */
    void insert(const char values[][32], int n) {
        if (n != colCount) {
            cout << "Column count mismatch\n";
            return;
        }

        Value* head{nullptr};
        Value* prev{nullptr};
        for (int i = 0; i < n; ++i) {
            Value* v = new Value;
            strcpy(v->data, values[i]);
            v->next = nullptr;
            if (!head) head = v;
            if (prev) prev->next = v;
            prev = v;
        }

        Row* r = new Row{head, nullptr};
        if (!firstRow) {
            firstRow = lastRow = r;
        } else {
            lastRow->next = r;
            lastRow = r;
        }
    }

    /* ---- print table ---- */
    void print() {
        /* header */
        for (int i = 0; i < colCount; ++i) {
            cout << colNames[i] << '\t';
        }
        cout << '\n';

        /* rows */
        for (Row* p = firstRow; p; p = p->next) {
            for (Value* v = p->head; v; v = v->next) {
                std::cout << v->data << '\t';
            }
            cout << '\n';
        }
    }
};

#endif