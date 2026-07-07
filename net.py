"""
Bpf based module contains 4 functions and one Class\n
- get_ip\n
- send_arp_request\n
- get_arp_cache\n
- get_unasigned_mac\n
- ArpLoop (this is the class)\n
"""
import threading
import time
import random
import subprocess
import re
import time
import os
import errno
import fcntl
import ctypes
import struct
from bpf import bpf, packets

def get_router_ip() -> str:
    """
    returns routers ip as string, 
    route -n get default | grep gateway
    """
    output: subprocess.Popen = subprocess.Popen(("route", "-n", "get", "default"), stdout=subprocess.PIPE, text=True)
    gateway: subprocess.Popen = subprocess.Popen(["grep", "gateway"], stdin=output.stdout, stdout=subprocess.PIPE, text=True)
    
    # [0] communicate returns output to 0, and error to 1. 
    # [len("   gateway: ")] this removes the word gateway from the output. 
    # [:-1] removes the \n at the end
    ip: str = gateway.communicate()[0][len("    gateway: "):][:-1]
    
    output.stdout.close()
    return ip

def get_ip() -> str:
    """returns ip as string from bpf.packets which gets it from ipconfig"""
    return packets.get_ipv4_address()

def _random_mac()->str:
    mac:str = ""
    for i in range(6):
        digit = random.randint(0,225)
        digit = hex(digit)
        mac = f"{mac}{digit[2:]}:" # get rid of 0x at start of digit
    mac = mac[:-1] # remove the final colon
    return mac

def get_arp_cache() -> list[tuple[str, str]]:
    """
    returns list of tuples (ip, mac) from os arp cache.\n
    """
    arp_cache = subprocess.run(["arp","-an"], capture_output = True, text = True).stdout
    
    ip_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    mac_pattern = re.compile(r"[1234567890abcdef]{1,2}:[1234567890abcdef]{1,2}:[1234567890abcdef]{1,2}:[1234567890abcdef]{1,2}:[1234567890abcdef]{1,2}:[1234567890abcdef]{1,2}", flags=re.I) # i for no case sensi
    
    arp_table: list[tuple[str, str]] = []
    for line in arp_cache.splitlines():
        if "(incomplete)" in line:
            continue
        ip_in_line: str = ip_pattern.search(line).group(0)
        mac_in_line: str = mac_pattern.search(line).group(0)

        arp_table.append((ip_in_line, mac_in_line))

    return arp_table

