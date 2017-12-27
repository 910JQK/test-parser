# Toy Parser (Just for fun)

## Overview

This is an interpreter for an **useless** programming language created by me for **practice**.

The program is built by 6 parts:

- `definition.py` Define the LL(1) syntax and sematic rules of the programming language
- `scanner.py` Scan source code files and match tokens using regular expression
- `syntax.py` Generate a syntax tree for the token series
- `translator.py` Traslate the syntax tree to 3-address code
- `machine.py` Virtual machine to run 3-address code
- `interpreter.py` Interpreter main program, takes argv[1] as code file

The language supports these features:

- ✅ Arithmetic operation for integer and  double
- ✅ Conditional clauses such as if, while, do, for
- ✅ Function definition and call with or without arguments
- ✅ Recursive function call
- ✅ Input and output for numbers

But does not support these features:

- ❌ OOP
- ❌ Array
- ❌ String
- ❌ Function pre-declaration
- ❌ External functions and linked library

In addition, code in this project may have plenty of bugs and won't be fixed, because it is just a practice.

By default, the interpreter will ouput debug messages, which can be disabled in `common.py` (set `DEBUG=False`).

## Example Codes

### Code 1

#### Source Code

```
$ cat test/test5
```

```
def f(int x, int y) {
    int i;
    for(i=0; i<10; i=i+1)
             y = y + i;
    return x + y;
}


def g(int x) -> int {
    return -x;
}


def h() {
    int x; int y;
    read x;
    read y;
    print f(x, y)*g(x);
}


def main() {
    eval h();
}
```

#### Intermediate Code

```
$ ./translate.py test/test5 2>/dev/null
```

```
proc f
alloc int _retval 0
alloc int y 0
mov y _arg1
alloc int x 0
mov x _arg0
alloc int i 0
mov i 0
label L0
lt _t0 i 10
goto_if_false _t0 L1
plus _t1 y i
mov y _t1
plus _t1 i 1
mov i _t1
goto L0
label L1
plus _t0 x y
mov _retval _t0
ret
ret
end f
proc g
alloc int _retval 0
alloc int x 0
mov x _arg0
minus _t0 0 x
mov _retval _t0
ret
ret
end g
proc h
alloc int x 0
alloc int y 0
read x
read y
override _arg0 x
override _arg1 y
call f
mov _t0 _getval
override _arg0 x
call g
mov _t1 _getval
mul _t2 _t0 _t1
print _t2
ret
end h
proc main
call h
exit
end main
start
call main
```

### Code 2

#### Source Code

```
$ cat test/test6
```

```
def f(int n) -> int {
    if(n < 0) {
         return 0;
    }
    if(n == 1 || n == 2) {
    	 return 1;
    } else {
      	 return f(n-1) + f(n-2);
    }
}


def main() {
    int n;
    read n;
    print f(n);
}
```

#### Intermediate Code

```
$ ./translator.py test/test6 2>/dev/null
```

```
proc f
alloc int _retval 0
alloc int n 0
mov n _arg0
lt _t0 n 0
goto_if_false _t0 L0
mov _retval 0
ret
goto L1
label L0
label L1
eq _t0 n 1
eq _t1 n 2
or _t2 _t0 _t1
goto_if_false _t2 L2
mov _retval 1
ret
goto L3
label L2
minus _t1 n 1
override _arg0 _t1
call f
mov _t1 _getval
minus _t0 n 2
override _arg0 _t0
call f
mov _t0 _getval
plus _t3 _t1 _t0
mov _retval _t3
ret
label L3
ret
end f
proc main
alloc int n 0
read n
override _arg0 n
call f
mov _t2 _getval
print _t2
exit
end main
start
call main
```

#### Run result

```
$ for i in {1..10}; do echo $i | ./interpreter.py test/test6 2>/dev/null; done
```

```
1
1
2
3
5
8
13
21
34
55
```