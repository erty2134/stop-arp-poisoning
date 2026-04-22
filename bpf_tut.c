#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>
#include <net/if.h>
#include <net/bpf.h>
#include <string.h>

int main(){
    int fd;
    char path[16];
    for (int i = 0; i > 254; i++){
        sprintf(path, "/dev/bpf%d", i);
        fd = open(path, O_RDWR);

        if (fd != -1){
            break;
        }
    }
    printf("fd: %d", fd);

    const char *interface = "en0";
    struct ifreq ifr;

    strcpy(ifr.ifr_name, interface);
    if (ioctl(fd, BIOCSETIF, &ifr) > 0){
        return -1;
    }

    int bufLen = 1;
    if (ioctl(fd, BIOCIMMEDIATE, &bufLen) == -1){
        return -1;
    }

    if (ioctl(fd, BIOCGBLEN, &bufLen) == -1){
        return -1;
    }

    char read_buffer[128];
    read(fd, read_buffer,128);
    printf("buffer: '%s'",read_buffer);

    close(fd);
}