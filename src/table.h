#ifndef TABLE_H
#define TABLE_H
#include "row.h"
#include "pager.h"
#include <iostream>
#include <cstring>
using namespace std;

class Table
{
public:
    Pager pager;
    // data
    char colNames[10][32]{};
    int colCount{0};
    Row *firstRow{nullptr};
    Row *lastRow{nullptr};

    // make table
    void create(const char cols[][32], int n)
    {
        colCount = n;
        for (int i = 0; i < n; ++i)
        {
            strcpy(colNames[i], cols[i]);
        }
    }

    // insert row
    void insert(const char values[][32], int n)
    {
        if (n != colCount)
        {
            cout << "Column count mismatch\n";
            return;
        }

        Value *head{nullptr};
        Value *prev{nullptr};
        for (int i = 0; i < n; ++i)
        {
            Value *v = new Value;
            strcpy(v->data, values[i]);
            v->next = nullptr;
            if (!head)
                head = v;
            if (prev)
                prev->next = v;
            prev = v;
        }

        Row *r = new Row{head, nullptr};
        if (!firstRow)
        {
            firstRow = lastRow = r;
        }
        else
        {
            lastRow->next = r;
            lastRow = r;
        }
    }

    // print table
    void print()
    {
        // header
        for (int i = 0; i < colCount; ++i)
        {
            cout << colNames[i] << '\t';
        }
        cout << '\n';

        // rows
        for (Row *p = firstRow; p; p = p->next)
        {
            for (Value *v = p->head; v; v = v->next)
            {
                std::cout << v->data << '\t';
            }
            cout << '\n';
        }
    }
    // bubble sorting
    void sortBy(int colIdx)
    {
        if (colIdx < 0 || colIdx >= colCount)
            return;
        bool swapped;
        do
        {
            swapped = false;
            Row **cur = &firstRow;
            while (*cur && (*cur)->next)
            {
                Row *a = *cur;
                Row *b = a->next;
                /* grab cell values */
                Value *va = a->head;
                Value *vb = b->head;
                for (int i = 0; i < colIdx; ++i)
                {
                    va = va->next;
                    vb = vb->next;
                }
                if (std::strcmp(va->data, vb->data) > 0)
                { // swap rows
                    a->next = b->next;
                    b->next = a;
                    *cur = b;
                    swapped = true;
                }
                cur = &((*cur)->next);
            }
        } while (swapped);
    }
    // finding and showing the data of where the data become equal to what we are looking for
    void printWhere(int colIdx, const char *val)
    {
        if (colIdx < 0 || colIdx >= colCount)
            return;
        for (Row *p = firstRow; p; p = p->next)
        {
            Value *v = p->head;
            for (int i = 0; i < colIdx; ++i)
                v = v->next;
            if (std::strcmp(v->data, val) == 0)
            {
                for (Value *cell = p->head; cell; cell = cell->next)
                    std::cout << cell->data << '\t';
                std::cout << '\n';
            }
        }
    }

    /* ---- serialize one row into page ---- */
    int curPageId{0};
    int curOffset{0};

    void flushRowToDisk(Row *r)
    {
        Page p{};
        int pos = 0;
        for (Value *v = r->head; v; v = v->next)
        {
            std::strcpy(p.bytes + pos, v->data);
            pos += 32; // fixed cell size
        }
        pager.write(curPageId++, p); // simple: one row per page
    }

    /* ---- load one row from page ---- */
    Row *loadRowFromPage(int pageId)
    {
        Page p{};
        if (!pager.read(pageId, p))
            return nullptr;
        Value *head = nullptr;
        Value *prev = nullptr;
        for (int i = 0; i < colCount; ++i)
        {
            Value *v = new Value;
            std::strcpy(v->data, p.bytes + i * 32);
            v->next = nullptr;
            if (!head)
                head = v;
            if (prev)
                prev->next = v;
            prev = v;
        }
        return new Row{head, nullptr};
    }

    bool save(const char *file)
    {
        // open with truncate=true so we start fresh for saving
        if (!pager.open(file, true))
            return false;
        curPageId = 0;
        for (Row *p = firstRow; p; p = p->next)
            flushRowToDisk(p);
        pager.close();
        return true;
    }

    bool load(const char *file)
    {
        if (!pager.open(file))
            return false;
        curPageId = 0;
        while (true)
        {
            Row *r = loadRowFromPage(curPageId);
            if (!r)
                break;
            /* append to linked list */
            if (!firstRow)
                firstRow = lastRow = r;
            else
            {
                lastRow->next = r;
                lastRow = r;
            }
            ++curPageId;
        }
        pager.close();
        return true;
    }
};

#endif