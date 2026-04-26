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