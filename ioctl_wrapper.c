//ioctl_wrapper.c
#include <sys/ioctl.h>
#include <net/bpf.h>
#include <net/if.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>

// wrapper to access bpf (cbpf) ioctls in python.
const int biocflush = BIOCFLUSH;
const int biocgblen = BIOCGBLEN;
const int biocgdlt = BIOCGDLT;
const int biocgdltlist = BIOCGDLTLIST;
const int biocgetif = BIOCGETIF;
const int biocghdrcmplt = BIOCGHDRCMPLT;
const int biocgrsig = BIOCGRSIG;
const int biocgrtimeout = BIOCGRTIMEOUT;
const int biocgseesent = BIOCGSEESENT;
const int biocgstats = BIOCGSTATS;
const int biocimmediate = BIOCIMMEDIATE;
const int biocpromisc = BIOCPROMISC;
const int biocsblen = BIOCSBLEN;
const int biocsdlt = BIOCSDLT;
const int biocsetf = BIOCSETF;
const int biocsetfnr = BIOCSETFNR;
const int biocsetif = BIOCSETIF;
const int biocshdrcmplt = BIOCSHDRCMPLT;
const int biocsrsig = BIOCSRSIG;
const int biocsrtimeout = BIOCSRTIMEOUT;
const int biocsseesent = BIOCSSEESENT;
const int biocversion = BIOCVERSION;
const int so_bindtodevice = SO_BINDTODEVICE; // idk what this is, i just put it here cuz it was under all the other iotcls



//printf("0x%lx\n", BIOCSETIF);
int main(){
    struct ifreq ifr;
    //ifr_name
    strcpy(ifr.ifr_name, "en0");
    //printf("ifreq (class-like): '%lu'\n", sizeof(struct ifreq));
    printf("ifr (object-like): '%lu'\n", sizeof(ifr));
    printf("ifr_name (%s): '%lu'\n", ifr.ifr_name, sizeof(ifr.ifr_name));
    printf("Field ifr_name is stored at: %p\n", (void*)&ifr.ifr_name);
    printf("Field ifr is at offset: %zu bytes\n", offsetof(struct ifreq, ifr_name));
    //printf("ifr_ifru (%s): '%lu'\n", ifr.ifr_ifru, sizeof(ifr.ifr_ifru));
    return 0;
}