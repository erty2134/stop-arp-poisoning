import ctypes

__darwin_time_t = ctypes.c_long # line 119, arm/_types.h
__darwin_suseconds_t = ctypes.c_long # line 86, sys/_types.h

class timeval(ctypes.Structure):
    _fields_ = [
        ("tv_sec", ctypes.c_int64), # int instead of int32 because line 30 in sys/_types/_int32_t.h where it says typedef int int32_t;
        ("tv_usec", ctypes.c_int64)
   
    ]