import sys
import os
import errno
import fcntl
import struct
import ctypes
libioctl_wrapper = ctypes.CDLL("./libioctl_wrapper.dylib") # load c wrapper

BIOCSETIF = ctypes.c_int32.in_dll(libioctl_wrapper, "biocsetif").value
BIOCIMMEDIATE = ctypes.c_uint32.in_dll(libioctl_wrapper, "biocimmediate").value
BIOCPROMISC = ctypes.c_uint32.in_dll(libioctl_wrapper, "biocpromisc").value
BIOCGBLEN = ctypes.c_uint32.in_dll(libioctl_wrapper, "biocgblen").value

file_descriptor:int = None
bpf_device:str = None
for i in range(0,257):
    try:
        file_descriptor = os.open(f"/dev/bpf{i}", os.O_RDWR)
        bpf_device = f"bpf{i}"
        break
    except OSError as e:
        if e.errno == errno.EBUSY: # EBUSY is the erno that is returned if a bpf is being used. refer to BPF(4) description
            continue
        #else:
        raise e

# lets bind
iface = bytes("en0","utf-16")
SIZE: int = 32 # from C, the struct ifreq is 32 bytes
ifreq = struct.pack( f"{SIZE}b", *b'en0', *b'\x00'*(SIZE-len(iface)))
fcntl.ioctl(file_descriptor, BIOCSETIF, ifreq)

os.close(file_descriptor)