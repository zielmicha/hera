#include <stdlib.h>

void *dlopen(const char *filename, int flag) {
    abort();
}

char *dlerror(void) {
    abort();
}

void *dlsym(void *handle, const char *symbol) {
    abort();
}

int dlclose(void *handle) {
    abort();
}
