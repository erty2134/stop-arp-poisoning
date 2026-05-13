"""
Module includes 2 seperate Classes:\n
- Display for cli printing and inputing\n
- CommandSerialization for creating commands\n
"""
import sys

class Display:
    def __init__(self)->None:
        self.prefix:str="";
        self.suffix:str="";
        self.prePrint="";
        self.preInput="";
        self.flush:bool=True
    
    def print(self,*args):
        """prints prefix, preprint, *args (in this order)"""
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
        """writes prefix, prininput, *args (in this order)"""
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
    #### create commands in functions
    - @create_command(command_name), creates a three (but allows two) part command. 
    it has a statement(statement_name), command, value structure eg: set targetfile words.txt
    - @create_statement is a single word command eg: help, run, exit
    - self.global_data: list, use this for object scope data
    - update(input), run this whenever you want to use any command
    
    idk if serialization is the correct word for this.\n
    but basically u can use deccorator to define \n
    commands in their own functions. This is \n
    because when i was creating a previous project \n
    i fell into an error where varible names between \n
    commands would get mixed up because i used if statement\n
    chains to create commands meaning all varibles were\n
    in the main scope. so giving each command \n
    their own function means that they have \n
    there own scope.
    """
    @staticmethod
    def _parse_input(input_: str)->tuple[str,str,str]:
        """doesnt parse value
        returns: statement, command, value
        """
        statement = input_.split()[0]
        command = input_.split()[1]
        value = None
        try: value = input_.split(maxsplit=3)[2]
        except: pass
        return statement, command, value

    def __init__(self):
        self.global_data: dict[str] = {}
        self._commands: list = [] # holds the names of the commands
        self._command_functions: list = [] # holds the callable function of the commands
        self._statements: list = [] # holds the names of the statements
        self._statement_functions: list = [] # holds the callable function of the statements

    def create_command(self, command_name):
        """
        function needs 3 args (statement, command, value)\n
        pass name of command into create_command
        
        """
        def wrapper(fn):
            self._commands.append(command_name)
            self._command_functions.append(fn)
        return wrapper
    
    def create_statement(self, statement_name):
        """
        Create a statement (a command without arguments)\n 
        eg: help, exit, start.
        
        """
        def wrapper(fn):
            self._statements.append(statement_name)
            self._statement_functions.append(fn)
        return wrapper
    
    def update(self, input_) -> str | None:
        """checks for first instance of command and runs it.\n
        returns the error message"""
        # check for statements
        for i,v in enumerate(self._statements):
            if v == input_[:-1]: # :-1 removes the \n
                self._statement_functions[i]()
                return;

        try:
            CommandSerialization._parse_input(input_)
        except: 
            return "Statement not found"
        
        # check for commands
        for i,v in enumerate(self._commands):
            if v == CommandSerialization._parse_input(input_)[1]:
                statement, command, value = CommandSerialization._parse_input(input_)
                self._command_functions[i](statement, command, value)
                return;
    
        return f"Error: command not found '{CommandSerialization._parse_input(input_)[1]}'"


def main() -> None:
    inputComands = CommandSerialization()

    @inputComands.create_command("test1")
    def test1(statement, command, value):
        if statement == "set":
            inputComands.global_data["test1"] = value
            print(f"set test1 '{inputComands.global_data["test1"]}'")
        elif statement == "get":
            print("get test1")

    @inputComands.create_command("test2")
    def test2(statement, command, value):
        if statement == "set":
            print("set test2")

    while True:
        print(inputComands.update(input_ = input("in: ")))

if __name__ == "__main__": main()