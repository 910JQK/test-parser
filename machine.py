from common import e_print


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
}


OPERATION = [
    'start',    
    'read', 'print',
    'proc', 'end', 'call', 'ret', 'exit',
    'static', 'alloc', 'override', 'mov',
    'label', 'goto', 'goto_if', 'goto_if_false'
]


RETVAL = '_retval'
GETVAL = '_getval'
ARG_PREFIX = '_arg'
TEMP_PREFIX = '_t'


class RuntimeError(Exception):
    def __init__(self, obj, msg):
        self.obj = obj
        self.msg = msg
    def __str__(self):
        return '%s\n[Error] %s' % (str(self.obj), self.msg)


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
            return self.ident

    def val(self, var_dict):
        if self.arg_type == 'data':
            data = self.data
        else:
            if var_dict.get(self.ident) is not None:
                data = var_dict[self.ident]
            else:
                raise RuntimeError(
                    self, '%s: Variable Not Found' % self.ident
                )
        # Todo: Error Handling for Invalid Input
        if self.data_type == 'int':
            int_val = int(data)
            if int_val > 0:
                return int_val & 0xffffffff
            else:
                return -((-int_val) & 0xffffffff)
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

    def __init__(self, cmd, arg1=None, arg2=None, arg3=None): 
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
        if self.arg1 is None:
            return self.cmd
        elif self.arg2 is None:
            return '%s %s' % (self.cmd, self.arg1)
        elif self.arg3 is None:
            return '%s %s %s' % (self.cmd, self.arg1, self.arg2)
        else:
            return (
                '%s %s %s %s'
                % (self.cmd, self.arg1, self.arg2, self.arg3)
            )


