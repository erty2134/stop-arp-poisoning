# stop-arp-poisoning
basic scapy-based tool that removes arp poisoning based mitms by arp poisoning the attacker and cleaning arp caches of effected devices through forged (technically poisoned) arp packets

doesnt work on fullduplex or internal yet (bettercap)

how to use:
create a python venv and download the requirements
python 3.14
⚠️ before any mitms note down the routers mac address



## Setup

#### 1. get attackers mac address
run this terminal command
```zsh
arp -a
```
note the attackers mac address, the mac will be the one associated with the routers ip


#### 2. escape the mitm with static arp entry
run this command to setup a static arp entry (11:22:33:44:55:66 is my routers ip)
```zsh
arp -s 192.168.54.1 11:22:33:44:55:66
```
replace the mac at the end of the command with the routers mac address


#### 3. get ip of the attacker
now that we have escaped his attack, lets find the attacker ip
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
set targetip 192.168.54.42
```


#### 6. start threads
this will run defense on whole subnet
```
start threads
```

it will take ~34.2 seconds to fininish broadcasting the network because it sends 2 rounds of broadcast arp packets to the whole network to wake up all devices on the network then sends another 2 rounds of broadcast arp packets to get the ip and mac of all devices.

after that the rest of the steps should be instant.

if anything doesnt work create an issue on my github