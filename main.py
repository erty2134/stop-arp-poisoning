import sys
import os
from datetime import datetime
import cli
import net
from bpf.packets import get_ipv4_address
from ansii import ANSI

def help() -> str:
    """gets help"""
    with open("help.txt", 'r') as f:
        return f.read()

def main(argc: int, argv: list[str]) -> int:
    #check if is using root by checking effective user id (euid)
    if (os.geteuid()!=0):
        print("sudo required.")
        return 1

    # --help flag
    if argc > 0:
        if "--help" in argv or "-h" in argv:
            print("help:")
            print(help())

    commands = cli.CommandSerialization()
    display = cli.Display()

    def initialize_global_data():
        commands.global_data["broadcast"] = []
        commands.global_data["poisoninterval"] = 0.5
        commands.global_data["cleaninterval"] = 2
        commands.global_data["reconnection_interval"] = 2
        commands.global_data["baninterval"] = 1
        commands.global_data["targetip"] = "192.168.54.42"
        commands.global_data["targetmac"] = "0e:d9:6c:6e:44:62"
        # ⌄ cant define it yet cuz my shitty code relys on the 
        # ⌄ Keyerror of when the key doesnt exist in the get command for threads
        # commands.global_data["counter_poison_loops"]
        commands.global_data["counter_poison_loops"] = []
        commands.global_data["clean_arp_caches_loops"] = []
        commands.global_data["counter_reconnect_loops"] = []
        commands.global_data["clientsip"] = []


    @commands.create_command("snapshot")
    def snapshot(statement, command, value):
        # get router ip
        # get target ip
        # get 

        pass

    # placeholder function, isnt called yet
    @commands.create_statement(chr(0b111010)+chr(0b110011))
    def enable_hyperflex_dhcp_mainframe_defense():
        """hackn the mainframe here"""
        def initialize_attack_sequence(rapid_packet_flow_injection_driver: int=213, /, tls_decipher: bool=True):
            dhcp_mainframe_bytecode: list[int] = [
                ((((~58 & 0xFF) ^ 0x2A) << 1) | (((~58 & 0xFF) ^ 0x2A) >> 7)) & 0xFF,#syscall
                ((((~51 & 0xFF) ^ 0x2A) << 1) | (((~51 & 0xFF) ^ 0x2A) >> 7)) & 0xFF#algorithmic_decihper()
            ]#escalation
            FIREWALL: int = 67#firewall_code
            min(*(rapid_packet_flow_injection_driver&tls_decipher, FIREWALL))
            firewall_root_encryption_bypass = [
                (~((((syn_ack_interception >> 1) | (syn_ack_interception << 7)) & 0xFF) ^ 0x2A)) & 0xFF
                for syn_ack_interception in dhcp_mainframe_bytecode
                ]
            display.print("".join([
                chr(spoof_defense_mitigation) 
                for spoof_defense_mitigation in firewall_root_encryption_bypass
                ]))
        initialize_attack_sequence(8945)

    @commands.create_command("poisoninterval")
    def poison_interval(statement, command, value):
        if statement == "set":
            commands.global_data["poisoninterval"] = float(value)
        if statement == "get":
            display.print(commands.global_data["poisoninterval"])
    @commands.create_command("cleaninterval")
    def clean_interval(statement, command, value):
        if statement == "set":
            commands.global_data["cleaninterval"] = float(value)
        if statement == "get":
            display.print(commands.global_data["cleaninterval"])
    @commands.create_command("isolateinterval")
    def clean_interval(statement, command, value):
        if statement == "set":
            commands.global_data["reconnection_interval"] = float(value)
        if statement == "get":
            display.print(commands.global_data["reconnection_interval"])
    @commands.create_command("baninterval")
    def ban_interval(statement, command, value) -> None:
        if statement == "set":
            commands.global_data["baninterval"] = value
        if statement == "get":
            display.print(commands.global_data["baninterval"])

    @commands.create_command("targetip")
    def target_ip(statement, command, value):
        if statement == "set":
            commands.global_data["targetip"] = value
            display.print(f"set targetip '{commands.global_data["targetip"]}'")
        if statement == "get":
            display.print(f"targetip '{commands.global_data["targetip"]}'")

    @commands.create_command("targetmac")
    def target_mac(statement, command, value):
        if statement == "set":
            commands.global_data["targetmac"] = value
            display.print(f"set targetmac '{commands.global_data["targetmac"]}'")
        if statement == "get":
            display.print(f"targetmac '{commands.global_data["targetmac"]}'")

    @commands.create_command("clientsip")
    def clients_ip(statement, command, value):
        if "clientsip" not in commands.global_data: # if it doesnt exists yet
            commands.global_data["clientsip"] = []  # then create it

        if statement == "add":
            commands.global_data["clientsip"].append(value)
        elif statement == "remove":
            commands.global_data["clientsip"].remove(value)
        elif statement == "get":
            try:
                display.print(f"clientips: '{commands.global_data["clientsip"]}'")
            except KeyError:
                display.print(f"clientsip is empty")
            else:
                raise
        else:
            display.print(f"Statement not valid '{statement}'")

    @commands.create_statement("broadcast")
    def broadcast_command() -> None:
        display.print("broadcast start, please wait...")
        net.broadcast_ping()
        arp_table = net.get_arp_cache()
        ips: list[str] = []
        macs: list[str] = []
        for entry in arp_table:
            ips.append(entry[0])
            macs.append(entry[1])
        commands.global_data["broadcast"] = (ips, macs)
        display.print(commands.global_data["broadcast"])
        display.print("broadcast ended")

    @commands.create_command("threads")
    def start_command(statement, command, value) -> None:
        #send broadcast ping to get a big arp cache X

        #   ## counter poisen XX
        # create an arploop X
        #   sends from: new and random un-used mac, every ip on the subnet X
        #   send to: targetmac, targetip X

        #   ## clean arp caches
        # for every ip in arp cache that's under the same subnet # same subnet cuz ar poisening can only happen on the same subnet
        # create another arploop
        #   sends from: router_mac, true_router_ip
        #   sends to: iterations mac, iterations ip

        if statement == "get":
            if len(commands.global_data["counter_poison_loops"]) > 0:
                display.print(f"counter poison: {commands.global_data["counter_poison_loops"]}")                
            else:
                display.print("no counter_poison_loops threads")

            if len(commands.global_data["clean_arp_caches_loops"]) > 0:
                display.print(f"clean cache: {commands.global_data["clean_arp_caches_loops"]}")
            else:
                display.print("no clean_arp_caches_loops threads")

            if len(commands.global_data["counter_reconnect_loops"]) > 0:
                display.print(f"counter reconnect: {commands.global_data["counter_reconnect_loops"]}")
            else:
                display.print("no counter reconnect threads")
            return
        if statement == "stop":
            display.print("stopping threads...")
            for arp_loops in commands.global_data["counter_poison_loops"]:
                arp_loops.stop()
            for arp_loops in commands.global_data["clean_arp_caches_loops"]:
                arp_loops.stop()
            for arp_loops in commands.global_data["counter_reconnect_loops"]:
                arp_loops.stop()
            display.print("all threads stopped")
            return
        if statement == "kill":
            for i, v in enumerate(commands.global_data["counter_poison_loops"]):
                v.stop()
                del commands.global_data["counter_poison_loops"][i]
            for i, v in enumerate(commands.global_data["clean_arp_caches_loops"]):
                v.stop()
                del commands.global_data["clean_arp_caches_loops"][i]
            for i, v in enumerate(commands.global_data["counter_reconnect_loops"]):
                v.stop()
                del commands.global_data["counter_reconnect_loops"][i]
            return

        # get user inputed data
        attacker_ip: str = commands.global_data["targetip"]
        attacker_mac: str = commands.global_data["targetmac"]
        counter_poison_interval = commands.global_data["poisoninterval"]
        arp_clean_interval = commands.global_data["cleaninterval"]
        prevent_reconnection_interval = commands.global_data["reconnection_interval"]

        # get the data for the loops
        if len(commands.global_data["broadcast"]) == 0 and len(commands.global_data["clientsip"]) == 0:
            display.print("Warning! no ips cached, use 'broadcast' or 'add clientsip ...'")
            return
        if len(commands.global_data["clientsip"]) > 0:
            target_client_ips = commands.global_data["clientsip"]
        else:
            ip_cache, mac_cache = commands.global_data["broadcast"]
        router_ip = net.get_router_ip()
        router_mac = net.get_mac_from_ip(router_ip, ips_and_macs=(ip_cache, mac_cache))
        device_subnet: str = net.get_ip().split(sep='.')[2]
        target_client_ips = []

        if len(commands.global_data["clientsip"]) > 0:
            target_client_ips = commands.global_data["clientsip"]
        else:
            ips_on_same_subnet: list[str] = ip_cache
            commands.global_data["counter_poison_loops"] = []
            for ips in ips_on_same_subnet:
                #print(f"ips:'{ips}' == '{router_ip}'\t ips[-3:]:'{ips[-3]}'. ips[-1:]:'{ips[-1]}'")
                if ips == router_ip:
                    print(f"'{ips}' continue ips == router_ip, {ips}=={router_ip}")
                    continue
                if ips[-3:] == "255": # if ip ends in 225 it is a broadcast and we dont wanna muck with it
                    print(f"'{ips}' continue ips[-3:]")
                    continue
                if ips == attacker_ip:
                    print(f"'{ips}' continue ips == attacker_ip")
                    continue
                if ips == net.get_ip():
                    print(f"'{ips}' continue ips == device_ip")
                    continue
                if ips.split(".")[2] != net.get_ip().split(".")[2]: # get the third octet from each ip to compare subnets 
                    print(f"'{ips}' continue ips != net.get_ip(), ips is on wrong subnet")
                    continue
                if ips.split(".")[3] == "0":
                    print(f"'{ips}' continue ips 4th octet == 0, eg ip == 192.168.67.0")
                    continue
                if ips == net.get_ip_from_mac(attacker_mac, (ip_cache, mac_cache)):
                    print(f"'{ips}' continue ips == true_attacker_ip")
                    continue
                target_client_ips.append(ips)
        display.print("finshed getting client ips")

        unused_mac_all: list[str] = []
        # send -counter- poison to the attacker
        # create loops
        display.print("Initializing counter poison threads")
        bpf_counter_poison = net.BerkleyPacketFilter()
        for ips in target_client_ips:
            unused_mac = net.get_unasigned_mac(mac_list=mac_cache+unused_mac_all)
            unused_mac_all.append(unused_mac)
            arploop: net.ArpLoop = net.ArpLoop(
                bpf_counter_poison,
                ips,
                unused_mac,
                attacker_ip,
                attacker_mac,
                interval=counter_poison_interval
            )
            commands.global_data["counter_poison_loops"].append(arploop)
            del arploop
            display.print(f"poison: {ips} bound to {unused_mac}, real {net.get_mac_from_ip(ips, ips_and_macs=(ip_cache, mac_cache))} > for {attacker_ip}, {attacker_mac}")
        # start the loops
        display.print("starting counter poison...")
        for arp_loops in commands.global_data["counter_poison_loops"]:
            arp_loops.start()
        display.print("finished counter poison")

        # clean arp caches of victims
        # create loops
        display.print("Initializing arp cache cleaning threads")
        bpf_clean_cache: net.BerkleyPacketFilter = net.BerkleyPacketFilter()
        commands.global_data["clean_arp_caches_loops"] = []
        for ips in target_client_ips:
            unused_mac = net.get_unasigned_mac(mac_list=mac_cache+unused_mac_all)
            # appends all unused macs to a list so it doesnt regenerate an unused mac when calling get_unasigned_mac()
            unused_mac_all.append(unused_mac) 
            arploop: net.ArpLoop = net.ArpLoop(
                bpf_clean_cache,
                router_ip,
                router_mac,
                ips,
                net.get_mac_from_ip(ips, ips_and_macs=(ip_cache, mac_cache)),
                interval=arp_clean_interval
            )
            commands.global_data["clean_arp_caches_loops"].append(arploop)
            del arploop
        # start loops
        display.print("starting arp cache cleaning")
        for arp_loops in commands.global_data["clean_arp_caches_loops"]:
            arp_loops.start()

        # prevent reconnection
        # create loops
        display.print("Initializing counter reconnect loops")
        bpf_prevent_reconnect: net.BerkleyPacketFilter = net.BerkleyPacketFilter()
        for ips in target_client_ips:
            unused_mac = net.get_unasigned_mac(mac_list=mac_cache+unused_mac_all)
            unused_mac_all.append(unused_mac)
            display.print(f"poison: {attacker_ip} bound to {unused_mac}, real {attacker_mac} > for {ips}, {net.get_mac_from_ip(ips,ips_and_macs=(ip_cache, mac_cache))}")
            arploop: net.ArpLoop = net.ArpLoop(
                bpf_prevent_reconnect,
                attacker_ip,
                unused_mac,
                ips,
                net.get_mac_from_ip(ips, ips_and_macs=(ip_cache, mac_cache)),
                interval=prevent_reconnection_interval
            )
            commands.global_data["counter_reconnect_loops"].append(arploop)
        # start loops
        for arp_loops in commands.global_data["counter_reconnect_loops"]:
            arp_loops.start()

        try:
            display.print(f"arp_ips {ip_cache}")
        except UnboundLocalError: # this is raised if arp_ips doesnt exist
            display.print(f"arp_ips None, because custom clientip list used")
        display.print(f"device_subnet {device_subnet}")
        display.print(f"target_client_ips {target_client_ips}")
        display.print("All threads running.")

    @commands.create_command("ban")
    def ban_command(statement, command, value):
        ip_cache, mac_cache = commands.global_data["broadcast"]
        unused_mac = net.get_unasigned_mac(mac_list=mac_cache) 
        # shouldnt be an issue that the unused mac is being used in both the poisons
        router_ip = net.get_router_ip()
        router_mac = net.get_mac_from_ip(router_ip, ips_and_macs=(ip_cache, mac_cache))
        attacker_ip = commands.global_data["targetip"]
        attacker_mac = commands.global_data["targetmac"]
        
        bpf_ban_attacker: net.BerkleyPacketFilter = net.BerkleyPacketFilter()
        ban_poison_attacker: net.ArpLoop = net.ArpLoop(
            bpf_ban_attacker,
            deviceIp=router_ip, 
            deviceMac=unused_mac, 
            sendToIp=attacker_ip, 
            sendToMac=attacker_mac,
            interval=commands.global_data["baninterval"]
            )
        ban_poison_router: net.ArpLoop = net.ArpLoop(
            bpf_ban_attacker,
            deviceIp=attacker_ip,
            deviceMac=unused_mac,
            sendToIp=router_ip,
            sendToMac=router_mac
        )

        if statement == "get":
            display.print(f"ban: spoofing attacker is {ban_poison_attacker.is_alive()}, spoofing router is {ban_poison_router.is_alive()}")
        if statement == "start":
            ban_poison_attacker.start()
            display.print(f"spoof, {router_ip} at {ANSI.ITALIC.value}{unused_mac}{ANSI.END.value}{ANSI.DIM.value} (real '{router_mac}') for '{attacker_ip}' at '{attacker_mac}'")
            ban_poison_router.start()
            display.print(f"spoof, {attacker_ip} at {ANSI.ITALIC.value}{unused_mac}{ANSI.END.value}{ANSI.DIM.value} (real '{attacker_mac}') for '{router_ip}' at '{router_mac}'")
        if statement == "stop":
            ban_poison_attacker.stop()
            ban_poison_router.stop()
            display.print("stopped 2 threads. arp caches have not and will not be cleaned by this script!")

    @commands.create_statement("help")
    def help_statement():
        display.print(help())
    
    # idk how to make an alias :(
    @commands.create_statement("quit")
    def exit_statement():
        display.print("exiting...")
        sys.exit(0)
    @commands.create_statement("exit")
    def exit_statement():
        display.print("exiting...")
        sys.exit(0)

    # setup cli
    COLOUR = ANSI.YELLOWBG.value + ANSI.BLACK.value
    display.prefix = f"{ANSI.YELLOWBG.value}{datetime.now().strftime("%H:%M:%S")}{COLOUR} 〉{ANSI.BOLD.value}{net.get_ip()}{ANSI.END.value}{ANSI.YELLOW.value} » {ANSI.END.value}"
    display.suffix = f"{ANSI.END.value}\n"
    display.prePrint = f"{ANSI.DIM.value}"
    display.preInput = f"{ANSI.BOLD.value}"

    display.print("Stop Arp Poisoning, Welcome")
    initialize_global_data()
    while True:
        # v sets the prefix again to update time
        display.prefix = f"{ANSI.YELLOWBG.value}{datetime.now().strftime("%H:%M:%S")}{COLOUR} 〉{ANSI.BOLD.value}{net.get_ip()}{ANSI.END.value}{ANSI.YELLOW.value} » {ANSI.END.value}"
        try:
            user_input = display.input()
        except KeyboardInterrupt: # graceful keyboard interupt
            print("\n") # adds extra line because ^C doesnt create new line
            continue
            display.print("quitting...")
            return 1
        error: str = commands.update(user_input)
        if error:
            display.print(error)

if __name__ == "__main__": 
    raise SystemExit(main(len(sys.argv), sys.argv))