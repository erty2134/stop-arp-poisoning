import sys
import os
from datetime import datetime
import cli
import net
from ansii import ANSI
import cProfile

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
            display.print("help:")
            display.print(help())

    commands = cli.CommandSerialization()
    display = cli.Display()

    @commands.create_command("snapshot")
    def snapshot(statement, command, value):
        # get router ip
        # get target ip
        # get 

        pass

    @commands.create_command("poisoninterval")
    def poison_interval(statement, command, value):
        if statement == "set":
            command.global_data["poiseninterval"] = value

    @commands.create_command("cleaninterval")
    def clean_interval(statement, command, value):
        if statement == "set":
            command.global_data["cleaninterval"] = value

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

    @commands.create_command("threads")
    def start_command(statement, command, value):
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
            try:
                display.print(f"counter poison: {commands.global_data["counter_poison_loops"]}")
            except KeyError:
                display.print("no counter_poison_loops threads")
            try:
                display.print(f"clean cache: {commands.global_data["clean_arp_caches_loops"]}")
            except KeyError:
                display.print("no clean_arp_caches_loops threads")
            return
        if statement == "stop":
            display.print("stopping threads...")
            for arp_loops in commands.global_data["counter_poison_loops"]:
                arp_loops.stop()
            for arp_loops in commands.global_data["clean_arp_caches_loops"]:
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
            return

        # get user inputed data
        try:
            attacker_ip: str = commands.global_data["targetip"]
        except KeyError:
            attacker_ip: str = net.get_router_ip()
        attacker_mac: str = commands.global_data["targetmac"]
        counter_poison_interval = 2
        arp_clean_interval = 5

        if value == "auto":
            attacker_ip = net.get_router_ip()
            attacker_mac = net.get_mac_from_ip(attacker_ip) # doesnt work because it would return the routers true mac if device has static arp entries
            counter_poison_interval = 2
            arp_clean_interval = 5

        # get the data for the loops
        router_ip = net.get_router_ip()
        router_mac = net.get_mac_from_ip(router_ip)
        device_subnet: str = net.get_ip().split(sep='.')[2]
        target_client_ips = []
        try:
            commands.global_data["counter_poison_loops"]
        except KeyError:
            commands.global_data["counter_poison_loops"] = []
        try:
            if len(commands.global_data["clientsip"]) > 0:
                target_client_ips = commands.global_data["clientsip"]
        except KeyError:
            display.print("broadcast start, please wait...")
            net.broadcast_ping(subnet_scan=True)
            display.print("broadcast ended")
            arp_ips: list = net.get_arp_cache()[0]
            ips_on_same_subnet: list[str] = [i for i in arp_ips if f".{device_subnet}." in i]
            commands.global_data["counter_poison_loops"] = []
            for ips in ips_on_same_subnet:
                #print(f"ips:'{ips}' == '{router_ip}'\t ips[-3:]:'{ips[-3]}'. ips[-1:]:'{ips[-1]}'")
                if ips == router_ip:
                    print(f"'{ips}' continue ips == router_ip, {ips}=={router_ip}")
                    continue
                if ips[-3:] == "255": # if ip ends in 225 it is a broadcast and we dont wanna muck with it
                    print(f"'{ips}' continue ips[-3:]")
                    continue
                if ips[-1:] == "0" and ips[-2:] == ".": # if ip ends in 0 it is maybe broadcast? and i dont wanna muck with it
                    print(f"'{ips}' continue ips[-1:] == 0")
                    continue
                if ips[-1:] == "1" and ips[-2:] == ".": # if ip ends in 1 it is maybe router? and i dont wanna muck with it
                    print(f"'{ips}' continue ips[-1:] == 1")
                    continue
                if ips == attacker_ip:
                    print(f"'{ips}' continue ips == attacker_ip")
                    continue 
                if net.get_mac_from_ip(ips, do_ping=False) == "(incomplete)": # well then the ip doesnt exist
                    #print(f"'{ips}' continue incpmplee")
                    pass
                target_client_ips.append(ips)
        display.print("finshed getting client ips")

        # counter poison the attacker
        # create loops
        display.print("Initializing counter poison threads")
        for ips in target_client_ips:
            #unused_mac = net.get_unasigned_mac()
            unused_mac = net._random_mac()
            commands.global_data["counter_poison_loops"].append(net.ArpLoop(ips, unused_mac, attacker_ip, attacker_mac, interval=counter_poison_interval))
            display.print(f"poison: {ips} bound to {unused_mac}, real net.get_mac_from_ip(ips)")
        # start the loops
        display.print("starting counter poison...")
        for arp_loops in commands.global_data["counter_poison_loops"]:
            arp_loops.start()
        display.print("finished counter poison")

        # clean arp caches of victims
        # create loops
        display.print("Initializing arp cache cleaning threads")
        commands.global_data["clean_arp_caches_loops"] = []
        for ips in target_client_ips:
            #unused_mac = net.get_unasigned_mac()
            unused_mac = net._random_mac()
            commands.global_data["clean_arp_caches_loops"].append(net.ArpLoop(router_ip, router_mac, ips, net.get_mac_from_ip(ips, do_ping=False), interval=arp_clean_interval))
        # start loops
        display.print("starting arp cache cleaning")
        for arp_loops in commands.global_data["clean_arp_caches_loops"]:
            arp_loops.start()

        try:
            display.print(f"arp_ips {arp_ips}")
        except UnboundLocalError: # this is raised if arp_ips doesnt exist
            display.print(f"arp_ips None, because custom clientip list used")
        display.print(f"device_subnet {device_subnet}")
        display.print(f"target_client_ips {target_client_ips}")
        display.print("All threads running.")

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
    display.prefix = f"{COLOUR}{datetime.now().strftime("%H:%M:%S")} 〉{ANSI.BOLD.value}{net.get_ip()}{ANSI.END.value}{ANSI.YELLOW.value} » {ANSI.END.value}"
    display.suffix = f"{ANSI.END.value}\n"
    display.prePrint = f"{ANSI.DIM.value}"
    display.preInput = f"{ANSI.BOLD.value}"

    display.print("Stop Arp Poisoning, Welcome")
    while True:
        # v sets the prefix again to update time
        display.prefix = f"{COLOUR}{datetime.now().strftime("%H:%M:%S")} 〉{ANSI.BOLD.value}{net.get_ip()}{ANSI.END.value}{ANSI.YELLOW.value} » {ANSI.END.value}"
        try:
            user_input = display.input()
        except KeyboardInterrupt: # graceful keyboard interupt
            print("\n") # adds extra line because ^C doesnt create new line like [ENTER]
            display.print("quitting...")
            return 1
        error: str = commands.update(user_input)
        if error:
            display.print(error)

if __name__ == "__main__": 
    sys.exit(main(len(sys.argv), sys.argv))