import sys
import datetime
import cli
import net
from ansii import ANSI

def main(argc: int, argv: list[str]) -> None:
    commands = cli.CommandSerialization()
    display = cli.Display()

    COLOUR = ANSI.YELLOWBG.value + ANSI.BLACK.value
    display.prefix = f"{COLOUR}{datetime.now().strftime("%H:%M:%S")}||{ANSI.BOLD.value}{net.get_ip}{ANSI.END.value}{COLOUR} › {ANSI.END.value}"
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

    display.print("Send Arp Packets, Welcome")
    while True:
        # v sets the prefix again to update time
        display.prefix = f"{COLOUR}{datetime.now().strftime("%H:%M:%S")}||{ANSI.BOLD.value}{net.get_ip}{ANSI.END.value}{COLOUR} › {ANSI.END.value}"
        user_input = display.input()
        commands.update(user_input)

if __name__ == "__main__": 
    main(len(sys.argv), sys.argv)