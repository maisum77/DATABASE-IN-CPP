#include "pager.h"

bool Pager::open(const char* filename) {
    file = fopen(filename, "r+b");
    if (!file) file = fopen(filename, "w+b");
    if (!file) return false;
    for (int i = 0; i < POOL_PAGES; ++i) pool[i].nextLRU = i + 1;
    pool[POOL_PAGES - 1].nextLRU = -1;
    freeList = 0;
    headLRU  = -1;
    return true;
}
void Pager::close() {
    for (int i = 0; i < POOL_PAGES; ++i)
        if (pool[i].dirty && pool[i].inUse)
            fseek(file, pool[i].pageId * PAGE_SIZE, SEEK_SET),
            fwrite(pool[i].bytes, 1, PAGE_SIZE, file);
    if (file) fclose(file);
}
int Pager::allocSlot() {
    if (freeList != -1) {
        int slot = freeList;
        freeList = pool[slot].nextLRU;
        return slot;
    }
    // evict tail
    int slot = headLRU;
    while (pool[slot].nextLRU != -1) slot = pool[slot].nextLRU;
    if (pool[slot].dirty) {
        fseek(file, pool[slot].pageId * PAGE_SIZE, SEEK_SET);
        fwrite(pool[slot].bytes, 1, PAGE_SIZE, file);
    }
    pool[slot].inUse = false;
    return slot;
}
void Pager::removeFromLRU(int slot) {
    if (pool[slot].prevLRU != -1) pool[pool[slot].prevLRU].nextLRU = pool[slot].nextLRU;
    if (pool[slot].nextLRU != -1) pool[pool[slot].nextLRU].prevLRU = pool[slot].prevLRU;
    if (slot == headLRU) headLRU = pool[slot].nextLRU;
    pool[slot].prevLRU = pool[slot].nextLRU = -1;
}
void Pager::addToHeadLRU(int slot) {
    pool[slot].prevLRU = -1;
    pool[slot].nextLRU = headLRU;
    if (headLRU != -1) pool[headLRU].prevLRU = slot;
    headLRU = slot;
}
Page* Pager::getPage(int pageId) {
    for (int i = 0; i < POOL_PAGES; ++i)
        if (pool[i].inUse && pool[i].pageId == pageId) {
            removeFromLRU(i);
            addToHeadLRU(i);
            return &pool[i];
        }
    int slot = allocSlot();
    fseek(file, pageId * PAGE_SIZE, SEEK_SET);
    fread(pool[slot].bytes, 1, PAGE_SIZE, file);
    pool[slot].pageId = pageId;
    pool[slot].inUse  = true;
    pool[slot].dirty  = false;
    addToHeadLRU(slot);
    return &pool[slot];
}
void Pager::unpinPage(int pageId, bool dirty) {
    for (int i = 0; i < POOL_PAGES; ++i)
        if (pool[i].inUse && pool[i].pageId == pageId) {
            pool[i].dirty |= dirty;
            return;
        }
}