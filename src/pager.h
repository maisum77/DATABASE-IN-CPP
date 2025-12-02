#ifndef PAGER_H
#define PAGER_H
#include <cstdio>
#include <cstring>
constexpr int PAGE_SIZE  = 512;
constexpr int POOL_PAGES = 64;

struct Page {
    char   bytes[PAGE_SIZE]{};
    bool   dirty{false};
    bool   inUse{false};
    int    pageId{-1};
    int    prevLRU{-1};
    int    nextLRU{-1};
};

class Pager {
    FILE* file{};
    Page  pool[POOL_PAGES];
    int   headLRU;               // most recent
    int   freeList{-1};          // linked list of free slots

    int  allocSlot();            // from free or LRU
    void removeFromLRU(int slot);
    void addToHeadLRU(int slot);
public:
    bool open(const char* filename);
    void close();

    Page* getPage(int pageId);   // pin & return
    void  unpinPage(int pageId, bool dirty);
};

#endif