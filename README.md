# stop-arp-poisoning
macos only Berkley Packet Filter tool that removes arp poisoning by sending multiple different types of spoofed arp packets to prevent arp poisoning from mitm tools like bettercap. This has been tested on Bettercap version v2.41.5 and with macos version 26.2 and only uses dependecies that are builtin to macos: route, arp, ifconfig, grep, ping.
I have tested against bettercap with halfduplex, fullduplex and internal, and got 0% packetloss.

how to use:
python 3.14.3 anything above 3 should work

⚠️ before any mitms note down the routers mac address
⚠️ during mitm before and during running the script use a static arp entry to defend your own computer from an mitm


## Setup

#### 1. get attackers mac address
run this terminal command
```zsh
arp -a
```
note the attackers mac address, the mac will be the one associated with the routers ip during an active mitm else it would just return the routers mac address


#### 2. escape the mitm with static arp entry
run this command to setup a static arp entry (11:22:33:44:55:66 is my routers mac)
```zsh
arp -s 192.168.54.1 11:22:33:44:55:66
```
replace the mac at the end of the command with the routers mac address


#### 3. get ip of the attacker
now that we have escaped the attackers arp poison, lets find the attackers ip
run arp -a again
```zsh
arp -a
```
his ip will be the one associated with his mac address we found in step 1



## script
#### 4. run with sudo
```zsh
sudo python3 main.py
```


#### 5. give the script the mac address and ip of the attacker
run this command but change the mac to the attackers mac from step 1
```
set targetmac 0e:d9:6c:6e:44:62
```

run this command but with the attackers ip from step 3
```
set targetip 192.168.54.67
```

#### 6. discover all devices on network
this will unicast icmp ping every device on the subnet
```
broadcast
```


#### 6. start threads
this will run defense on whole subnet
```
start threads
```

it will take ~5 seconds to fininish broadcasting the subnet because of the timeout time for the devices that dont exist on your subnet

## bugs
if anything doesnt work create an issue on this repo on github.