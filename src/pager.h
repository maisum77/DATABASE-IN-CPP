#ifndef PAGER_H
#define PAGER_H
#include <cstdio>
#include <cstring>
using namespace std;

const int PAGE_SIZE = 512;   // small for testing

struct Page {
    char bytes[PAGE_SIZE]{};
};

class Pager {
    FILE* file{};
public:
    // try to open without truncating by default; pass truncate=true to create/truncate
    bool open(const char* filename, bool truncate = false) {
        if (truncate) {
            file = fopen(filename, "w+b");   // create/truncate for saving
            return file != nullptr;
        }
        // open for read/write without truncating if file exists
        file = fopen(filename, "r+b");
        if (!file) {
            // file doesn't exist -> create it
            file = fopen(filename, "w+b");
        }
        return file != nullptr;
    }
    void close() { if (file) fclose(file); }

    /* read pageId into dst (0-based) */
    bool read(int pageId, Page& dst) {
        fseek(file, pageId * PAGE_SIZE, SEEK_SET);
        return fread(dst.bytes, 1, PAGE_SIZE, file) == PAGE_SIZE;
    }

    /* write page at pageId */
    bool write(int pageId, const Page& src) {
        fseek(file, pageId * PAGE_SIZE, SEEK_SET);
        return fwrite(src.bytes, 1, PAGE_SIZE, file) == PAGE_SIZE;
    }
};

#endif