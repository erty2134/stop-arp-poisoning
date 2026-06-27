import ctypes
import ioccom
from socket_ import *
from timeval import *

IFNAMSIZ = 16
bpf_int32 = ctypes.c_int32
bpf_u_int32 = ctypes.c_uint32


# Alignment macros.  BPF_WORDALIGN rounds up to the next
# even multiple of BPF_ALIGNMENT.

BPF_ALIGNMENT = ctypes.sizeof(bpf_int32)

def bpf_wordalign(x):
    return ctypes.c_int32(((x)+(BPF_ALIGNMENT-1))&~(BPF_ALIGNMENT-1))

BPF_MAXINSNS = 512

BPF_MAXBUFSIZE = 0x80000

BPF_MINBUFSIZE = 32

class bf_insns(ctypes.Structure):
    _fields_ = [
        ("code", ctypes.c_ushort),
        ("jt", ctypes.c_char),
        ("jf", ctypes.c_char),
        ("k", bpf_u_int32)
    ]
# Structure for BIOCSETF.
class bpf_program(ctypes.Structure):
    _fields_ = [
        ("bpf_len", ctypes.c_uint),
        ("bpf_insn", ctypes.POINTER(bf_insns))
        # come back to struct bpf_insn *bf_insns; later...
    ]

# Struct returned by BIOCGSTATS.
class bpf_stat(ctypes.Structure):
    _fields_ = [
        ("bs_recv", ctypes.c_uint),
        ("bs_drop", ctypes.c_uint)
    ]

# Struct return by BIOCVERSION.  This represents the version number of
# the filter language described by the instruction encodings below.
# bpf understands a program iff kernel_major == filter_major &&
# kernel_minor >= filter_minor, that is, if the value returned by the
# running kernel has the same major number and a minor number equal
# equal to or less than the filter being downloaded.  Otherwise, the
# results are undefined, meaning an error may be returned or packets
# may be accepted haphazardly.
# It has nothing to do with the source code version.
class bpf_version(ctypes.Structure):
    _fields_ = [
        ("bv_major", ctypes.c_ushort),
        ("bv_minor", ctypes.c_ushort)
    ]

#class ifr_ifru(ctypes.Union): # i dont think we need this union,
#    _fields_ = [
#        ("ifru_addr", sockaddr),
#        ("ifru_dstaddr", sockaddr),
#        ("ifru_broadaddr", sockaddr),
#        ("ifru_flags", ctypes.c_short),
#        ("ifru_metric", ctypes.c_int),
#        ("ifru_mtu", ctypes.c_int),
#        ("ifru_phys", ctypes.c_int),
#        ("ifru_media", ctypes.c_int),
#        ("ifru_intval", ctypes.c_int),
#
#    ]
class ifreq(ctypes.Structure):
    _fields_ = [
        ("ifr_name", ctypes.c_char * IFNAMSIZ),
        ("ifr_ifru", ctypes.c_ubyte * 16)
        # macros dont take memory, so only these are used
    ]

# Structure to retrieve available DLTs for the interface.
class bfl_u(ctypes.Union):
    _layout_ = "ms" # pack only works with micrsoft abi layout although clang uses gcc-syssv
    _pack_ = 4 # pragma pack (4)
    _fields_ = [
        ("bflu_list", ctypes.POINTER(ctypes.c_uint32)),
        ("bflu_pad", ctypes.c_uint64)
    ]
class bpf_dltlist(ctypes.Structure):
    _layout_ = "ms" # pack only works with micrsoft abi layout although clang uses gcc-syssv
    _pack_ = 4 # pragma pack(4)
    _fields_ = [
        ("bfl_len", ctypes.c_uint32),
        ("bfl_u", bfl_u)
    ]

BIOCGBLEN = ioccom.ior('B',102, ctypes.c_uint).value
BIOCSBLEN = ioccom.iowr('B',102, ctypes.c_uint).value
BIOCSETF = ioccom.iow('B',103, bpf_program).value
BIOCFLUSH = ioccom.io('B',104).value
BIOCPROMISC = ioccom.io('B',105).value
BIOCGDLT = ioccom.ior('B',106, ctypes.c_uint).value
BIOCGETIF = ioccom.ior('B',107, ifreq).value
BIOCSETIF = ioccom.iow('B',108, ifreq).value
BIOCSRTIMEOUT = ioccom.iow('B',109, timeval).value
BIOCGRTIMEOUT = ioccom.ior('B',110, timeval).value
BIOCGSTATS = ioccom.ior('B',111, bpf_stat).value
BIOCIMMEDIATE = ioccom.iow('B',112, ctypes.c_uint).value
BIOCVERSION = ioccom.ior('B',113, bpf_version).value
BIOCGRSIG = ioccom.ior('B',114, ctypes.c_uint).value
BIOCSRSIG = ioccom.iow('B',115, ctypes.c_uint).value
BIOCGHDRCMPLT = ioccom.ior('B',116, ctypes.c_uint).value
BIOCSHDRCMPLT = ioccom.iow('B',117, ctypes.c_uint).value
BIOCGSEESENT = ioccom.ior('B',118, ctypes.c_uint).value
BIOCSSEESENT = ioccom.iow('B',119, ctypes.c_uint).value
BIOCSDLT = ioccom.iow('B',120, ctypes.c_uint).value
BIOCGDLTLIST = ioccom.iowr('B',121, bpf_dltlist).value
BIOCSETFNR = ioccom.iow('B', 126, bpf_program).value

#print(BIOCGDLTLIST)

def main() -> int:
    print(BIOCGBLEN,BIOCSBLEN,BIOCSETF,BIOCFLUSH,BIOCPROMISC,BIOCGDLT,BIOCGETIF,BIOCSETIF,BIOCSRTIMEOUT,BIOCGRTIMEOUT,BIOCGSTATS,BIOCIMMEDIATE,BIOCVERSION,BIOCGRSIG,BIOCSRSIG,BIOCGHDRCMPLT,BIOCSHDRCMPLT,BIOCGSEESENT,BIOCSSEESENT,BIOCSDLT,BIOCGDLTLIST,BIOCSETFNR, sep="\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())