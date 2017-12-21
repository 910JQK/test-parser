#!/usr/bin/python

from machine import *

I = Instruction
A = Argument
Int = lambda s: A('ident', 'int', s)
IntVal = lambda i: A('data', 'int', i)

insts = [
    I('read', Int('t1')),
    I('read', Int('t2')),
    I('plus', Int('t3'), Int('t1'), Int('t2')),
    I('goto', 'L'),
    I('mul', Int('t3'), Int('t3'), IntVal(3)),
    I('label', 'L'),
    I('write', Int('t3'))
]

def main():
    m = Machine()
    m.run(insts)


if __name__ == '__main__':
    main()
