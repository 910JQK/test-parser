#!/usr/bin/env python3


import sys
from syntax import get_syntax_tree
from machine import *


TEMP_IDENT_PREFIX = '_t'


def translate(syntax_tree_root):
    max_ident_index = -1
    released_idents_list = []
    released_idents = {}
    def get_ident():
        nonlocal max_ident_index
        if released_idents_list:
            ident = released_idents_list.pop()
            del released_idents[ident]
            return ident
        else:
            max_ident_index += 1
            return TEMP_IDENT_PREFIX + str(max_ident_index)
    def release_ident(ident):
        assert ident.startswith(TEMP_IDENT_PREFIX)
        if not released_idents.get(ident):
            released_idents_list.append(ident)
            released_idents[ident] = True
    def expand_code_list(code_list):
        result = []
        for code in code_list:
            result += code
        return result
    def synthesis_code(node):
        children_codes = [synthesis_code(child) for child in node.children]
        if node.syntax_item == 'ParExpr':
            # parentheses could break the order of calculation,
            # which will cause more identifiers being required
            ident_in_par = node.children[1].properties['arg'].ident
            if ident_in_par == released_idents_list[-1]:                
                released_idents_list.pop()
                del released_idents[ident_in_par]
        for child in node.children:
            if (
                    not node.properties.get('include_par')
                and child.properties.get('arg')
                and child.properties['arg'].arg_type == 'ident'
            ):                
                arg_ident = child.properties['arg'].ident
                if arg_ident.startswith(TEMP_IDENT_PREFIX):
                    release_ident(arg_ident)
        if hasattr(Produce, node.syntax_item):
            produce_code = getattr(Produce, node.syntax_item)
            return produce_code(node, children_codes)
        else:
            return expand_code_list(children_codes)
    class Produce():
        # Todo: Conditional Clauses
        def Oprand(node, children_codes):
            # Oprand -> Var | integer_value | double_value | bool_value
            data_type = node.properties['data_type']
            child = node.children[0]
            if node.deriv_tuple[0] == 'Var':
                arg = Argument('ident', data_type, child.properties['ident'])
            else:
                arg = Argument('data', data_type, child.token.string)
            node.properties['arg'] = arg
            return []
        def ParExpr(node, children_codes):
            # ParExpr -> (Expr)
            node.properties['arg'] = node.children[1].properties['arg']
            return expand_code_list(children_codes)
        def Unary(node, children_codes):
            # Unary -> {+, -, !} Unary | ParExpr | Oprand
            code = []
            op = node.deriv_tuple[0]
            oprand = node.children[-1]
            oprand_arg = oprand.properties['arg']
            data_type = node.properties['data_type']
            if op in ['ParExpr', 'Oprand', '+']:
                node.properties['arg'] = oprand_arg
            elif op == '-':
                temp = Argument('ident', data_type, get_ident())
                zero = Argument('data', data_type, 0)                
                code.append(Instruction('minus', temp, zero, oprand_arg))
                node.properties['arg'] = temp
            elif op == '!':
                temp = Argument('ident', data_type, get_ident())
                code.append(Instruction('not', temp, oprand_arg))
                node.properties['arg'] = temp
            else:
                assert False
            return expand_code_list(children_codes) + code
        def HandleCalcItem(inst_of_op, left, right, node, children_codes):
            # Xxx -> Item XxxRight
            # XxxRight -> Op Item XxxRight
            code = []
            if right.children:
                op = right.properties['op']
                right_arg = right.properties['arg']
                left_arg = left.properties['arg']
                data_type = node.properties['data_type']
                temp = Argument('ident', data_type, get_ident())
                code.append(
                    Instruction(inst_of_op[op], temp, left_arg, right_arg)
                )
                node.properties['arg'] = temp
                if node.deriv_tuple[0] in inst_of_op:
                    node.properties['op'] = node.children[0].token.string
                else:
                    pass
            else:
                if node.deriv_tuple[0] in inst_of_op:
                    node.properties['op'] = node.children[0].token.string
                else:
                    pass
                node.properties['arg'] = left.properties['arg']
            return expand_code_list(children_codes) + code
        def HandleCalc(op_map, node, children_codes, r=False):
            right = r
            if not right:
                # Xxx -> Item XxxRight
                left = node.children[0]
            elif node.children:
                # XxxRight -> Op Item XxxRight
                left = node.children[1]
            else:
                # XxxRight -> ""
                return []
            right = node.children[-1]
            return Produce.HandleCalcItem(
                op_map, left, right, node, children_codes
            )
        def Term(*args):
            # Term -> Unary TermRight
            return Produce.HandleCalc({'*':'mul', '/':'div'}, *args)
        def TermRight(*args):
            # TermRight -> "" | {*, /} Unary TermRight
            return Produce.HandleCalc({'*':'mul', '/':'div'}, *args, r=True)
        def Arith(*args):
            # Arith -> Term ArithRight
            return Produce.HandleCalc({'+':'plus', '-':'minus'}, *args)
        def ArithRight(*args):
            # TermRight -> "" | {*, /} Unary TermRight
            return Produce.HandleCalc({'+':'plus', '-':'minus'}, *args, r=True)
        def Rel(*args):
            # Rel -> Airth RelRight
            return Produce.HandleCalc(
                {
                    '<': 'lt', '>': 'gt',
                    '<=': 'le', '>=': 'ge'
                },
                *args
            )
        def RelRight(*args):
            # RelRight -> "" | {<, <=, >, >=} Arith RelRight
            return Produce.HandleCalc(
                {
                    '<': 'lt', '>': 'gt',
                    '<=': 'le', '>=': 'ge'
                },
                *args,
                r = True
            )
        def Equality(*args):
            # Equality -> Rel EqualityRight
            return Produce.HandleCalc({'==':'eq', '!=':'neq'}, *args)
        def EqualityRight(*args):
            # EqualityRight -> "" | {==, !=} Rel EqualityRight
            return Produce.HandleCalc({'==':'eq', '!=':'neq'}, *args, r=True)
        def Join(*args):
            # Join -> Equality JoinRight
            return Produce.HandleCalc({'&&':'and'}, *args)
        def JoinRight(*args):
            # JoinRight -> "" | && Equality JoinRight
            return Produce.HandleCalc({'&&':'and'}, *args, r=True)
        def Expr(*args):
            # Expr -> Join ExprRight
            return Produce.HandleCalc({'||':'or'}, *args)
        def ExprRight(*args):
            # ExprRight -> "" | || Join ExprRight
            return Produce.HandleCalc({'||':'or'}, *args, r=True)
    return synthesis_code(syntax_tree_root)


def print_code(code):
    for instruction in code:
        print(instruction)

        
def process_file(file_name):
    f = open(file_name, 'r')
    root = get_syntax_tree(f.read())
    code = translate(root)
    print_code(code)
    f.close()


def main():
    first = True
    for file_name in sys.argv:
        if not first:
            process_file(file_name)
        first = False


if __name__ == '__main__':
    main()
