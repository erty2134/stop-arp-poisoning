import sys
import os
import errno
import fcntl
import struct
import ctypes
libioctl_wrapper = ctypes.CDLL("./libioctl_wrapper.dylib") # load c wrapper

# set bpf ioctl
BIOCSETIF = ctypes.c_int32.in_dll(libioctl_wrapper, "biocsetif").value
BIOCIMMEDIATE = ctypes.c_uint32.in_dll(libioctl_wrapper, "biocimmediate").value
BIOCPROMISC = ctypes.c_uint32.in_dll(libioctl_wrapper, "biocpromisc").value
BIOCGBLEN = ctypes.c_uint32.in_dll(libioctl_wrapper, "biocgblen").value

class BpfDevice:
    def __init__(self, file_descriptor=None):
        if file_descriptor != None: # if custom file descriptor, return before get_bpf()
            self.file_descriptor = file_descriptor
            return
        self.file_descriptor, self.device_name, self.file_object = self.get_bpf()
        
    @staticmethod
    def get_bpf() -> tuple[int,str, any] | None:
        """
        gets an available bpf and returns its file descriptor, device name, file object\n
        if no file descript is found it will return 'None', make \n
        sure you check for this in your code
        """
        file_descriptor:int=None
        for i in range(0,257):
            try:
                file_object = None
                file_descriptor = os.open(f"/dev/bpf{i}", os.O_RDWR)
                bpf_device = f"bpf{i}"
                break
            except OSError as e:
                if e.errno == errno.EBUSY: # EBUSY is the erno that is returned if a bpf is being used. refer to BPF(4) description
                    continue
                raise e
        if (file_descriptor==None):
            pass # returns None still. I am thinking of changing it so il keep this here
        return file_descriptor, bpf_device, file_object

    def close(self):
        os.close(self.file_descriptor)

    # use ioctl biosetif to bind it to an interface
    def bind_to_interface(self, interface:bytes) -> None:
        #class ifreq(ctypes.Structure):
        #    _fields_ = [("ifr_name", ctypes.c_char*16)]
        #ifr = ifreq() #struct ifreq ifr;
        #ctypes.memset(ctypes.byref(ifr), 0, ctypes.sizeof(ifr)) #memset(&ifr, 0, sizeof(ifr));
        #ifr.ifr_name=b"en0"#ctypes.memmove(ifr.ifr_name, "en0", ctypes.sizeof(ifr.ifr_name)-1) #strncpy(ifr.ifr_name, "en0", sizeof(ifr.ifr_name) - 1);
        #ioctl(fd, BIOCSETIF, &ifr)
        ###ifreq = struct.pack("s", interface) # man states that ifreq needs to be a C struct
        fcntl.ioctl(self.file_object, BIOCSETIF, struct.pack("16s",b"en0"))
        
    def set_immediate_mode(self, is_enabled:bool):
        fcntl.ioctl(BIOCIMMEDIATE, self.file_descriptor, bytes(is_enabled))
    def set_biocpromisc_mode(self, is_enabled:bool):
        fcntl.ioctl(BIOCPROMISC, self.file_descriptor, is_enabled)

    def read(self) -> bytes:
        length = fcntl.ioctl(self.file_descriptor,BIOCGBLEN)
        return os.read(self.file_descriptor,length)
    
    #def __del__(self):
    #    os.close(self.file_descriptor)


def main(argc:int, argv:list[str]) -> None:
    my_bpf = BpfDevice()
    print(my_bpf.file_descriptor, my_bpf.device_name, my_bpf.file_object)
    my_bpf.bind_to_interface("en0")
    my_bpf.set_immediate_mode(True)
    print(my_bpf.file_descriptor, my_bpf.device_name)
    print(my_bpf.read())
    my_bpf.close()

    #my_bpf.bind_to_interface("en0")
    #my_bpf.set_immediate_mode(True)
    #my_bpf.set_biocpromisc_mode(False)
    #my_bpf.read();

if (__name__=="__main__"): main(len(sys.argv), sys.argv)