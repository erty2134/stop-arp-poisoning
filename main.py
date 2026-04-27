import sys
import os
from datetime import datetime
import cli
import net
from ansii import ANSI

def main(argc: int, argv: list[str]) -> None:
    #check if is using root by checking effective user id (euid)
    if (os.geteuid()!=0):
        raise PermissionError("Permsion denied. USE SUDO!!");

    commands = cli.CommandSerialization()
    display = cli.Display()

    COLOUR = ANSI.YELLOWBG.value + ANSI.BLACK.value
    display.prefix = f"{COLOUR}{datetime.now().strftime("%H:%M:%S")}||{ANSI.BOLD.value}{net.get_ip()}{ANSI.END.value}{COLOUR} › {ANSI.END.value}"
    display.suffix = f"{ANSI.END.value}\n"
    display.prePrint = f"{ANSI.DIM.value}"
    display.preInput = f"{ANSI.BOLD.value}"

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
            command.global_data["targetmac"] = value
            display.print(f"set targetmac '{commands.global_data["targetmac"]}'")
        if statement == "get":
            display.print(f"targetmac '{command.global_data["targetmac"]}'")

    @commands.create_command("clientsip")
    def clients_ip(statement, command, value):
        if statement == "add":
            command.global_data["clientsip"].append(value)
        if statement == "remove":
            command.global_data["clientsip"].remove(value)
        if statement == "get":
            display.print(f"clientips: '{command.global_data["clientsip"]}'")

    @commands.create_statement("start")
    def start_command():
        #send broadcast ping to get a big arp cache

        #   ## counter poisen
        # create an arploop
        #   sends from: new and random un-used mac, every ip on the subnet
        #   send to: targetmac, targetip

        #   ## clean arp caches
        # for every ip in arp cache that's under the same subnet # same subnet cuz ar poisening can only happen on the same subnet
        # create another arploop
        #   sends from: router_mac, true_router_ip
        #   sends to: iterations mac, iterations ip

        attacker_ip: str = commands.global_data["targetip"]
        attacker_mac: str = commands.global_data["targetmac"]

        counter_poisen_interval = 2
        arp_clean_interval = 5

        # counter poisen
        # get the data for the loops
        net.broadcast_ping()
        arp_ips: list = net.get_arp_cache()[0]
        device_subnet: str = net.get_ip().split(sep='.')[2]
        ips_on_same_subnet: list = [i for i in arp_ips if f".{device_subnet}." in i]
        counter_poisen_loops: list = []
        for ip in ips_on_same_subnet:
            unused_mac = net.get_unasigned_mac()
            counter_poisen_loops.append(net.ArpLoop(ip, unused_mac, attacker_ip, attacker_mac, interval=counter_poisen_interval))
        # start the loops
        for arp_loop in counter_poisen_loops:
            # dont wanna start this yet so i will run foo instead of start
            # also i will remove the print later
            display.print(arp_loop.foo()) 

        display.print(arp_ips)
        display.print(device_subnet)
        display.print(ips_on_same_subnet)

        #for i in range(2):
        #    counter_poisen_loops.append(net.ArpLoop())

    @commands.create_statement("help")
    def help_statement():
        display.print("Help...")
    
    # idk how to make an alias :(
    @commands.create_statement("quit")
    def exit_statement():
        display.print("exiting...")
        sys.exit()
    @commands.create_statement("exit")
    def exit_statement():
        display.print("exiting...")
        sys.exit()

    display.print("Send Arp Packets, Welcome")
    while True:
        # v sets the prefix again to update time
        display.prefix = f"{COLOUR}{datetime.now().strftime("%H:%M:%S")}||{ANSI.BOLD.value}{net.get_ip()}{ANSI.END.value}{COLOUR} › {ANSI.END.value}"
        user_input = display.input()
        error: str = commands.update(user_input)
        if error:
            display.print(error)

if __name__ == "__main__": 
    main(len(sys.argv), sys.argv)