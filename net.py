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
conf.verb = 0

def get_ip()->str:
    """returns ip as string, uses scapy"""
    return get_if_addr(conf.iface)

def send_arp_request(
        target_mac=None, 
        sender_mac=get_if_hwaddr("en0"), 
        sender_ip=get_if_addr("en0"), 
        target_ip=None
        ):
    """returns scapy sr1 ans"""
    arp = Ether( # pyright: ignore[reportUndefinedVariable]
        dst = target_mac,
        src = sender_mac
        )/ARP( # pyright: ignore[reportUndefinedVariable]
        hwsrc = sender_mac,
        psrc = sender_ip,
        hwdst = target_mac,
        pdst = target_ip
        )
    return sr1(arp) 

def _random_mac()->str:
    mac:str = ""
    for i in range(6):
        digit = random.randint(0,225)
        digit = hex(digit)
        mac = f"{mac}{digit[2:]}:" # get rid of 0x at start of digit
    mac = mac[:-1] # remove the final colon
    return mac

def get_arp_cache():
    """returns list of ips [0] and list of macs [1]"""
    arp_cache = subprocess.run(["arp","-a"], capture_output = True, text = True).stdout
    ip_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    mac_pattern = re.compile(r".{1,2}:.{1,2}:.{1,2}:.{1,2}:.{1,2}:.{1,2}")
    ips = ip_pattern.findall(arp_cache)
    macs = mac_pattern.findall(arp_cache)
    return ips, macs

def broadcast_ping():
    """
    internal, gets arp cache and searchs for ff:ff:ff:ff:ff:ff \n 
    then pings the related ip
    """
    ips, macs = get_arp_cache()
    broadcast_ip = None
    for i,v in enumerate(macs):
        if v == "ff:ff:ff:ff:ff:ff":
            broadcast_ip = ips[i]
    subprocess.run(["ping", "-c", "1", broadcast_ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #return sr1(IP(dst=broadcast_ip)/ICMP()) # pyright: ignore[reportUndefinedVariable]

def get_unasigned_mac():
    """returns mac addr that is not in the given list"""
    broadcast_ping() # fill arp cache first
    mac_list: list[str] = get_arp_cache()[1]
    mac = None
    while mac == None:
        rand_mac = _random_mac()
        if not rand_mac in mac_list:
            mac = rand_mac
    return mac
    
class ArpLoop(threading.Thread):
    """Creates an object that constantly sends arp packets\n
    - run() to start the loop
    - and stop() to stop the loop
    - arp packets are sent every interval \n
    """
    def __init__(self, deviceIp: str, deviceMac: str, sendToIp: str, sendToMac: str, interval: float = 0.5)->None:
        super().__init__(daemon=True)
        self._exit = threading.Event()
        self.deviceIp = deviceIp
        self.deviceMac = deviceMac
        self.sendToIp = sendToIp
        self.sendToMac = sendToMac
        self._interval = interval
    def run(self):
        while not self._exit.is_set():
            send_arp_request(self.deviceIp,self.deviceMac,self.sendToIp,self.sendToMac)
            time.sleep(self._interval)
    def stop(self):
        self._exit.set()
    def foo(self):
        return ("bar")