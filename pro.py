#!.venv/bin/python3
# author is gale williams
"""Tiny macOS/BSD BPF reader using Python.

This demonstrates:

1. open /dev/bpfN
2. BIOCSETIF with struct ifreq to bind an interface
3. BIOCIMMEDIATE so reads return as packets arrive
4. BIOCGBLEN to discover the kernel read buffer size
5. read() packet records prefixed with struct bpf_hdr

Run on macOS with enough permission to open /dev/bpf*, for example:

    ./bsd_bpf_sniff.py --constants-only
    sudo ./bsd_bpf_sniff.py lo0 --count 3
    sudo ./bsd_bpf_sniff.py en0 --count 3
"""

from __future__ import annotations

import argparse
import array
import ctypes
import errno
import fcntl
import os
import platform
import select
import struct
import sys


IFNAMSIZ = 16
BPF_ALIGNMENT = 4

IOC_VOID = 0x20000000
IOC_OUT = 0x40000000
IOC_IN = 0x80000000
IOC_INOUT = IOC_IN | IOC_OUT
IOCPARM_MASK = 0x1FFF


class IfReq(ctypes.Structure):
    """Darwin struct ifreq layout for BIOCSETIF.

    The real C type is:

        char ifr_name[IFNAMSIZ];
        union { ... } ifr_ifru;

    BIOCSETIF only needs ifr_name, but the ioctl command encodes
    sizeof(struct ifreq), so the Python object must match that ABI size.
    On modern macOS, IFNAMSIZ is 16 and the union is 16 bytes.
    """

    _fields_ = [
        ("ifr_name", ctypes.c_char * IFNAMSIZ),
        ("ifr_ifru", ctypes.c_char * 16),
    ]


def _ioc(direction: int, group: str, number: int, size: int) -> int:
    return (
        direction
        | ((size & IOCPARM_MASK) << 16)
        | (ord(group) << 8)
        | number
    )

def _ior(group: str, number: int, ctype: type[ctypes._SimpleCData] | type[ctypes.Structure]) -> int:
    return _ioc(IOC_OUT, group, number, ctypes.sizeof(ctype))


def _iow(group: str, number: int, ctype: type[ctypes._SimpleCData] | type[ctypes.Structure]) -> int:
    return _ioc(IOC_IN, group, number, ctypes.sizeof(ctype))


BIOCGBLEN = _ior("B", 102, ctypes.c_uint)
BIOCSETIF = _iow("B", 108, IfReq)
BIOCIMMEDIATE = _iow("B", 112, ctypes.c_uint)


def bpf_wordalign(value: int) -> int:
    return (value + (BPF_ALIGNMENT - 1)) & ~(BPF_ALIGNMENT - 1)


def open_bpf() -> int:
    first_error: OSError | None = None

    for index in range(256):
        path = f"/dev/bpf{index}"
        try:
            return os.open(path, os.O_RDWR)
        except OSError as error:
            if error.errno == errno.EBUSY:
                continue
            if first_error is None:
                first_error = error
            if error.errno == errno.ENOENT:
                break

    if first_error is not None:
        raise first_error

    raise FileNotFoundError("No /dev/bpf* device was available")


def bind_interface(fd: int, interface: str) -> None:
    encoded = interface.encode("utf-8")
    if len(encoded) >= IFNAMSIZ:
        raise ValueError(
            f"Interface name {interface!r} is too long for IFNAMSIZ={IFNAMSIZ}"
        )

    request = IfReq()
    request.ifr_name = encoded
    fcntl.ioctl(fd, BIOCSETIF, bytes(request))


def set_immediate(fd: int) -> None:
    value = array.array("I", [1])
    fcntl.ioctl(fd, BIOCIMMEDIATE, value, True)


def get_buffer_length(fd: int) -> int:
    value = array.array("I", [0])
    fcntl.ioctl(fd, BIOCGBLEN, value, True)
    return int(value[0])


def iter_bpf_records(buffer: bytes):
    offset = 0

    while offset + 18 <= len(buffer):
        tv_sec, tv_usec, caplen, datalen, hdrlen = struct.unpack_from(
            "IIIIH", buffer, offset
        )
        packet_start = offset + hdrlen
        packet_end = packet_start + caplen
        if hdrlen < 18 or packet_end > len(buffer):
            break

        yield tv_sec, tv_usec, caplen, datalen, buffer[packet_start:packet_end]
        offset += bpf_wordalign(hdrlen + caplen)


def sniff(interface: str, count: int, timeout: float) -> None:
    fd = open_bpf()
    try:
        bind_interface(fd, interface)
        set_immediate(fd)
        buffer_length = get_buffer_length(fd)

        print(f"bound /dev/bpf fd {fd} to {interface}")
        print(f"kernel BPF read buffer length: {buffer_length} bytes")

        seen = 0
        while seen < count:
            readable, _, _ = select.select([fd], [], [], timeout)
            if not readable:
                print(
                    f"timed out after {timeout:g}s waiting for packets on {interface}; "
                    "try generating traffic on that interface"
                )
                return

            data = os.read(fd, buffer_length)
            for tv_sec, tv_usec, caplen, datalen, packet in iter_bpf_records(data):
                seen += 1
                preview = packet[:24].hex(" ")
                print(
                    f"{seen:03d} {tv_sec}.{tv_usec:06d} "
                    f"captured={caplen} original={datalen} bytes "
                    f"first_bytes={preview}"
                )
                if seen >= count:
                    break
    finally:
        os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read a few packets through classic BSD BPF on macOS."
    )
    parser.add_argument(
        "interface",
        nargs="?",
        default="lo0",
        help="interface to bind, such as lo0 or en0",
    )
    parser.add_argument("--count", type=int, default=5, help="packets to print")
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="seconds to wait for each read before giving up",
    )
    parser.add_argument(
        "--constants",
        action="store_true",
        help="print computed ABI constants before sniffing",
    )
    parser.add_argument(
        "--constants-only",
        action="store_true",
        help="print computed ABI constants and exit before opening /dev/bpf*",
    )
    args = parser.parse_args()

    if platform.system() != "Darwin":
        print("This example targets macOS/Darwin classic BSD BPF.", file=sys.stderr)
        return 2

    if args.constants or args.constants_only:
        print(f"sizeof(IfReq): {ctypes.sizeof(IfReq)}")
        print(f"BIOCSETIF:    0x{BIOCSETIF:08x}")
        print(f"BIOCIMMEDIATE:0x{BIOCIMMEDIATE:08x}")
        print(f"BIOCGBLEN:    0x{BIOCGBLEN:08x}")

    if args.constants_only:
        return 0

    try:
        sniff(args.interface, args.count, args.timeout)
    except PermissionError as error:
        print(
            f"permission denied opening/configuring /dev/bpf*: {error}. "
            "Run with sufficient privileges, commonly sudo on macOS.",
            file=sys.stderr,
        )
        return 1
    except OSError as error:
        print(f"BPF setup/read failed: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())