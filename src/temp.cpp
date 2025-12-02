#include <iostream>
#include <cstring>

// ---------- one cell ----------
struct Value {
    char     data[32]{};
    Value*   next{nullptr};
};

// ---------- one row ----------
struct Row {
    Value* head{nullptr};
    Row*   next{nullptr};
};

// ---------- tiny table ----------
struct Table {
    char   cols[10][32]{};
    int    colCount{0};
    Row*   firstRow{nullptr};
    Row*   lastRow{nullptr};

    // CREATE TABLE (name1, name2, ...)
    void create(const char names[][32], int n) {
        colCount = n;
        for (int i = 0; i < n; ++i) std::strcpy(cols[i], names[i]);
    }

    // INSERT INTO table VALUES (v1, v2, ...)
    void insert(const char values[][32], int n) {
        if (n != colCount) { std::cout << "Column count mismatch\n"; return; }
        Value* head = nullptr, *prev = nullptr;
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

    // bubble-sort rows by column idx
    void sortBy(int idx) {
        if (idx < 0 || idx >= colCount) return;
        bool swapped;
        do {
            swapped = false;
            Row** cur = &firstRow;
            while (*cur && (*cur)->next) {
                Row* a = *cur;
                Row* b = a->next;
                // grab cell values
                Value* va = a->head;
                Value* vb = b->head;
                for (int i = 0; i < idx; ++i) { va = va->next; vb = vb->next; }
                if (std::strcmp(va->data, vb->data) > 0) {
                    a->next = b->next;
                    b->next = a;
                    *cur = b;
                    swapped = true;
                }
                cur = &((*cur)->next);
            }
        } while (swapped);
    }

    // PRINT entire table
    void print() {
        for (int i = 0; i < colCount; ++i) std::cout << cols[i] << '\t';
        std::cout << '\n';
        for (Row* p = firstRow; p; p = p->next) {
            for (Value* v = p->head; v; v = v->next) std::cout << v->data << '\t';
            std::cout << '\n';
        }
    }

    // PRINT WHERE col = val
    void printWhere(int idx, const char* val) {
        if (idx < 0 || idx >= colCount) return;
        for (Row* p = firstRow; p; p = p->next) {
            Value* v = p->head;
            for (int i = 0; i < idx; ++i) v = v->next;
            if (std::strcmp(v->data, val) == 0) {
                for (Value* cell = p->head; cell; cell = cell->next)
                    std::cout << cell->data << '\t';
                std::cout << '\n';
            }
        }
    }
};

// ---------- tiny CLI ----------
int main() {
    Table t;
    const char cols[3][32] = {"id", "name", "age"};
    t.create(cols, 3);

    t.insert((const char [3][32]){"3", "Carol", "19"});
    t.insert((const char [3][32]){"1", "Alice", "20"});
    t.insert((const char [3][32]){"2", "Bob", "22"});

    std::cout << "--- original ---\n";
    t.print();

    std::cout << "--- sorted by name ---\n";
    t.sortBy(1);
    t.print();

    std::cout << "--- where age = 20 ---\n";
    t.printWhere(2, "20");

    return 0;
}