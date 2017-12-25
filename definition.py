import re


TOKEN = [
    (
        'comment',
        re.compile('\/\/[^\n]*|\/\*([^\*]|\*[^\/])*\*\/')
    ),
    (
        'string',
        re.compile('"[^\n"]"' + '|' + "'[^\n']'")
    ),
    (
        'space',
        re.compile('[ \n\t]+')
    ),
    (
        'type_key',
        re.compile('void|int|double|bool|string')
    ),
    (
        'bool_value',
        re.compile('true|false')
    ),
    (
        'cond_key',
        re.compile('for|while|do|break|if|else')
    ),
    (
        'key',
        re.compile('class|null|this|extends|return|new|print|read|eval')
    ),
    (
        'double_value',
        re.compile('[0-9]+\.[0-9]*|[0-9]+\.[0-9]*[eE][+-]?[0-9]+')
    ),
    (
        'integer_value',
        re.compile('[1-9][0-9]*|[0-9]|0[xX][1-9A-Fa-f][0-9A-Fa-f]*|0[xX][0-9A-Fa-f]')
    ),
    (
        'op',
        re.compile(r'\-\>|\&\&|\|\||\=\=|\!|\+|\-|\*|\/|\&|%|\\|\<|\<\=|\>|\>\=|\=|\!\=|\;|\,|\.|\[|\]|\(|\)|\{|\}')
    ),
    (
        'ident',
        re.compile('[A-Za-z][0-9A-Za-z_]*')
    )
]