def broadcast_ping() -> tuple[list]:
    """
    broadcast icmp ping on whole subnet and update kernel arp cache from subprocess
    """
    # get all ips on subnet
    ip_list: list[str] = []
    for i in range(0,256): # from 0 to 255
        # create send to ip
        ip: str = packets.get_ipv4_address()
        ip_split: list[str] = ip.split('.')
        ip_split.pop() # remove last octate
        ip_split.append(str(i)) # add i as final octet
        ip: str = '.'.join(ip_split) # make string again
        ip_list.append(ip)
    
    # start a Popen ping for each ip
    ping_proccesses: list[subprocess.Popen] = []
    for ip in ip_list:
        # uses a tuple instead of a list in subprocess.Popen because tuples are slightly faster 
        # than lists and i want as much speed as possible for this cuz its normally pretty slow
        ping_proccesses.append(subprocess.Popen(("ping", "-c", "1", "-W", "500", ip), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    # wait for all proccesses to finish
    for process in ping_proccesses:
        process.wait()
    
def get_unasigned_mac(mac_list: list[str]|None = None) -> str:
    """returns mac addr that is not in the given list, run broadcast first"""
    if not mac_list:
        mac_list: list[str] = get_arp_cache()[1] # legacy

    mac: str = None
    while mac == None:
        rand_mac = _random_mac()
        if not rand_mac in mac_list:
            mac = rand_mac
    return mac

def get_ip_from_mac(mac: str, ips_and_macs: tuple[list[str],list[str]]):
    if ips_and_macs:
        ip: str = None
        ips, macs = ips_and_macs
        for i,v in enumerate(macs):
            if v == mac:
                ip = ips[i]
        return ip

def get_mac_from_ip(ip:str, /, do_ping=True, ips_and_macs: tuple[list[str],list[str]]=None) -> str:
    """
    returns mac as a strin, set ips_and_macs to a tuple containing\n
    two lists of ips and macs respectively
    """
    if ips_and_macs:
        mac: str | None = None
        ips, macs = ips_and_macs
        for i,v in enumerate(ips):
            if v == ip:
                mac = macs[i]
        return mac
    
    print("LEGACY")
    # legacy version
    mac = None
    if do_ping:
        ping = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if ping.returncode == -1:
            print("SUBPROCESS PING FAILED") # add real error handling later
            raise
    ips, macs = get_arp_cache()
    for i,v in enumerate(ips):
        if v == ip:
            mac = macs[i]
    #mac_pattern = re.compile(rf"{ip} .{1,2}:.{1,2}:.{1,2}:.{1,2}:.{1,2}:.{1,2}")
    return mac

class BerkleyPacketFilter():
    @classmethod
    def get_max_bpf(cls) -> int:
        output: str = subprocess.run(["sysctl", "debug.bpf_maxdevices"], capture_output=True).stdout
        max_bpfs: int = int(output[len("debug.bpf_maxdevices: "):])
        return max_bpfs
    
    @classmethod
    def open_bpf(cls) -> tuple[int, int]:
        """
        returns fd, bpf_index
        """
        fd: int | None = None
        for i in range(0, BerkleyPacketFilter.get_max_bpf()+1):
            bpf_num: int = i
            try:
                fd: int = os.open(f"/dev/bpf{i}", os.O_RDWR)
                if fd:
                    break
            except OSError as e:
                if e.errno == errno.EBUSY:
                    continue
                raise e
        if fd == None:
            raise RuntimeError("No BPFs available")
        return fd, bpf_num
    
    def __init__(self) -> None:
        self.bpf = BerkleyPacketFilter.open_bpf()
        self.fd = self.bpf[0]
        self.index = self.bpf[1]

    def __del__(self) -> None:
        os.close(self.fd)
        
    
class ArpLoop(threading.Thread):
    """Creates an object that constantly sends arp packets\n
    - run() to start the loop
    - and stop() to stop the loop
    - arp packets are sent every interval \n
    """
    def __init__(
        self,
        bpf_device: BerkleyPacketFilter | int, 
        
        deviceIp: str,
        deviceMac: str,
        sendToIp: str,
        sendToMac: str,

        interval: float = 0.5
    ) -> None:
        super().__init__(daemon=True)
        self._exit = threading.Event()
        self.deviceIp: str = deviceIp
        self.deviceMac: str = deviceMac
        self.sendToIp: str = sendToIp
        self.sendToMac: str = sendToMac
        self._interval: float = interval

        if isinstance(bpf_device, BerkleyPacketFilter):
            self.bpf: BerkleyPacketFilter = bpf_device
            self.bpf_fd: int = self.bpf.fd
            self.bpf_index: int = self.bpf.index
        else:
            self.bpf_fd: int = bpf_device

        self.ifr: bpf.ifreq = bpf.ifreq()
        self.ifr.ifr_name = b"en0"
        fcntl.ioctl(self.bpf_fd, bpf.BIOCSETIF, self.ifr, True)

        buf_immediate: ctypes.c_int = ctypes.c_uint()
        fcntl.ioctl(self.bpf_fd, bpf.BIOCIMMEDIATE, buf_immediate, True)

        buf_len: ctypes.c_int = ctypes.c_uint(1)
        fcntl.ioctl(self.bpf_fd, bpf.BIOCGBLEN, buf_len, True)

        header_complete = ctypes.c_uint(1)
        fcntl.ioctl(self.bpf_fd, bpf.BIOCSHDRCMPLT, header_complete, True)



    def send_arp_request(
        self,
        target_mac=None, 
        sender_mac=packets.get_mac_address(), 
        sender_ip=packets.get_ipv4_address(), 
        target_ip=None,
        oper: int=1
    ) -> None:
        arp =  packets.Arp_Packet(
            tha=target_mac,
            tpa=target_ip,
            oper=oper,
            sha=sender_mac,
            spa=sender_ip
        )
        os.write(self.bpf_fd, arp.bytes_)

    def run(self) -> None:
        while not self._exit.is_set():
            self.send_arp_request(self.sendToMac,self.deviceMac,self.deviceIp,self.sendToIp, oper=2)
            time.sleep(self._interval)
    def stop(self) -> None:
        self._exit.set()
    def foo(self) -> None:
        return ("bar")
    
def main() -> None:
    bpf_fd = BerkleyPacketFilter.open_bpf()[0] # 0 is the fd

    ifr: bpf.ifreq = bpf.ifreq()
    ifr.ifr_name = b"en0"
    fcntl.ioctl(bpf_fd, bpf.BIOCSETIF, ifr, True)
    #buf_immediate: ctypes.c_int = ctypes.c_uint()
    #fcntl.ioctl(bpf_fd, bpf.BIOCIMMEDIATE, buf_immediate, True)
    #buf_len: ctypes.c_int = ctypes.c_uint(1)
    #fcntl.ioctl(bpf_fd, bpf.BIOCGBLEN, buf_len, True)

    header_complete = ctypes.c_uint(1)
    fcntl.ioctl(bpf_fd, bpf.BIOCSHDRCMPLT, header_complete, True)


    pay = "hello".encode("utf-8")
    frame: bytes = struct.pack(
        f">6s6s2s{len(pay)}s",
        packets.ascii_to_ethernet("b6:ac:31:43:11:ee"), # dst
        packets.ascii_to_ethernet("11:22:33:44:55:66"), # src
        0x0801.to_bytes(2, "big"),
        pay
    )

    try:
        #my_ethernet = packets.Ethernet_Frame(b"Hello!", "22:22:22:33:33:33", "1a:64:b6:c3:b:13", ether_type=0x0801)
        os.write(bpf_fd, frame)
    except:
        raise
    finally:
        os.close(bpf_fd)
    return None
    my_loop: ArpLoop = ArpLoop(
        bpf_device=BerkleyPacketFilter(),
        deviceIp= "192.168.54.67",
        deviceMac="11:22:33:44:55:66",
        sendToIp="192.168.54.42",
        sendToMac="b8:27:eb:74:f2:6c",
        interval=1
    )
    my_loop.run()

if __name__ == "__main__": 
    main()