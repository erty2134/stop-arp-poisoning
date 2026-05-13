"""
Scapy based module contains 4 functions and one Class\n
- get_ip\n
- send_arp_request\n
- get_arp_cache\n
- get_unasigned_mac\n
- ArpLoop (this is the class)\n
"""
from scapy.all import *
import threading
import time
import random
import subprocess
import re
import time
conf.verb = 0

def get_router_ip() -> str:
    """returns routers ip as string"""
    return conf.route.route("0.0.0.0")[2]

def get_ip(split:bool = False) -> str | list[str]:
    """returns ip as string, uses scapy. or list str if split"""
    if split:
        return get_if_addr(conf.iface).split(sep=".")
    return get_if_addr(conf.iface)

def send_arp_request(
        target_mac=None, 
        sender_mac=get_if_hwaddr("en0"), 
        sender_ip=get_if_addr("en0"), 
        target_ip=None,
        oper: int=1
        ) -> PacketList | None:
    """returns scapy sr1 ans"""
    arp = Ether(
        dst = target_mac,
        src = sender_mac
        )/ARP(
        op=oper,
        hwsrc = sender_mac,
        psrc = sender_ip,
        hwdst = target_mac,
        pdst = target_ip
        )
    return sendp(arp)

def _random_mac()->str:
    mac:str = ""
    for i in range(6):
        digit = random.randint(0,225)
        digit = hex(digit)
        mac = f"{mac}{digit[2:]}:" # get rid of 0x at start of digit
    mac = mac[:-1] # remove the final colon
    return mac

def get_arp_cache(system=False) -> tuple[list[str], list[str]]:
    """
    returns list of ips [0] and list of macs [1] from os arp cache.\n
    Dont use this. This is bad and slow and uses subproccess instead of scapy
    """
    arp_cache = subprocess.run(["arp","-an"], capture_output = True, text = True).stdout
    ip_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    mac_pattern = re.compile(r"at\s(.*?)\son")
    ips = ip_pattern.findall(arp_cache)
    macs = mac_pattern.findall(arp_cache)
    return ips, macs

def broadcast_ping() -> tuple[list]:
    """
    broadcast arp ping who-has on whole network and returns ips and macs
    """
    # arp ping every device    
    #create packets
    packets: list = []
    for i in range(0,256): # doesnt skips .255
        # create send to ip
        ip_split: list[str] = get_ip(split=True)
        ip_split.pop() # remove final octate
        ip_split.append(str(i)) # add i as final octet
        ip: str = '.'.join(ip_split) # make string again
        
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip, op=1)
        packets.append(pkt)
    #send and wait for packets
    response, _ = srp(packets, timeout=6, retry=3, inter=0.01) # three trys with 6s waits inbetween because of Wi-Fi low-power mode, this ensures all devices are discovered
    response_ip = []
    response_mac = []
    for i, pkt in enumerate(response):
        print(f"{i} {pkt.answer.psrc}, {pkt.answer.src}\n")
        response_ip.append(pkt.answer.psrc)
        response_mac.append(pkt.answer.src)
    return (response_ip, response_mac)

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
        mac: str = None
        ips, macs = ips_and_macs
        for i,v in enumerate(ips):
            if v == ip:
                mac = macs[i]
        return mac
    
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
    
class ArpLoop(threading.Thread):
    """Creates an object that constantly sends arp packets\n
    - run() to start the loop
    - and stop() to stop the loop
    - arp packets are sent every interval \n
    """
    def __init__(self, deviceIp: str, deviceMac: str, sendToIp: str, sendToMac: str, interval: float = 0.5) -> None:
        super().__init__(daemon=True)
        self._exit = threading.Event()
        self.deviceIp = deviceIp
        self.deviceMac = deviceMac
        self.sendToIp = sendToIp
        self.sendToMac = sendToMac
        self._interval = interval
    def run(self) -> None:
        while not self._exit.is_set():
            send_arp_request(self.sendToMac,self.deviceMac,self.deviceIp,self.sendToIp, oper=2)
            time.sleep(self._interval)
    def stop(self) -> None:
        self._exit.set()
    def foo(self) -> None:
        return ("bar")
    
def main():
    ips, macs = broadcast_ping()
    get_mac_from_ip("192.168.54.105", ips_and_macs=(ips, macs))

if __name__ == "__main__": main()