SYNTAX = {
    # Program -> Decls Functions
    'Program': {
        'empty': False,
        'derivations': [
            ('ANY', ('Decls', 'Functions'))
        ]
    },
    # Functions -> "" | Function Functions
    'Functions': {
        'empty': True,
        'derivations': [
            ('def', ('Function', 'Functions'))
        ]
    },
    # Fucntion -> def ident(ParaList) FunctionBody
    'Function': {
        'empty': False,
        'derivations': [
            ('ANY', ('def', 'ident', '(', 'ParaList', ')', 'FunctionBody'))
        ]
    },
    # ParaList -> "" | Type ident ParaListRight
    'ParaList': {
        'empty': True,
        'derivations': [
            ('type_key', ('Type', 'ident', 'ParaListRight'))
        ]
    },
    # ParaListRight -> "" | , Type ident ParaListRight
    'ParaListRight': {
        'empty': True,
        'derivations': [
            (',', (',', 'Type', 'ident', 'ParaListRight'))
        ]
    },
    # FunctionBody -> {"", FunctionType} { Decls Stmts }
    'FunctionBody': {
        'empty': False,
        'derivations': [
            ('{', ('{', 'Decls', 'Stmts', '}')),
            ('->', ('FunctionType', '{', 'Decls', 'Stmts', '}'))
        ]
    },
    # FunctionType -> -> Type
    'FunctionType': {
        'empty': False,
        'derivations': [
            ('ANY', ('->', 'Type'))
        ]
    },
    # Block -> { Stmts }
    'Block': {
        'empty': False,
        'derivations': [
            ('ANY', ('{', 'Stmts', '}'))
        ]
    },
    # Decls -> "" | Decl Decls
    'Decls': {
        'empty': True,
        'derivations': [
            ('type_key', ('Decl', 'Decls'))
        ]
    },
    # Decl -> Type ident;
    'Decl': {
        'empty': False,
        'derivations': [
            ('ANY', ('Type', 'ident', ';'))
        ]
    },
    # Type -> type_key TypeRight
    'Type': {
        'empty': False,
        'derivations': [
            ('ANY', ('type_key', 'TypeRight'))
        ]
    },
    # TypeRight -> "" | [ integer_value ] TypeRight
    'TypeRight': {
        'empty': True,
        'derivations': [
            ('[', ('[', 'integer_value', ']', 'TypeRight'))
        ]
    },
    # Stmts -> "" | Stmt Stmts
    'Stmts': {
        'empty': True,
        'derivations': [
            ('ident', ('Stmt', 'Stmts')),
            ('key', ('Stmt', 'Stmts')),
            ('cond_key', ('Stmt', 'Stmts')),
            ('{', ('Stmt', 'Stmts'))
        ]
    },
    # Stmt -> Assign; | read Var; | print expr; | eval expr;
    #         if(Expr) Stmt Else | while(Expr) Stmt |
    #         do Stmt while(Expr); | for(Assign; Expr; Assign) Stmt |
    #         break; | continue; | return ReturnValue | Block
    'Stmt': {
        'empty': False,
        'derivations': [
            ('ident', ('Assign', ';')),
            ('read', ('read', 'Var', ';')),
            ('print', ('print', 'Expr', ';')),
            ('eval', ('eval', 'Expr', ';')),
            ('if', ('if', '(', 'Expr', ')', 'Stmt', 'Else')),
            ('while', ('while', '(', 'Expr', ')', 'Stmt')),
            ('do', ('do', 'Stmt', 'while', '(', 'Expr', ')', ';')),
            ('for',
             ('for', '(', 'Assign', ';', 'Expr', ';', 'Assign', ')', 'Stmt')
            ),
            ('break', ('break', ';')),
            ('continue', ('continue', ';')),
            ('return', ('return', 'ReturnValue')),
            ('{', ('Block',)),
            ('ANY', ('Expr',))
        ]
    },
    # ReturnValue -> ; | Expr;
    'ReturnValue': {
        'empty': False,
        'derivations': [
            (';', (';',)),
            ('ANY', ('Expr', ';'))
        ]
    },
    # Assign -> Var = Expr
    'Assign': {
        'empty': False,
        'derivations': [
            ('ANY', ('Var', '=', 'Expr'))
        ]
    },
    # Else -> "" | else Stmt
    'Else': {
        'empty': True,
        'derivations': [
            ('else', ('else', 'Stmt'))
        ]
    },
    # VarCall -> ident VarCallRight
    'VarCall': {
        'empty': False,
        'derivations': [
            ('ANY', ('ident', 'VarCallRight'))
        ]
    },
    # VarCallRight -> "" | VarRight | ArgListWrapper
    'VarCallRight': {
        'empty': True,
        'derivations': [
            ('[', ('VarRight',)),
            ('(', ('ArgListWrapper',))
        ]
    },
    # Var -> ident VarRight
    'Var': {
        'empty': False,
        'derivations': [
            ('ANY', ('ident', 'VarRight'))
        ]
    },
    # VarRight -> "" | [Expr] VarRight
    'VarRight': {
        'empty': True,
        'derivations': [
            ('[', ('[', 'Expr', ']', 'VarRight'))
        ]
    },
    # ArgListWrapper -> ( ArgList )
    'ArgListWrapper': {
        'empty': False,
        'derivations': [
            ('ANY', ('(', 'ArgList', ')'))
        ]
    },
    # ArgList -> "" | Expr ArgListRight
    'ArgList': {
        'empty': True,
        'follow': ')',
        'derivations': [
            ('ANY', ('Expr', 'ArgListRight'))
        ]
    },
    # ArgListRight -> "" | ,Expr ArgListRight
    'ArgListRight': {
        'empty': True,
        'derivations': [
            (',', (',', 'Expr', 'ArgListRight'))
        ]
    },
    # Expr -> Join ExprRight
    'Expr': {
        'empty': False,
        'derivations': [
            ('ANY', ('Join', 'ExprRight'))
        ]
    },
    # ExprRight -> "" | || Join ExprRight
    'ExprRight': {
        'empty': True,
        'derivations': [
            ('||', ('||', 'Join', 'ExprRight'))
        ]
    },
    # Join -> Equality JoinRight
    'Join': {
        'empty': False,
        'derivations': [
            ('ANY', ('Equality', 'JoinRight'))
        ]
    },
    # JoinRight -> "" | && Equality
    'JoinRight': {
        'empty': True,
        'derivations': [
            ('&&', ('&&', 'Equality'))
        ]
    },
    # Equality -> Rel EqualityRight
    'Equality': {
        'empty': False,
        'derivations': [
            ('ANY', ('Rel', 'EqualityRight'))
        ]
    },
    # EqualityRight -> "" | {==, !=} Rel EqualityRight
    'EqualityRight': {
        'empty': True,
        'derivations': [
            ('==', ('==', 'Rel', 'EqualityRight')),
            ('!=', ('!=', 'Rel', 'EqualityRight'))
        ]
    },
    # Rel -> Arith RelRight
    'Rel': {
        'empty': False,
        'derivations': [
            ('ANY', ('Arith', 'RelRight'))
        ]
    },
    # RelRight -> "" | {<, <=, >, >=} Arith RelRight
    'RelRight': {
        'empty': True,
        'derivations': [
            ('<', ('<', 'Arith', 'RelRight')),
            ('<=', ('<=', 'Arith', 'RelRight')),
            ('>', ('>', 'Arith', 'RelRight')),
            ('>=', ('>=', 'Arith', 'RelRight'))
        ]
    },
    # Arith -> Term ArithRight
    'Arith': {
        'empty': False,
        'derivations': [
            ('ANY', ('Term', 'ArithRight'))
        ]
    },
    # ArithRight -> "" | {+, -} Term ArithRight
    'ArithRight': {
        'empty': True,
        'derivations': [
            ('+', ('+', 'Term', 'ArithRight')),
            ('-', ('-', 'Term', 'ArithRight'))
        ]
    },
    # Term -> Unary TermRight
    'Term': {
        'empty': False,
        'derivations': [
            ('ANY', ('Unary', 'TermRight'))
        ]
    },
    # TermRight -> "" | {*, /} Unary TermRight
    'TermRight': {
        'empty': True,
        'derivations': [
            ('*', ('*', 'Unary', 'TermRight')),
            ('/', ('/', 'Unary', 'TermRight'))
        ]
    },
    # Unary -> {+, -, !} Unary | ParExpr | Oprand
    'Unary': {
        'empty': False,
        'derivations': [
            ('+', ('+', 'Unary')),
            ('-', ('-', 'Unary')),
            ('!', ('!', 'Unary')),
            ('(', ('ParExpr',)),
            ('ANY', ('Oprand',))
        ]
    },
    # ParExpr -> (Expr)
    'ParExpr': {
        'empty': False,
        'derivations': [
            ('ANY', ('(', 'Expr', ')'))
        ]
    },
    # Oprand -> VarCall | integer_value | double_value | bool_value
    'Oprand': {
        'empty': False,
        'derivations': [
            ('ident', ('VarCall',)),
            ('integer_value', ('integer_value',)),
            ('double_value', ('double_value',)),
            ('bool_value', ('bool_value',))
        ]
    }
}


