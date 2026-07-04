import ctypes

sa_family_t = ctypes.c_uint8

class sockaddr(ctypes.Structure):
    _fields_ = [
        ("sa_len", ctypes.c_uint8),
        ("sa_family", sa_family_t),
        ("sa_data", ctypes.c_char*4)
    ]
