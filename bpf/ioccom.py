import ctypes


uint32_t = ctypes.c_uint32


# Ioctl's have the command encoded in the lower word, and the size of
# any in or out parameters in the upper word.  The high 3 bits of the
# upper word are used to encode the in/out status of the parameter.

IOCPARM_MASK: int = uint32_t(0x1fff) # parameter length, at most 13 bits

def iocparm_len(x: int) -> uint32_t:
    return uint32_t(((x) >> 16) & IOCPARM_MASK)

def iocbasecmd(x) -> uint32_t:
    return uint32_t((x) & ~(IOCPARM_MASK << 16))

def iocgroup(x) -> uint32_t:
    return uint32_t(((x) >> 8) & 0xff)


IOCPARM_MAX: uint32_t = uint32_t(IOCPARM_MASK.value + 1) # max size of ioctl args
# no parameters
IOC_VOID: uint32_t = uint32_t(0x20000000)
# copy parameters out
IOC_OUT: uint32_t = uint32_t(0x40000000)
# copy parameters in
IOC_IN: uint32_t = uint32_t(0x80000000)
# mask for IN/OUT/VOID
IOC_INOUT = uint32_t(IOC_IN.value|IOC_OUT.value)


def ioc(inout, group, num, len) -> uint32_t:
    return uint32_t(inout.value | ((len & IOCPARM_MASK.value) << 16) | (ord(group) << 8) | (num))

def io(g, n) -> uint32_t:
    return ioc(IOC_VOID, (g), (n), 0)

def ior(g, n, t) -> uint32_t:
    return ioc(IOC_OUT, (g), (n), ctypes.sizeof(t))

def iow(g, n, t) -> uint32_t:
    return ioc(IOC_IN, (g), (n), ctypes.sizeof(t))

# this should be _IORW, but stdio got there first # but we dont got stdlib but to keep it consisnent we going with _IOWR
def iowr(g, n, t) -> uint32_t:
    return ioc(IOC_INOUT, (g), (n), ctypes.sizeof(t))


def main():
    class ioctl_data(ctypes.Structure):
        _fields_ = [
            ("x", uint32_t)
        ]

    iowr_test: uint32_t = iowr('M', 1, ioctl_data);
    print("iowr_test",iowr_test.value)

    io_test = io('M',2)
    print("io_test",io_test.value)
    
    ior_test = ior('M',2,ioctl_data)
    print("ior_test",ior_test.value)

    iow_test = iow('M',2,ioctl_data)
    print("iow_test",iow_test.value)


if __name__ == "__main__":
    main()