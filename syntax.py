#!/usr/bin/env python3


import re
import sys
from definition import TOKEN, SYNTAX, RULE
from scanner import get_tokens


def e_print(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


class InvalidSyntaxException(Exception):
    def __init__(self, coor):
        self.coor = coor

    def __str__(self):
        return 'Invalid Syntax at Line %d, Col %d' % self.coor


class SyntaxError(Exception):
    def __init__(self, coor, msg):
        self.coor = coor
        self.msg = msg

    def __str__(self):
        return 'Syntax Error at Line %d, Col %d:\n\t%s' % (*self.coor, self.msg)


class SyntaxTreeNode:
    syntax_item = ''
    children = None # list, reference type
    properties = None # dict
    parent = None
    token = None
    processed = False
    deriv_tuple = ()
    def __init__(self, syntax_item):
        self.syntax_item = syntax_item
        self.children = []
        self.properties = {'data_type': None, 'arg': None}

    def get_type(self):
        return get_syntax_item_type(self.syntax_item)

    def check_processed(self):
        has_unprocessed = False
        for child in self.children:
            if not child.processed:
                has_unprocessed = True
                break
        if not has_unprocessed:
            self.processed = True
            if self.parent:
                self.parent.check_processed()

    def match_token(self, token):
        item_type = self.get_type()
        assert item_type != 'non-terminal'
        def match():
            self.token = token
            self.processed = True
            if self.parent:
                self.parent.check_processed()
        if item_type == 'token-type':
            if token.token_type == self.syntax_item:
                match()
                return True
            else:
                return False
        elif item_type == 'string':
            if token.string == self.syntax_item:
                match()
                return True
            else:
                return False
        else:
            return False

    def set_empty(self):
        self.processed = True
        if self.parent:
            self.parent.check_processed()

    def produce_children_reversed(self, derivation_tuple):
        for item in reversed(derivation_tuple):
            new_node = SyntaxTreeNode(item)
            new_node.parent = self
            self.children.insert(0, new_node)
            yield new_node


def get_syntax_item_type(string):
    if re.compile('[A-Z]').match(string):
        return 'non-terminal'
    else:
        for token_type, regex in TOKEN:
            if string == token_type:
                return 'token-type'            
        return 'string'


def get_syntax_tree(code):
    root = SyntaxTreeNode('Start')
    symbols = {}
    syntax_stack = []
    syntax_stack.append(root)
    
    def process_token(token):
        def set_properties(node):
            if node.processed:
                if hasattr(RULE, node.syntax_item):
                    check_f = getattr(RULE, node.syntax_item)
                    result = check_f(symbols, node)
                    if result.ok:
                        if node.parent:
                            set_properties(node.parent)
                    else:
                        raise SyntaxError(token.coor, result.msg)
                else:
                    if node.parent:
                        set_properties(node.parent)
        e_print('(Debug) -- Processing Token ' + str(token))
        current_node = syntax_stack.pop()
        def push_children(deriv_tuple):
            for child in current_node.produce_children_reversed(deriv_tuple):
                syntax_stack.append(child)
                e_print('(Debug) Push [%s]' % child.syntax_item)
        if current_node.get_type() == 'non-terminal':
            e_print(
                '(Debug) Try to expand [%s]'
                % current_node.syntax_item
            )
            syntax = SYNTAX[current_node.syntax_item]
            expanded = False
            for first, deriv_tuple in syntax['derivations']:
                if first == 'ANY':
                    expanded = True
                else:
                    if get_syntax_item_type(first) == 'token-type':
                        if first == token.token_type:
                            expanded = True                    
                    else:
                        # string
                        if first == token.string:
                            expanded = True
                if expanded:
                    push_children(deriv_tuple)
                    current_node.deriv_tuple = deriv_tuple
                    #e_print('(Debug) derive_tuple=%s' % str(deriv_tuple))
                    break
            if not expanded:
                if syntax['empty']:
                    e_print('(Debug) Expanded by ""')
                    current_node.set_empty()
                    set_properties(current_node)
                    process_token(token)
                else:
                    raise InvalidSyntaxException(token.coor)
            else:
                e_print('(Debug) Expanded by %s' % str(deriv_tuple))
                process_token(token)
        else:
            e_print(
                '(Debug) Try to match [%s]'
                % current_node.syntax_item
            )
            if(current_node.match_token(token)):
                e_print('(Debug) Matched %s' % token.string)
                set_properties(current_node)
            else:
                raise InvalidSyntaxException(token.coor)

    for token in get_tokens(code):
        if token.token_type in ['comment', 'space']:
            continue
        else:
            process_token(token)
    last_token = token

    while (
            syntax_stack
            and get_syntax_item_type(
                syntax_stack[-1].syntax_item) == 'non-terminal'
            and SYNTAX[syntax_stack[-1].syntax_item]['empty']
    ):
        syntax_stack.pop()
    if not syntax_stack:
        pass
    else:
        raise InvalidSyntaxException(last_token.coor)

    return root


def print_syntax_tree(node, depth=0):
    depth_string = '  '*depth
    line = '%s[%s] '% (depth_string, node.syntax_item)
    if node.properties['data_type']:
        line += node.properties['data_type'] + ' '
    if node.get_type() != 'non-terminal':
        line += node.token.string
    print(line)
    for child in node.children:
        print_syntax_tree(child, depth+1)


def process_file(file_name):
    f = open(file_name, 'r')
    root = get_syntax_tree(f.read())
    print_syntax_tree(root)
    f.close()


def main():
    first = True
    for file_name in sys.argv:
        if not first:
            process_file(file_name)
        first = False


if __name__ == '__main__':
    main()
