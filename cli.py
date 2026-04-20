import sys

class Display:
    def __init__(self)->None:
        self.prefix:str="";
        self.suffix:str="";
        self.prePrint="";
        self.preInput="";
        self.flush:bool=True
    
    def print(self,*args):
        listArgs=list(args);
        sys.stdout.write(self.prefix);
        sys.stdout.write(self.prePrint);
        for i,v in enumerate(listArgs):
            listArgs[i]=str(listArgs[i]);
        sys.stdout.write(''.join(listArgs));
        if (self.flush): sys.stdout.flush();
        sys.stdout.write(self.suffix+"\n"); # <---- contains a \n so there is an empty line bewteen every line
        if (self.flush): sys.stdout.flush();#       The input method creates its own new line when the user 
                                            #       clicks enter. 
    def input(self,*args)->str:
        sys.stdout.write(self.prefix);  # writes the prefix
        sys.stdout.write(self.preInput);# writes preinput 
        listArgs=list(args);
        for i,v in enumerate(listArgs): # converts *args into a single string to be printed
            listArgs[i]=str(listArgs[i]);
        sys.stdout.write(''.join(listArgs));
        sys.stdout.flush();
        read:str=sys.stdin.readline();
        sys.stdout.write(self.suffix);
        if (self.flush): sys.stdout.flush();
        return read;

# its worth noting that these two classes are complety independent from eachother.

class CommandSerialization:
    """
    ## Command Serialization
    #### create commands in there own scope and function
    - @create_command(command_name)
    - self.global_data: list, use this for object scope data
    - update(input), run this whenever you want to use any command
    
    idk if serialization is the correct word for this.\n
    but basically u can use deccorator to define \n
    commands in their own functions. This is \n
    because when i was creating a previous project \n
    i fell into an error where varible names between \n
    commands would get mixed up. so giving each \n
    command their own function means that they have \n
    there own scope.
    """
    @staticmethod
    def _parse_input(input_: str)->tuple[str,str,str]:
        """doesnt parse value
        returns: statement, command, value
        """
        statement = input_.split()[0]
        command = input_.split()[1]
        value = input_.split(maxsplit=3)[2]
        return statement, command, value

    def __init__(self):
        self.global_data: dict[str] = {}
        self._functions: list = []
        self._commands: list = []

    def create_command(self, command_name):
        def wrapper(fn):
            self._commands.append(command_name)
            self._functions.append(fn)
        return wrapper
    
    def update(self, input_) -> str:
        """checks for first instance of command and runs it.\n
        returns the error message"""
        try: CommandSerialization._parse_input(input_)
        except: return "Error: Not enough inputs, requires: statement command value"

        for i,v in enumerate(self._commands):
            if v == CommandSerialization._parse_input(input_)[1]:
                statement, command, value = CommandSerialization._parse_input(input_)
                self._functions[i](statement, command, value)
                return;
    
        return f"Error: command not found '{CommandSerialization._parse_input(input_)[1]}'"


def main() -> None:
    inputComands = CommandSerialization()

    @inputComands.create_command("targetip")
    def targetip(statement, command, value) -> None:
        if statement == "set":
            inputComands.global_data["targetip"] = value
            print(f"set ip '{inputComands.global_data["targetip"]}'")
        elif statement == "get":
            print("get ip")

    @inputComands.create_command("targetmac")
    def targetmac(statement, command, value) -> None:
        if statement == "set":
            print("set mac")

    while True:
        print(inputComands.update(input_ = input("in: ")))

if __name__ == "__main__": main()