class Machine:
    call_stack = None # list

    def __init__(self):
        self.clear()

    def clear(self):
        self.call_stack = [{'pos':0,'var_dict':{'_type':{}}}]

    def run(self, instructions):
        label_dict = {}
        proc_dict = {}
        proc_end_dict = {}
        start = 0
        for i in range(0, len(instructions)):
            inst = instructions[i]
            if inst.cmd == 'label':
                label_name = inst.arg1
                label_dict[label_name] = i
            elif inst.cmd == 'proc':
                proc_name = inst.arg1
                proc_dict[proc_name] = i
            elif inst.cmd == 'end':
                proc_name = inst.arg1
                proc_end_dict[proc_name] = i
            elif inst.cmd == 'start':
                if start == 0:
                    start = i
                else:
                    raise RuntimeError(inst, 'More than 1 start point')
        i = start
        call_stack = self.call_stack
        def is_in_stack():
            return len(call_stack) > 1
        def check_type(ident_arg, var_dict):
            if ident_arg.arg_type != 'ident':
                return
            elif ident_arg.ident.startswith(TEMP_PREFIX):
                return
            elif ident_arg.ident.startswith(ARG_PREFIX):
                return
            ident = ident_arg.ident
            if var_dict.get(ident) is not None:
                stored_type = var_dict['_type'][ident]
                if stored_type == ident_arg.data_type:
                    pass
                else:
                    raise RuntimeError(inst, 'Wrong Data Type')
            else:
                raise RuntimeError(inst, '%s: Invalid Address' % ident)
        while i < len(instructions):
            heap_var_dict = call_stack[0]['var_dict']
            stack_var_dict = call_stack[-1]['var_dict'] if is_in_stack() else {}
            var_dict = {**heap_var_dict, **stack_var_dict}
            def get_active_var_dict(ident):
                if ident.startswith(TEMP_PREFIX):
                    return stack_var_dict
                else:
                    if stack_var_dict.get(ident) is not None:
                        return stack_var_dict
                    else:
                        return heap_var_dict
            inst = instructions[i]
            e_print('[Run] %d: %s' % (i, inst))            
            inst_type = inst.inst_type
            cmd = inst.cmd
            arg1 = inst.arg1
            arg2 = inst.arg2
            arg3 = inst.arg3
            if inst_type == 'calculation':
                f = CALCULATION[cmd]
                ident = arg1.ident
                active = get_active_var_dict(ident)
                active[arg1.ident] = f(
                    arg2.val(var_dict), arg3 and arg3.val(var_dict)
                )
            elif cmd == 'mov':
                ident = arg1.ident
                active = get_active_var_dict(ident)
                check_type(arg1, active)
                check_type(arg2, var_dict)                
                active[ident] = arg2.val(var_dict)
            elif cmd == 'override':
                if is_in_stack():
                    ident = arg1.ident
                    active = get_active_var_dict(ident)
                    active[ident] = arg2.val(var_dict)
                    active['_type'][ident] = arg2.data_type
                else:
                    raise RuntimeError(
                        inst, 'Invalid Operation: Reallocate on Heap'
                    )
            elif cmd == 'static':
                assert arg3 and arg3.arg_type == 'data'
                ident = arg2
                data_type = arg1
                heap_var_dict[ident] = arg3.val({})
                heap_var_dict['_type'][ident] = data_type
            elif cmd == 'alloc':
                assert arg3 and arg3.arg_type == 'data'
                ident = arg2
                data_type = arg1
                if is_in_stack():
                    stack_var_dict[ident] = arg3.val({})
                    stack_var_dict['_type'][ident] = data_type
                else:
                    raise RuntimeError(
                        inst, 'Invalid Operation: Allocate on Heap'
                    )
            elif cmd == 'read':
                active = get_active_var_dict(ident)
                check_type(arg1, active)
                active[arg1.ident] = input()
                # check if input valid
                _ = arg1.val(var_dict)
            elif cmd == 'print':
                print(arg1.val(var_dict))
            elif cmd in ['label', 'start', 'end']:
                pass
            elif cmd == 'proc':
                proc_name = arg1
                if proc_end_dict.get(proc_name) is not None:
                    i = proc_end_dict[proc_name]
                else:
                    raise RuntimeError(
                        inst, '%s: End of procedure not defined' % proc_name
                    )
            elif cmd == 'call':
                call_stack.append({'pos': i, 'var_dict':{'_type':{}}})
                if proc_dict.get(arg1) is not None:
                    i = proc_dict[arg1]
                else:
                    raise RuntimeError(
                        inst, '%s: Procedure does not exist' % arg1
                    )
            elif cmd == 'ret':
                if is_in_stack():
                    not_void = stack_var_dict.get(RETVAL) is not None
                    if not_void:
                        retval_type = stack_var_dict['_type'][RETVAL]
                        retval = stack_var_dict[RETVAL]
                    last_call = call_stack.pop()
                    if not_void:
                        current_dict = call_stack[-1]['var_dict']
                        if (
                                len(call_stack) == 1
                                and current_dict.get(GETVAL) is not None
                                and (current_dict['_type'][GETVAL]
                                     != retval_type)
                        ):
                            raise RuntimeError(inst, 'Wrong Return Type')
                        else:
                            current_dict[GETVAL] = retval
                            current_dict['_type'][GETVAL] = retval_type
                    i = last_call['pos']
                else:
                    raise RuntimeError(inst, 'Unable to pop from call stack')
            elif cmd in ['goto', 'goto_if', 'goto_if_false']:
                if cmd == 'goto':
                    condition = True
                    label_name = arg1
                else:
                    condition = arg1.val(var_dict)
                    if cmd == 'goto_if_false':
                        condition = not condition
                    label_name = arg2
                if condition:
                    if label_dict.get(label_name) is not None:
                        i = label_dict[label_name]
                    else:
                        raise RuntimeError(
                            inst, '%s: Label does not exist' % label_name
                        )
                else:
                    pass
            elif cmd == 'exit':
                break
            else:
                raise RuntimeError(inst, '%s: Invalid Command' % cmd)
            i = i + 1
            

            

