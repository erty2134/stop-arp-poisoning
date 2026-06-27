from enum import Enum
class ANSI(Enum):
    END="\033[0m";
    BOLD="\033[1m";
    DIM="\033[2m";
    ITALIC="\033[3m";
    UNDERLINE="\033[4m";
    REVERSE="\033[7m";
    STRIKETHROUGH="\033[9m";
    #colours
    BLACK = "\033[30m"
    MAGENTA = "\033[35m"
    BLUE =  "\033[34m"
    CYAN =  "\033[36m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    PINK = "\033[35m"
    #highlight
    BLACKBG = "\033[40m"
    MAGENTABG = "\033[45m"
    BLUEBG =  "\033[44m"
    CYANBG =  "\033[46m"
    GREENBG = "\033[42m"
    REDBG = "\033[41m"
    YELLOWBG = "\033[43m"
    PINKBG = "\033[45m"