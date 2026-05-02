import sys
import os
from datetime import datetime
import cli
import net
from ansii import ANSI

def help() -> str:
    """gets help"""
    with open("help.txt", 'r') as f:
        return f.read()

def main(argc: int, argv: list[str]) -> None:
    #check if is using root by checking effective user id (euid)
    if (os.geteuid()!=0):
        raise PermissionError("Permsion denied. USE SUDO!!");

    # --help flag
    if argc > 0:
        if "--help" in argv or "-h" in argv:
            display.print("help:")
            display.print(help())

    commands = cli.CommandSerialization()
    display = cli.Display()

    COLOUR = ANSI.YELLOWBG.value + ANSI.BLACK.value
    display.prefix = f"{COLOUR}{datetime.now().strftime("%H:%M:%S")}||{ANSI.BOLD.value}{net.get_ip()}{ANSI.END.value}{COLOUR} › {ANSI.END.value}"
    display.suffix = f"{ANSI.END.value}\n"
    display.prePrint = f"{ANSI.DIM.value}"
    display.preInput = f"{ANSI.BOLD.value}"

    @commands.create_command("snapshot")
    def snapshot(statement, command, value):
        # get router ip
        # get target ip
        # get 

        pass

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
            display.print("stopping threads")
            for arp_loops in commands.global_data["counter_poison_loops"]:
                arp_loops.stop()
            for arp_loops in commands.global_data["clean_arp_caches_loops"]:
                arp_loops.stop()
            return


        attacker_ip: str = commands.global_data["targetip"]
        attacker_mac: str = commands.global_data["targetmac"]

        counter_poison_interval = 2
        arp_clean_interval = 5

        # get the data for the loops
        net.broadcast_ping()
        arp_ips: list = net.get_arp_cache()[0]
        device_subnet: str = net.get_ip().split(sep='.')[2]
        ips_on_same_subnet: list[str] = [i for i in arp_ips if f".{device_subnet}." in i]
        commands.global_data["counter_poison_loops"] = []
        router_ip = net.get_router_ip()
        router_mac = net.get_mac_from_ip(router_ip)

        # counter poisen the attacker
        # create loops
        target_client_ips = ips_on_same_subnet
        if len(commands.global_data["clientsip"]) > 0:
            target_client_ips = commands.global_data["clientsip"]
        for ips in target_client_ips:
            if ips == router_ip:
                continue
            unused_mac = net.get_unasigned_mac()
            commands.global_data["counter_poison_loops"].append(net.ArpLoop(ips, unused_mac, attacker_ip, attacker_mac, interval=counter_poison_interval))
            print(">>>"+ips+" >>>"+unused_mac)
        # start the loops
        for arp_loops in commands.global_data["counter_poison_loops"]:
            arp_loops.start()

        # clean arp caches of victims
        # create loops
        #"""
        commands.global_data["clean_arp_caches_loops"] = []
        for ips in target_client_ips:
            if ips == router_ip or ips == attacker_ip:
                continue
            unused_mac = net.get_unasigned_mac()
            commands.global_data["clean_arp_caches_loops"].append(net.ArpLoop(router_ip, router_mac, ips, net.get_mac_from_ip(ips), interval=arp_clean_interval))
        # start loops
        for arp_loops in commands.global_data["clean_arp_caches_loops"]:
            arp_loops.start()
        #"""

        display.print(arp_ips)
        display.print(device_subnet)
        display.print(target_client_ips)

    @commands.create_statement("help")
    def help_statement():
        display.print(help())
    
    # idk how to make an alias :(
    @commands.create_statement("quit")
    def exit_statement():
        display.print("exiting...")
        sys.exit()
    @commands.create_statement("exit")
    def exit_statement():
        display.print("exiting...")
        sys.exit()

    display.print("Stop Arp Poisoning, Welcome")
    while True:
        # v sets the prefix again to update time
        display.prefix = f"{COLOUR}{datetime.now().strftime("%H:%M:%S")}||{ANSI.BOLD.value}{net.get_ip()}{ANSI.END.value}{COLOUR} › {ANSI.END.value}"
        try:
            user_input = display.input()
        except KeyboardInterrupt: # gracefull keyboard interupt
            print("\n") # adds extra line because ^C doesnt create new line like [ENTER]
            display.print("quitting...")
            sys.exit()
        error: str = commands.update(user_input)
        if error:
            display.print(error)

if __name__ == "__main__": 
    main(len(sys.argv), sys.argv)