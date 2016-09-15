import sexp

def emit_module(items):
    assert items[0] == 'module'
    items = items[1:]
    output = []

    struct_decls = [item for item in items if item[0] == 'struct']
    for decl in struct_decls:
        output.append('typedef struct {0} {0};'.format(decl[1]))
    output.append('')

    fn_decls = [item for item in items if item[0] == 'fn']
    for decl in fn_decls:
        output.append('{ret} {name}({args});'.format(
            ret=decl[2],
            name=decl[1][0],
            args=', '.join(emit_typed_var(pair) for pair in decl[1][1:])
        ))
    output.append('')

    for item in items:
        if item[0] == 'struct':
            struct = 'struct {name} {{\n{body}\n}}'.format(
                name=item[1],
                body='\n'.join(emit_typed_var(pair) + ';' for pair in item[2:]),
            )
            output.append(struct)
        elif item[0] == 'fn':
            print(item)
            fn = '{ret} {name}({args}) {{\n{body}\n}}'.format(
                ret=item[2],
                name=item[1][0],
                args=', '.join(emit_typed_var(pair) for pair in item[1][1:]),
                body='\n'.join(emit_statement(stmt) for stmt in item[3:]),
            )
            output.append(fn)

        output.append('')

    return '\n'.join(output)


def emit_statement(stmt):
    assert isinstance(stmt, list)
    if stmt[0] == 'let!':
        print('let', stmt[1:])
    elif stmt[0] == 'if':
        output = 'if ({cond}) {{\n{code}\n}}'.format(
            cond=emit_expr(stmt[1]),
            code=emit_statement(stmt[2]),
        )
        if len(stmt) > 3:
            output += ' else {{\n{code}\n}}'.format(
                code=emit_statement(stmt[3]),
            )
        return output
    elif stmt[0] == 'for':
        print('for', stmt[1], stmt[2:])
        return ''
    elif stmt[0] == 'while':
        print('while', stmt[1], stmt[2:])
        return ''
    else:
        return emit_expr(stmt) + ';'


def emit_expr(expr):
    if isinstance(expr, list):
        print(expr)
        if expr[0] in ('+', '-', '*', '/'):
            return '({})'.format(expr[0].join(emit_expr(e) for e in expr[1:]))
        elif expr[0] == 'str!':
            return '"{}"'.format(' '.join(expr[1:]))
        else:
            return '{}({})'.format(expr[0], ', '.join(emit_expr(e) for e in expr[1:]))
    return str(expr)


def emit_call(expr):
    return str(expr)


def emit_typed_var(pair):
    """
    Return a type and name declaration.

    Examples
    >>> emit_typed_var(['foo', 'int'])
    'int foo'
    >>> emit_typed_var(['bar', ['ptr!', 'char']])
    'char *bar'
    >>> emit_typed_var(['baz', ['ptr!', ['ptr!', 'double']]])
    'double **baz'
    >>> emit_typed_var(['qux', ['arr!', ['ptr!', ['ptr!', 'int']]]])
    'int **qux[]'
    >>> emit_typed_var(['quux', ['ptr!', ['ptr!', ['arr!', 'int']]]])
    'int (**quux)[]'
    >>> emit_typed_var(['fizz', ['ptr!', ['arr!', 3, 'int']]])
    'int (*fizz)[3]'
    """
    name, ty = pair
    if isinstance(ty, list):
        if ty[0] == 'ptr!':
            return emit_typed_var(('*' + name, ty[1]))
        elif ty[0] == 'arr!':
            if name[0] == '*':
                name = '({})'.format(name)
            if len(ty) > 2:
                return emit_typed_var(('{}[{}]'.format(name, ty[1]), ty[2]))
            return emit_typed_var((name + '[]', ty[1]))
    return str(ty) + ' ' + name


code_sample = '''
(module
 (struct person
   (name (ptr! char))
   (age int))
 (fn (person_summary (p (ptr! person))) void
   (printf (str! %s is %d years old!) p->name p->age))
 (fn (fib (n int)) int
   (if (<= n 0)
     (return 0)
     (if (== n 1)
       (return 1)
       (return (+ (fib (- n 1))
                  (fib (- n 2))))))))
'''


def demo():
    print(emit_module(sexp.loads(code_sample)))
