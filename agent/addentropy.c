#include <linux/random.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <string.h>

int addEntropyRaw(const char* data, int size) {
    int fd = open("/dev/urandom", O_RDWR);
    if(fd < 0)
        return -1;
    struct {
        int ent_count;
        int size;
        unsigned char data[1024];
    } entropy;
    if(size > sizeof(entropy.data))
        size = sizeof(entropy.data);
    entropy.size = size;
    entropy.ent_count = size * 8;
    memcpy(entropy.data, data, size);
    int res = ioctl(fd, RNDADDENTROPY, &entropy);
    close(fd);
    return res;
}
