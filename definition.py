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
        re.compile('class|null|this|extends|return|new|NewArray|Print|ReadInteger|ReadLine')
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
        re.compile(r'\&\&|\|\||\=\=|\!|\+|\-|\*|\/|\&|%|\\|\<|\<\=|\>|\>\=|\=|\!\=|\;|\,|\.|\[|\]|\(|\)|\{|\}')
    ),
    (
        'ident',
        re.compile('[A-Za-z][0-9A-Za-z_]*')
    )
]


SYNTAX = {
    # Start -> Block
    'Start': {
        'empty': False,
        'derivations': [
            ('ANY', ('Block',))
        ]
    },
    # Block -> { Decls Stmts }
    'Block': {
        'empty': False,
        'derivations': [
            ('ANY', ('{', 'Decls', 'Stmts', '}'))
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
            ('cond_key', ('Stmt', 'Stmts')),
            ('{', ('Stmt', 'Stmts'))
        ]
    },
    # Stmt -> Assign; |
    #         if(Expr) Stmts Else | while(Expr) Stmt |
    #         do Stmt while(Expr); | for(Assign; Expr; Assign) Stmt |
    #         break; | Block
    'Stmt': {
        'empty': False,
        'derivations': [
            ('ident', ('Assign', ';')),
            ('if', ('if', '(', 'Expr', ')', 'Stmt', 'Else')),
            ('while', ('while', '(', 'Expr', ')', 'Stmt')),
            ('do', ('do', 'Stmt', 'while', '(', 'Expr', ')', ';')),
            ('for',
             ('for', '(', 'Assign', ';', 'Expr', ';', 'Assign', ')', 'Stmt')
            ),
            ('break', ('break', ';')),
            ('{', ('Block',))
        ]
    },
    # Assign -> Var = Expr AssignRight
    'Assign': {
        'empty': False,
        'derivations': [
            ('ANY', ('Var', '=', 'Expr', 'AssignRight'))
        ]
    },
    # AssignRight -> "" | = Expr
    'AssignRight': {
        'empty': True,
        'derivations': [
            ('=', ('=', 'Expr'))
        ]
    },
    # Else -> "" | else Stmt
    'Else': {
        'empty': True,
        'derivations': [
            ('else', ('else', 'Stmt'))
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
    # Expr -> Join ExprRight
    'Expr': {
        'empty': False,
        'derivations': [
            ('ANY', ('Join', 'ExprRight'))
        ]
    },
    # ExprRight -> "" | || Join
    'ExprRight': {
        'empty': True,
        'derivations': [
            ('||', ('||', 'Join'))
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
    # Oprand -> Var | integer_value | double_value | bool_value
    'Oprand': {
        'derivations': [
            ('ident', ('Var',)),
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
        if not symbols.get(ident):
            symbols[ident] = data_type
            return Check.Pass()
        else:
            return Check.Error('Identifier %s already defined' % ident)

    def Var(symbols, node):
        # Var -> ident VarRight
        ident = node.children[0].token.string
        if symbols.get(ident):
            node.properties['data_type'] = symbols[ident]
            return Check.Pass()
        else:
            return Check.Error('Variable %s not defined' % ident)
        
    def Oprand(symbols, node):
        # Oprand -> Var | integer_value | double_value | bool_value
        deriv_tuple = node.deriv_tuple
        token2data = {
            'integer_value': 'int',
            'bool_value': 'bool', 
            'double_value': 'double'
        }
        var_or_val = node.children[0]
        if deriv_tuple[0] == 'Var':
            data_type = var_or_val.properties['data_type']
        else:
            data_type = token2data[var_or_val.token.token_type]
        node.properties['data_type'] = data_type
        return Check.Pass()

    def ParExpr(symbols, node):        
        # ParExpr -> (Expr)
        expr = node.children[1]
        node.properties['data_type'] = expr.properties['data_type']
        return Check.Pass()

    def Unary(symbols, node):
        # Unary -> {+, -, !} Unary | ParExpr | Oprand
        op = node.deriv_tuple[0]
        oprand = node.children[-1]
        oprand_type = oprand.properties['data_type']
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
        return Check.Pass()

    def SetNumberType(node, item, right):
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

    def SetBoolType(node):
        if node.children:
            item = node.children[0]
            right = node.children[1]
            if right.children:
                node.properties['data_type'] = 'bool'
            else:
                node.properties['data_type'] = item.properties['data_type']
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
        return RULE.SetBoolType(node)

    def Stmt(symbols, node):
        # Stmt -> Assign; |
        #         if(Expr) Stmts Else | while(Expr) Stmt |
        #         do Stmt while(Expr); | for(Assign; Expr; Assign) Stmt |
        #         break; | Block
        def check_bool_expr(cond_expr):
            if cond_expr.properties['data_type'] not in ['bool', 'int']:
                return Check.Error('if: bool expression required')
            else:
                return None
        deriv_tuple = node.deriv_tuple
        err = None
        if deriv_tuple[0] in ['if', 'while']:
            err = check_bool_expr(node.children[2])
        elif deriv_tuple[0] == 'do':
            err = check_bool_expr(node.children[4])
        elif deriv_tuple[0] == 'for':
            err = check_bool_expr(node.children[4])
        return err if err is not None else Check.Pass()

