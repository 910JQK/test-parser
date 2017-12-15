#!/usr/bin/env python3


import sys
from definition import TOKEN


class InvalidTokenException(Exception):
    def __init__(self, coor):
        self.coor = coor
    def __str__(self):        
        return 'Invalid Token at Line %d, Col %d' % self.coor


class Token:
    token_type = ''
    string = ''
    coor = (-1, -1)
    def __str__(self):
        return (
            "(%s, '%s') at (%d, %d)"
            % (self.token_type, self.string, *self.coor)
        )
    def __init__(self, token_type, string, coor):
        self.token_type = token_type
        self.string = string
        self.coor = coor


def coordinate_generator(code):
    lines = code.split('\n')
    line_num = 0 # start from zero
    line_start = 0
    last_pos = 0
    def get_coordinate(pos):
        nonlocal line_num, line_start, last_pos
        assert pos >= last_pos
        last_pos = pos
        while line_num < len(lines):
            if line_start <= pos and pos < line_start + len(lines[line_num])+1:
                return (line_num+1, pos-line_start+1)
            line_start += len(lines[line_num])+1 # start of the next line
            line_num += 1 # line number of the next line
        return (-1, -1)
    return get_coordinate


def get_tokens(code):    
    pos = 0
    get_coordinate = coordinate_generator(code);
    while pos < len(code):
        ok = False
        coor = get_coordinate(pos)
        for token_type, regex in TOKEN:
            match = regex.match(code, pos);
            if match:
                match_str = match.group(0)
                yield Token(token_type, match_str, coor)
                pos += len(match_str)
                ok = True
                break
        if not ok:
            raise InvalidTokenException(coor)


def process_file(file_name):
    f = open(file_name, 'r')
    for token in get_tokens(f.read()):
        print(token)
    f.close()


def main():
    first = True
    for file_name in sys.argv:
        if not first:
            process_file(file_name)
        first = False


if __name__ == '__main__':
    main()