class Check:
    def __init__(self, ok=True, msg=''):
        self.ok = ok
        self.msg = msg
    def __bool__(self):
        return self.ok
    def Pass():
        return Check()
    def Error(msg):
        return Check(False, msg)


# Decorator
def MergeSymbols(f):
    def g(symbols, node):
        if node.function:
            function_symbols = node.function.properties['symbols']
        else:
            function_symbols = {}
        merged_symbols = {**symbols, **function_symbols}
        return f(merged_symbols, node)
    return g


class RULE:
    def Type(symbols, node):
        # Type -> type_key TypeRight
        type_key = node.children[0]
        # int / double / bool
        type_name = type_key.token.string
        node.properties['data_type'] = type_name
        return Check.Pass()

    def Decl(symbols, node):
        # Decl -> Type ident
        data_type = node.children[0].properties['data_type']        
        ident = node.children[1].token.string
        node.properties['data_type'] = data_type
        node.properties['ident'] = ident
        if node.function:
            active_symbols = node.function.properties['symbols']
        else:
            active_symbols = symbols
        if not active_symbols.get(ident):
            active_symbols[ident] = data_type
            return Check.Pass()
        else:
            return Check.Error('Duplicate definition for variable %s' % ident)

    @MergeSymbols
    def Var(symbols, node):
        # Var -> ident VarRight
        ident = node.children[0].token.string
        if symbols.get(ident):
            node.properties['data_type'] = symbols[ident]
            node.properties['ident'] = ident # todo: array
            return Check.Pass()
        else:
            return Check.Error('Variable %s not defined' % ident)

    @MergeSymbols
    def VarCall(symbols, node):
        # VarCall -> ident VarCallRight
        ident = node.children[0].token.string
        var_type = node.children[1].properties['var_type']
        node.properties['var_type'] = var_type
        if var_type == 'var':
            if symbols.get(ident):
                node.properties['data_type'] = symbols[ident]
                node.properties['ident'] = ident
                return Check.Pass()
            else:
                return Check.Error('Variable %s not defined' % ident)
        elif var_type == 'array':
            # todo: array
            pass
        elif var_type == 'call':
            node.properties['keep_temp'] = True
            if symbols['_functions'].get(ident):
                function_info = symbols['_functions'][ident]
                arg_types = node.children[1].properties['arg_types']
                if function_info['parameters'] == arg_types:
                    node.properties['function_name'] = ident
                    node.properties['data_type'] = function_info['return_type']
                else:
                    return Check.Error(
                        'Wrong Argument Type: %s required but %s given'
                        % (function_info['parameters'], arg_types)
                    )
            else:
                return Check.Error('%s: No such function' % ident)
        else:
            assert False
        return Check.Pass()

    def VarCallRight(symbols, node):
        # VarCallRight -> "" | VarRight | ArgListWrapper
        if not node.children:
            node.properties['var_type'] = 'var'
        elif node.deriv_tuple[0] == 'VarRight':
            # todo: array
            node.properties['var_type'] = 'array'
        elif node.deriv_tuple[0] == 'ArgListWrapper':
            node.properties['var_type'] = 'call'
            wrapper_node = node.children[0]
            node.properties['arg_types'] = wrapper_node.properties['arg_types']
        else:
            assert False
        return Check.Pass()

    def ArgListWrapper(symbols, node):
        # ArgListWrapper -> ( ArgList )
        node.properties['arg_types'] = node.children[1].properties['arg_types']
        return Check.Pass()

    def ArgList(symbols, node):
        # ArgList -> Expr ArgListRight
        if not node.children:
            node.properties['arg_types'] = ()
            return Check.Pass()
        expr = node.children[0]
        right = node.children[-1]
        node.properties['arg_types'] = tuple([
            expr.properties['data_type'],
            *right.properties['arg_types']
        ])
        return Check.Pass()

    def ArgListRight(symbols, node):
        # ArgListRight -> "" | ,Expr ArgListRight
        if not node.children:
            node.properties['arg_types'] = ()
        else:
            expr = node.children[1]
            right = node.children[-1]
            node.properties['arg_types'] = tuple([
                expr.properties['data_type'],
                *right.properties['arg_types']
            ])
        return Check.Pass()

    def Oprand(symbols, node):
        # Oprand -> VarCall | integer_value | double_value | bool_value
        deriv_tuple = node.deriv_tuple
        token2data = {
            'integer_value': 'int',
            'bool_value': 'bool', 
            'double_value': 'double'
        }
        var_or_val = node.children[0]
        if deriv_tuple[0] == 'VarCall':
            data_type = var_or_val.properties['data_type']
            node.properties['keep_temp'] = True
        else:
            data_type = token2data[var_or_val.token.token_type]
        node.properties['data_type'] = data_type
        return Check.Pass()

    def ParExpr(symbols, node):        
        # ParExpr -> (Expr)
        expr = node.children[1]        
        node.properties['data_type'] = expr.properties['data_type']
        node.properties['keep_temp'] = True
        return Check.Pass()

    def Unary(symbols, node):
        # Unary -> {+, -, !} Unary | ParExpr | Oprand
        op = node.deriv_tuple[0]
        oprand = node.children[-1]
        oprand_type = oprand.properties['data_type']
        if oprand_type == 'void':
            data_type = 'void'
        else:
            if op == '!':
                if oprand_type == 'bool':
                    data_type = 'bool'
                else:
                    return Check.Error('Not Operator: bool oprand required')
            elif op == 'Oprand':
                data_type = oprand_type
            else:
                if oprand_type == 'double':
                    data_type = 'double'
                else: # int or bool
                    data_type = 'int'
        node.properties['data_type'] = data_type
        if op in ['Oprand', 'ParExpr']:
            if oprand.properties.get('keep_temp'):
                node.properties['keep_temp'] = True
        return Check.Pass()

    # Reuse Function
    def SetNumberType(node, item, right):
        if item.properties['data_type'] == 'void':
            data_type = 'void'            
        elif right.children and right.properties['data_type'] == 'void':
            data_type = 'void'
        else:
            if right.children:
                if item.properties['data_type'] == 'double':
                    data_type = 'double'
                else:
                    data_type = right.properties['data_type']
            else:
                if item.properties['data_type'] == 'bool':
                    data_type = 'int'
                else:
                    data_type = item.properties['data_type']
            if item.properties.get('keep_temp'):
                node.properties['keep_temp'] = True
        node.properties['data_type'] = data_type
        return Check.Pass()    
 
    def Term(symbols, node):
        # Term -> Unary TermRight
        unary = node.children[0]
        right = node.children[-1]
        return RULE.SetNumberType(node, unary, right)

    def TermRight(symbols, node):
        # TermRight -> "" | {*, /} Unary TermRight
        if node.children:
            unary = node.children[1]
            right = node.children[-1]
            return RULE.SetNumberType(node, unary, right)
        else:
            return Check.Pass()

    def Arith(symbols, node):
        # Arith -> Term ArithRight
        term = node.children[0]
        right = node.children[-1]        
        return RULE.SetNumberType(node, term, right)
        
    def ArithRight(symbols, node):
        # ArithRight -> "" | {+, -} Term ArithRight
        if node.children:
            term = node.children[1]
            right = node.children[-1]        
            return RULE.SetNumberType(node, term, right)
        else:
            return Check.Pass()

    # Reuse Function
    def SetBoolType(node):
        if node.children:
            item = node.children[0]
            right = node.children[1]
            if right.children:
                item_type = item.properties['data_type']
                right_type = right.children[1].properties['data_type']
                if right_type == 'void' or item_type == 'void':
                    node.properties['data_type'] = 'void'
                else:
                    node.properties['data_type'] = 'bool'
                item.properties['keep_temp'] = True
                right.properties['keep_temp'] = True
                node.properties['keep_temp'] = True
            else:
                node.properties['data_type'] = item.properties['data_type']
                if item.properties.get('keep_temp'):
                    node.properties['keep_temp'] = True
        return Check.Pass()

    def Rel(symbols, node):
        # Rel -> Arith RelRight
        return RULE.SetBoolType(node)

    def Equality(symbols, node):
        # Equality -> Rel EqualityRight
        return RULE.SetBoolType(node)

    def Join(symbols, node):
        # Join -> Equality JoinRight
        return RULE.SetBoolType(node)

    def Expr(symbols, node):
        # Expr -> Join ExprRight
        if node.parent.syntax_item == 'ParExpr':
            node.properties['keep_temp'] = True
        check = RULE.SetBoolType(node)
        if check:
            assert node.parent.deriv_tuple
            is_eval = node.parent.deriv_tuple[0] == 'eval'
            if node.properties['data_type'] == 'void' and not is_eval:
                return Check.Error('Void expression in calculation')
            else:
                return Check.Pass()
        else:
            return check

    def Stmt(symbols, node):
        # Stmt -> Assign; |
        #         if(Expr) Stmts Else | while(Expr) Stmt |
        #         do Stmt while(Expr); | for(Assign; Expr; Assign) Stmt |
        #         break; | Block
        def check_bool_expr(cond_type, cond_expr):
            if cond_expr.properties['data_type'] not in ['bool', 'int']:
                return Check.Error('%s: bool expression required' % cond_type)
            else:
                return None
        def check_function_type(this_return_type):            
            func = node.function
            if not func:
                return Check.Error('Return statement not in function')
            if func.properties.get('return_type'):
                if func.properties['return_type'] != this_return_type:
                    return Check.Error(
                        '%s: return type conflict' % this_return_type
                    )
                else:
                    return None
            else:
                func.properties['return_type'] = this_return_type
        key = node.deriv_tuple[0]
        err = None
        if key in ['if', 'while']:
            # if(Expr) Stmt | while(Expr) Stmt
            err = check_bool_expr(key, node.children[2])
        elif key == 'do':
            # do Stmt while(Expr);
            err = check_bool_expr(key, node.children[4])
        elif key == 'for':
            # for(Assign; Expr; Assign) Stmt
            err = check_bool_expr(key, node.children[4])
        elif key == 'return':
            # return ReturnValue;
            err = check_function_type(node.children[1].properties['data_type'])
        return err if err is not None else Check.Pass()

    def ReturnValue(symbols, node):
        # ReturnValue -> ; | Expr;
        if node.deriv_tuple[0] == 'Expr':
            expr_node = node.children[0]
            node.properties['data_type'] = expr_node.properties['data_type']
        else:
            node.properties['data_type'] = 'void'
        return Check.Pass()

    def FunctionBody(symbols, node):
        # FunctionBody -> {"", FunctionType} { Decls Stmts }
        if node.deriv_tuple[0] == '->':
            f_type = node.children[0]
            node.properties['return_type'] = f_type.properties['return_type']
        return Check.Pass()

    def FunctionType(symbols, node):
        # FunctionType -> -> Type
        data_type = node.children[1].properties['data_type']
        node.properties['return_type'] = data_type
        name = node.function.children[1].token.string
        symbols['_functions'][name]['return_type'] = data_type
        return Check.Pass()

    def Function(symbols, node):
        # Fucntion -> def ident(ParaList) FunctionBody
        name = node.children[1].token.string
        body = node.children[-1]
        decl_type = body.properties.get('return_type')
        detect_type = node.properties.get('return_type') or 'void'
        if decl_type and decl_type != detect_type:
            return Check.Error(
                'Return type conflict: Defined=%s, Detected=%s'
                % (decl_type, detect_type)
            )
        para_list_node = node.children[3]
        para_list = para_list_node.properties['para_list']
        node.properties['name'] = name
        node.properties['para_list'] = para_list
        node.properties['return_type'] = detect_type
        assert symbols['_functions'].get(name)
        symbols['_functions'][name]['return_type'] = detect_type
        return Check.Pass()
        
    def ParaListRight(symbols, node):
        # ParaListRight -> "" | , Type ident ParaListRight
        if not node.children:
            para_list = ()
        else:
            data_type = node.children[1].properties['data_type']
            ident = node.children[2].token.string
            right = node.children[-1]
            para_list = tuple([
                (data_type, ident),
                *right.properties['para_list']
            ])
        node.properties['para_list'] = para_list
        return Check.Pass()

    def ParaList(symbols, node):
        # ParaList -> Type ident ParaListRight
        if not node.children:
            para_list = ()
        else:
            data_type = node.children[0].properties['data_type']
            ident = node.children[1].token.string
            right = node.children[-1]
            para_list = (
                (data_type, ident),
                *right.properties['para_list']
            )
        node.properties['para_list'] = para_list
        for para_type, para_name in para_list:
            node.function.properties['symbols'][para_name] = para_type
        name = node.function.children[1].token.string
        if not symbols['_functions'].get(name):
            symbols['_functions'][name] = {
                'parameters': tuple(p[0] for p in para_list)
            }
        else:
            return Check.Error('Function %s: Duplicate definition' % name)
        return Check.Pass()

