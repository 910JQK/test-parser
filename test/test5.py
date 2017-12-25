#!/usr/bin/env python3

def f(x, y):
    i = 0
    while i<10:
        y = y + i
        i = i + 1
    return x + y

def g(x):
    return -x

def h():
    x = int(input())
    y = int(input())
    print (f(x, y) * g(x))

h()

