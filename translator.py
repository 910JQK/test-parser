#!/usr/bin/env python3


import sys
from syntax import get_syntax_tree
from machine import (
    Instruction, Argument, CALCULATION,
    RETVAL, GETVAL, ARG_PREFIX, TEMP_PREFIX
)
from common import DEBUG, e_print


LABEL_PREFIX = 'L'
MAIN = 'main'
DEFAULT_VAL = {
    'int': Argument('data', 'int', 0),
    'double': Argument('data', 'double', 0.0),
    'bool': Argument('data', 'bool', False)
}


def translate(syntax_tree_root):
    max_ident_index = -1
    max_label_index = -1
    released_idents_list = []
    released_idents = {}
    def get_label():
        nonlocal max_label_index
        max_label_index += 1
        return LABEL_PREFIX + str(max_label_index)
    def get_ident():
        nonlocal max_ident_index
        if released_idents_list:
            ident = released_idents_list.pop()
            del released_idents[ident]
            return ident
        else:
            max_ident_index += 1
            return TEMP_PREFIX + str(max_ident_index)
    def release_ident(ident):
        assert ident.startswith(TEMP_PREFIX)
        if not released_idents.get(ident):
            released_idents_list.append(ident)
            released_idents[ident] = True
    def cancel_released_ident(ident):
        if released_idents_list:
            if ident == released_idents_list[-1]:
                released_idents_list.pop()
                del released_idents[ident]
    def expand_code_list(code_list):
        result = []
        for code in code_list:
            result += code
        return result
    def new_inst(cmd, *args):
        # parentheses and function calls could
        # break the order of calculation,
        # which will cause more identifiers being required
        # release a ident when the temp variable is used
        first = True
        for arg in args:
            if first:
                if cmd in ['mov', 'override', *CALCULATION]:
                    first = False
                    continue
            if hasattr(arg, 'arg_type'):
                if arg.arg_type == 'ident':
                    if arg.ident.startswith(TEMP_PREFIX):
                        release_ident(arg.ident)
            first = False
        return Instruction(cmd, *args)
    def synthesis_code(node):
        children_codes = [synthesis_code(child) for child in node.children]
        if hasattr(Produce, node.syntax_item):
            produce_code = getattr(Produce, node.syntax_item)
            return produce_code(node, children_codes)
        else:
            return expand_code_list(children_codes)
    class Produce():
        def Program(node, children_codes):
            return [
                *expand_code_list(children_codes),
                new_inst('start'),
                new_inst('call', MAIN)
            ]
        def Decl(node, children_codes):
            data_type = node.properties['data_type']
            ident = node.properties['ident']
            if node.function:
                inst_name = 'alloc'
            else:
                inst_name = 'static'
            return [
                new_inst(
                    inst_name, data_type, ident, DEFAULT_VAL[data_type]
                )
            ]
        def Function(node, children_codes):
            # Fucntion -> def ident(ParaList) FunctionBody
            body_code = children_codes[-1]
            para_list = node.properties['para_list'] # ((type, ident),...)
            para_code = []
            i = len(para_list)-1
            while i >= 0:
                para = para_list[i]
                para_code.append(
                    new_inst('alloc', *para, DEFAULT_VAL[para[0]])
                )
                para_code.append(
                    new_inst(
                        'mov',
                        Argument('ident', *para),
                        Argument('ident', para[0], ARG_PREFIX+str(i))
                    )
                )
                i = i - 1
            name = node.properties['name']
            if name == MAIN:
                return_code = [new_inst('exit')]
            else:
                return_code = [new_inst('ret')]
            return_type = node.properties['return_type']
            if return_type != 'void':
                retval_code = [
                    new_inst(
                        'alloc', return_type, RETVAL, DEFAULT_VAL[return_type]
                    )
                ]
            else:
                retval_code = []
            return [
                new_inst('proc', name),
                *retval_code,
                *para_code,
                *body_code,
                *return_code,
                new_inst('end', name)
            ]
        def ReturnValue(node, children_codes):
            # ReturnValue -> ; | Expr;
            if node.deriv_tuple[0] == 'Expr':
                node.properties['arg'] = node.children[0].properties['arg']
            return expand_code_list(children_codes)
        def Stmt(node, children_codes):
            # Stmt -> Assign; | read Var; | print Expr; | eval Expr;
            #         if(Expr) Stmt Else | while(Expr) Stmt |
            #         do Stmt while(Expr); | for(Assign; Expr; Assign) Stmt |
            #         break; | continue; | return ReturnValue | Block
            def enable_jump(code, continue_label, break_label):
                for i in range(0, len(code)):
                    if code[i] == 'continue':
                        code[i] = new_inst('goto', continue_label)
                    elif code[i] == 'break':
                        code[i] = new_inst('goto', break_label)
            rule = node.deriv_tuple[0]
            if rule == 'if':
                # if(Expr) Stmt Else
                expr_node = node.children[2]
                expr_code = children_codes[2]
                expr_arg = expr_node.properties['arg']
                stmt_code = children_codes[4]
                else_code = children_codes[5]
                label_pre_else = get_label()
                label_post_else = get_label()
                return [
                    *expr_code,
                    new_inst('goto_if_false', expr_arg, label_pre_else),
                    *stmt_code,
                    new_inst('goto', label_post_else),
                    new_inst('label', label_pre_else),
                    *else_code,
                    new_inst('label', label_post_else)
                ]
            elif rule == 'while':
                # while(Expr) Stmt
                expr_node = node.children[2]
                expr_code = children_codes[2]
                expr_arg = expr_node.properties['arg']
                stmt_code = children_codes[4]
                label_go_back = get_label()
                label_tail = get_label()
                enable_jump(stmt_code, label_go_back, label_tail)
                return [
                    new_inst('label', label_go_back),
                    *expr_code,
                    new_inst('goto_if_false', expr_arg, label_tail),
                    *stmt_code,
                    new_inst('goto', label_go_back),
                    new_inst('label', label_tail)
                ]
            elif rule == 'do':
                # do Stmt while(Expr);
                expr_node = node.children[4]
                expr_code = children_codes[4]
                expr_arg = expr_node.properties['arg']
                stmt_code = children_codes[1]
                label_go_back = get_label()
                label_tail = get_label()
                enable_jump(stmt_code, label_go_back, label_tail)
                return [
                    new_inst('label', label_go_back),
                    *stmt_code,
                    *expr_code,
                    new_inst('goto_if', expr_arg, label_go_back),
                    new_inst('label', label_tail)
                ]
            elif rule == 'for':
                # for(Assign; Expr; Assign) Stmt
                initial_code = children_codes[2]
                condition_node = node.children[4]
                condition_code = children_codes[4]
                condition_arg = condition_node.properties['arg']
                increment_code = children_codes[6]
                stmt_code = children_codes[8]
                label_go_back = get_label()
                label_tail = get_label()
                enable_jump(stmt_code, label_go_back, label_tail)
                return [
                    *initial_code,
                    new_inst('label', label_go_back),
                    *condition_code,
                    new_inst('goto_if_false', condition_arg, label_tail),
                    *stmt_code,
                    *increment_code,
                    new_inst('goto', label_go_back),
                    new_inst('label', label_tail)
                ]
            elif rule == 'break':
                # to be handled in enable_jump()
                return ['break']
            elif rule == 'continue':
                # to be handled in enable_jump()
                return ['continue']
            elif rule == 'return':
                code = []
                data_type = node.children[1].properties['data_type']
                if data_type != 'void':
                    retval_arg = Argument('ident', data_type, RETVAL)
                    expr_arg = node.children[1].properties['arg']
                    expr_code = children_codes[1]
                    code = [*code, *expr_code]
                    code.append(new_inst('mov', retval_arg, expr_arg))
                assert node.function
                if node.function.properties['name'] == MAIN: 
                    code.append(new_inst('exit'))
                else:
                    code.append(new_inst('ret'))
                return code
            elif rule == 'read':
                # read Var;
                ident = node.children[1].properties['ident']
                data_type = node.children[1].properties['data_type']
                ident_arg = Argument('ident', data_type, ident)
                return [new_inst('read', ident_arg)]
            elif rule == 'print':
                # print Expr;
                expr_code = children_codes[1]
                expr_arg = node.children[1].properties['arg']
                return [*expr_code, new_inst('print', expr_arg)]
            else:
                return expand_code_list(children_codes)
        def Assign(node, children_codes):
            # Assign -> Var = Expr
            ident = node.children[0].properties['ident']
            data_type = node.children[0].properties['data_type']
            var_arg = Argument('ident', data_type, ident)
            expr_arg = node.children[2].properties['arg']
            expr_code = children_codes[2]
            return [
                *expr_code,
                new_inst('mov', var_arg, expr_arg)
            ]
        def Oprand(node, children_codes):
            # Oprand -> Var | integer_value | double_value | bool_value
            data_type = node.properties['data_type']
            child = node.children[0]
            if node.deriv_tuple[0] == 'VarCall':
                arg = node.children[0].properties['arg']
            else:
                arg = Argument('data', data_type, child.token.string)
            node.properties['arg'] = arg
            return expand_code_list(children_codes)
        def VarCall(node, children_codes):
            # VarCall -> ident VarCallRight
            code = []
            ident = node.children[0].token.string
            var_type = node.properties['var_type']
            data_type = node.properties['data_type']
            if var_type == 'var':                
                arg = Argument('ident', data_type, ident)
            elif var_type == 'array':
                # todo: array
                pass
            elif var_type == 'call':
                arglist_code = children_codes[1]
                code = [*code, *arglist_code]
                code.append(new_inst('call', ident))
                if data_type != 'void':
                    getval = Argument('ident', data_type, GETVAL)
                    arg = Argument('ident', data_type, get_ident())
                    code.append(new_inst('mov', arg, getval))
                else:
                    arg = None
            else:
                assert False
            node.properties['arg'] = arg
            return code
        def ArgList(node, children_codes):
            # ArgList -> Expr ArgListRight
            if not node.children:
                return []
            result_code = []
            expr_node = node.children[0]
            right = node.children[-1]
            arg = expr_node.properties['arg']
            code = children_codes[0]
            args = node.properties['args'] = [arg, *right.properties['args']]
            codes = [[*code], *children_codes[-1]]
            types = node.properties['arg_types']
            for i in range(0, len(args)):
                result_code = [
                    *result_code,
                    *codes[i],
                    new_inst(
                        'override',
                        Argument('ident', types[i], ARG_PREFIX+str(i)),
                        args[i]
                    )
                ]
            return result_code
        def ArgListRight(node, children_codes):
            # ArgListRight -> "" | ,Expr ArgListRight
            if not node.children:
                node.properties['args'] = []
                return []
            else:
                expr_node = node.children[1]
                right = node.children[-1]
                arg = expr_node.properties['arg']
                code = children_codes[1]
                node.properties['args'] = [arg, *right.properties['args']]
                return [[*code], *children_codes[-1]]
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
                code.append(new_inst('minus', temp, zero, oprand_arg))
                node.properties['arg'] = temp
            elif op == '!':
                temp = Argument('ident', data_type, get_ident())
                code.append(new_inst('not', temp, oprand_arg))
                node.properties['arg'] = temp
            else:
                assert False
            return expand_code_list(children_codes) + code
        def HandleCalcItem(inst_of_op, left, right, node, children_codes):
            # Xxx -> Item XxxRight
            # XxxRight -> Op Item XxxRight
            code = []
            if (
                    right.children
#                and right.children[].syntax_item.startswith(node.syntax_item)
            ):
                op = right.properties['op']
                right_arg = right.properties['arg']
                left_arg = left.properties['arg']
                data_type = node.properties['data_type']
                temp = Argument('ident', data_type, get_ident())
                code.append(
                    new_inst(inst_of_op[op], temp, left_arg, right_arg)
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
    if DEBUG:
        code = synthesis_code(syntax_tree_root)
        e_print('Translated Code:')
        count = 0
        for instruction in code:
            e_print('%d: %s' % (count, instruction))
            count += 1
        return code
    else:
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
