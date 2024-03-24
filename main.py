import os
from grammar import *


def main():
    f = open("program.txt", "r")
    code = f.read()
    f.close()

    g = Grammar()
    prog = g.parse(code)
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
