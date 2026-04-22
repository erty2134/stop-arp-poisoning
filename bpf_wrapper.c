#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <net/bpf.h>
#include <errno.h>
#include <string.h>

int getBpf(){
    
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