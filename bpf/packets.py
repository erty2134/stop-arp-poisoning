import struct
import subprocess
import sys
from enum import Enum

def get_ipv4_address():
    output = subprocess.run(
        ("ipconfig", "getifaddr", "en0"),
        capture_output = True,
        shell=False,
        text=True
    )

    ip = output.stdout[:-1] # remove the \n
    return ip

def get_mac_address(interface: str="en0") -> str:
    if not isinstance(interface, str):
        raise TypeError("Interface must be string type")
    
    ifconfig_output = subprocess.Popen(
        ("ifconfig", interface),
        stdout=subprocess.PIPE,
        text=True
    )
    
    grep_output = subprocess.Popen(
        ("grep", "ether"),
        stdin=ifconfig_output.stdout,
        stdout=subprocess.PIPE,
        text=True
    )
    
    stdoutput = grep_output.communicate()[0]
    mac = stdoutput[len(" ether "):-1]
    return mac

def ascii_to_ethernet(ascii_mac: str) -> bytes:
    clean: str = ascii_mac.replace(":", "").lower()
    if len(clean) != 12:
        raise ValueError("Invalid MAC address length")
    ethernet_address: bytes = bytes.fromhex(clean)
    return ethernet_address

def ip_string_to_bytes(ip_string: str) -> bytes:
    """ipv4. size is how many bytes long you want ur ip to be packed into. uses big endian"""
    ip_octet_split = ip_string.split(".")
    
    ip_bytes: bytearray = bytearray()
    for octet in ip_octet_split:
        #print(int(octet),sys.getsizeof(int(octet)))
        byte_octet = int(octet).to_bytes(1, "big")
        #ip_bytes[:0] = byte_octet
        ip_bytes.extend(byte_octet)

    return bytes(ip_bytes)

class Ether_Types(Enum):
    IPV4: int = 0x0800
    IPV6: int = 0x86DD
    ARP: int= 0x0806
    WOL: int= 0x0842
    ETHERNET_FLOW_CONTROL: int = 0x8808

class Ethernet_Frame:
    """
    Ethernet frame for writing to bpf. use dot bytes when sending
    """
    def __init__(self, payload: bytes | str, dst: str, src: str, ether_type: int) -> None:
        self.payload: bytes
        if isinstance(payload, bytes):
            self.payload = payload
        elif isinstance(payload, str): # if the user just wants to send a message like 'Hello!' to the other computer. we will allow them to use a str
            self.payload = payload.encode("utf-8")
        else:
            raise ValueError("'payload' must be Bytes or Str!")
        
        self.dst: bytes = ascii_to_ethernet(dst)
        self.src: bytes = ascii_to_ethernet(src)
        self.ether_type: bytes = ether_type.to_bytes(2, "big")

        self.bytes_: bytes = struct.pack(
            f">6s6s2s{len(self.payload)}s",
            self.dst,
            self.src,
            self.ether_type,
            self.payload
        )

class Arp_Payload:
    def __init__(
        self,
        tha: str, 
        tpa: str,
        htype: int = 1,
        ptype: int = 0x0800,
        hlen: int = 6,
        plen: int = 4,
        oper: int = 2,
        sha: str = get_mac_address("en0"),
        spa: str = get_ipv4_address()
    ) -> None:

        self.htype: int = htype
        self.ptype: int = ptype
        self.hlen: int = hlen
        self.plen: int = plen
        self.oper: int = oper
        self.sha: bytes = ascii_to_ethernet(sha)
        self.spa: bytes = ip_string_to_bytes(spa)
        self.tha: bytes = ascii_to_ethernet(tha)
        self.tpa: bytes = ip_string_to_bytes(tpa)

        self.bytes_: bytes = struct.pack(
            ">HHBBH6s4s6s4s",
            self.htype,
            self.ptype,
            self.hlen,
            self.plen,
            self.oper,
            self.sha,
            self.spa,
            self.tha,
            self.tpa
        )

class Arp_Packet:
    """creates an arp packet by encapsulating an arp packet (arp_payload object) into an ethernet frame"""
    def __init__(
        self,
        tha: str,
        tpa: str,
        htype: int = 1,
        ptype: int = 0x0800,
        hlen: int = 6,
        plen: int = 4,
        oper: int = 2,
        sha: str = get_mac_address("en0"),
        spa: str = get_ipv4_address()
    ) -> None:

        self.arp_payload = Arp_Payload(
            tha,
            tpa,
            htype,
            ptype,
            hlen,
            plen,
            oper,
            sha,
            spa
        )
        
        self.ethernet = Ethernet_Frame(
            self.arp_payload.bytes_,
            tha,
            sha,
            Ether_Types.ARP.value
        )
        
        self.bytes_ = self.ethernet.bytes_


def main():
    my_ips: list[str] = [
        "123.456.1.1",
        "123.456.1.22",
        "123.456.22.1",
        "123.456.22.22",
    ]
    #ip_string_to_bytes("192.168.54.412", size=6)
    for i in my_ips:
        ip_string_to_bytes(i)
        print()

if __name__ == "__main__" : main()