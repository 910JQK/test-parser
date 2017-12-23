#!/usr/bin/env python3


import sys
from machine import Machine
from translator import translate
from syntax import get_syntax_tree


def main():
    machine = Machine()
    if len(sys.argv) > 1:
        code_file = sys.argv[1]
        f = open(code_file, 'r')
        machine.run(
            translate(
                get_syntax_tree(
                    f.read()
                )
            )
        )
        f.close()


if __name__ == '__main__':
    main()
