#ifndef TABLE_H
#define TABLE_H
#include "row.h"
#include "pager.h"
#include <iostream>
#include <cstring>

class Table {
    /* ---------- data ---------- */
    char   colNames[10][32]{};
    int    colCount{0};
    Row*   firstRow{nullptr};
    Row*   lastRow{nullptr};

    Pager  pager;
    int    nextPage{0};                 // next free page to try
    static constexpr int slotsPerPage = PAGE_SIZE / 32;

    /* ---------- helpers ---------- */
    int allocSlot(Page* p) {
        for (int i = 0; i < slotsPerPage; ++i)
            if (p->bytes[i * 32] == '\0') return i;   // empty marker
        return -1;
    }

public:
    /* ---- create table ---- */
    void create(const char cols[][32], int n) {
        colCount = n;
        for (int i = 0; i < n; ++i) std::strcpy(colNames[i], cols[i]);
    }

    /* ---- insert row (uses pages + keeps RAM list) ---- */
    void insert(const char values[][32], int n) {
        if (n != colCount) { std::cout << "Column count mismatch\n"; return; }

        /* 1. disk page slot */
        Page* pg = pager.getPage(nextPage);
        int slot = allocSlot(pg);
        if (slot == -1) {                       // page full
            pager.unpinPage(nextPage, true);
            ++nextPage;
            pg = pager.getPage(nextPage);
            slot = 0;
        }
        for (int i = 0; i < n; ++i)
            std::strcpy(pg->bytes + slot * 32 + i * 32, values[i]);
        pager.unpinPage(nextPage, true);

        /* 2. memory linked list (for today's print) */
        Value* head{nullptr}, *prev{nullptr};
        for (int i = 0; i < n; ++i) {
            Value* v = new Value;
            std::strcpy(v->data, values[i]);
            v->next = nullptr;
            if (!head) head = v;
            if (prev) prev->next = v;
            prev = v;
        }
        Row* r = new Row{head, nullptr};
        if (!firstRow) firstRow = lastRow = r;
        else { lastRow->next = r; lastRow = r; }
    }

    /* ---- print table (from RAM list) ---- */
    void print() {
        for (int i = 0; i < colCount; ++i) std::cout << colNames[i] << '\t';
        std::cout << '\n';
        for (Row* p = firstRow; p; p = p->next) {
            for (Value* v = p->head; v; v = v->next) std::cout << v->data << '\t';
            std::cout << '\n';
        }
    }

    /* ---- persist ---- */
    bool save(const char* file) {
        if (!pager.open(file)) return false;
        /* write every used page */
        for (int i = 0; i <= nextPage; ++i) {
            Page* p = pager.getPage(i);
            pager.unpinPage(i, true);   // mark dirty so flush happens
        }
        pager.close();
        return true;
    }

    bool load(const char* file) {
        if (!pager.open(file)) return false;
        nextPage = 0;
        while (true) {
            Page* pg = pager.getPage(nextPage);
            bool any = false;
            for (int slot = 0; slot < slotsPerPage; ++slot) {
                if (pg->bytes[slot * 32] == '\0') continue;
                /* rebuild row */
                Value* head{nullptr}, *prev{nullptr};
                for (int i = 0; i < colCount; ++i) {
                    Value* v = new Value;
                    std::strcpy(v->data, pg->bytes + slot * 32 + i * 32);
                    v->next = nullptr;
                    if (!head) head = v;
                    if (prev) prev->next = v;
                    prev = v;
                }
                Row* r = new Row{head, nullptr};
                if (!firstRow) firstRow = lastRow = r;
                else { lastRow->next = r; lastRow = r; }
                any = true;
            }
            pager.unpinPage(nextPage, false);
            if (!any) break;
            ++nextPage;
        }
        pager.close();
        return true;
    }
};

#endif