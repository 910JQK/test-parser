CALCULATION = {
    # Arithmetic
    'plus': lambda x,y: (x + y),
    'minus': lambda x,y: (x - y),
    'mul': lambda x,y: (x * y),
    'div': lambda x,y: (x / y),
    # Relation
    'gt': lambda x,y: (x > y),
    'lt': lambda x,y: (x < y),
    'ge': lambda x,y: (x >= y),
    'le': lambda x,y: (x <= y),
    'eq': lambda x,y: (x == y),
    'neq': lambda x,y: (x != y),
    # Logic
    'and': lambda x,y: (x and y),
    'or': lambda x,y: (x or y),
    'not': lambda x,y: (not x),
    # Do Nothing
    'mov': lambda x,y: x
}


OPERATION = [
    'read', 'print',
    'label', 'goto', 'if_goto'
]


class RuntimeError(Exception):
    def __init__(self, obj, msg):
        self.obj = obj
        self.msg = msg
    def __str__(self):
        return '%s\n[Error] %s' % (obj, msg)


class Argument:

    arg_type = 'data'
    data_type = 'int'
    data = None # Variant
    ident = None # String

    def __init__(self, arg_type, data_type, val):
        assert arg_type in ['data', 'ident']
        self.arg_type = arg_type
        self.data_type = data_type
        if self.arg_type == 'data':
            self.data = val
        else:
            self.ident = val

    def __str__(self):
        if self.arg_type == 'data':
            return str(self.data)
        else:
            return '%s::%s' % (self.data_type, self.ident)

    def val(self, var_dict):
        if self.arg_type == 'data':
            data = self.data
        else:
            if var_dict.get(self.ident):                
                data = var_dict[self.ident]
            else:
                raise RuntimeError(
                    self, '%s: Variable Not Found' % self.ident
                )
        # Todo: Error Handling for Invalid Input
        if self.data_type == 'int':
            return int(data) & 0xffffffff
        elif self.data_type == 'double':
            return float(data)
        elif self.data_type == 'bool':
            return bool(data)
        else:
            raise RuntimeError(
                self, '%s: Invalid Data Type' % self.data_type
            )
        return data


class Instruction:

    def __init__(self, cmd, arg1, arg2=None, arg3=None): 
        self.cmd = cmd
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        # check if valid
        if cmd in CALCULATION:
            self.inst_type = 'calculation'
        elif cmd in OPERATION:
            self.inst_type = 'operation'
        else:
            raise RuntimeError(self, 'Invalid Instruction')
        # Todo: Other Checks for Specified Command

    def __str__(self):
        if self.arg2 is None:
            return '%s %s' % (self.cmd, self.arg1)
        elif self.arg3 is None:
            return '%s %s << %s' % (self.cmd, self.arg1, self.arg2)
        else:
            return (
                '%s %s << [%s, %s]'
                % (self.cmd, self.arg1, self.arg2, self.arg3)
            )


class Machine:
    var_dict = None # dict
    label_dict = None # dict

    def __init__(self):
        self.clear()

    def clear(self):
        self.var_dict = {}

    def run(self, instructions):
        label_dict = {}
        for i in range(0, len(instructions)):
            inst = instructions[i]
            if inst.cmd == 'label':
                label_name = inst.arg1
                label_dict[label_name] = i
        i = 0
        var_dict = self.var_dict
        while i < len(instructions):
            inst = instructions[i]
            #print(inst)
            inst_type = inst.inst_type
            cmd = inst.cmd
            arg1 = inst.arg1
            arg2 = inst.arg2
            arg3 = inst.arg3
            if inst_type == 'calculation':
                f = CALCULATION[cmd]
                ident = arg1.ident
                var_dict[arg1.ident] = f(
                    arg2.val(var_dict), arg3.val(var_dict)
                )
            elif cmd == 'read':
                ident = arg1.ident
                var_dict[arg1.ident] = input()
                _ = arg1.val(var_dict)
            elif cmd == 'print':
                print(arg1.val(var_dict))
            elif cmd == 'label':
                pass
            elif cmd == 'goto' or 'if_goto':
                if cmd == 'goto':
                    condition = True
                    label_name = arg1
                else:
                    condition = arg1.val(var_dict)
                    label_name = arg2
                if condition:
                    if label_dict.get(label_name):
                        i = label_dict[label_name] + 1
                        continue
                    else:
                        raise RuntimeError(
                            inst, '%s: Invalid Label' % label_name
                        )
                else:
                    pass
            else:
                raise RuntimeError(inst, '%s: Invalid Command' % cmd)
            i = i + 1
            

            

