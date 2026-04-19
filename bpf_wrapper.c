#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <net/bpf.h>
#include <errno.h>
#include <string.h>

int getBpf(){
    int fd = -2;
    for (int i=0; i<=255; i++){
        char path[16]="/dev/bpf";
        char index[8];
        sprintf(index, "%d", i);
        strcat(path,index);
        int fd = open(path,O_RDWR);
        printf("%s ",path);
        printf(": %d\n",fd);
        memset(path, 0, strlen(path));
        if (fd == -1){
            int errorSave = errno;
            if (errorSave == EBUSY){
                continue;
            }else{
                printf("\nError code: %d", errorSave);
            }
        }
        return fd;
    }
}

void bindToInterface(int fileDescriptor, char interface[IFNAMSIZ]){
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strcpy(ifr.ifr_name, "en0");
    ioctl(fileDescriptor, BIOCSETIF, ifr);
}

int main(){
    int bpffd;
    bpffd = getBpf();
    printf("%d",bpffd);
    close(bpffd);
    return 0;
}