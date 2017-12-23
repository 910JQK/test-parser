import sys


DEBUG = True


def e_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


