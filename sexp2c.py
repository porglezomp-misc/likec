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
            struct = 'struct {name} {{\n{body}\n}};'.format(
                name=item[1],
                body='\n'.join(emit_typed_var(pair) + ';' for pair in item[2:]),
            )
            output.append(struct)
        elif item[0] == 'fn':
            fn = '{ret} {name}({args}) {{\n{body}\n}}'.format(
                ret=item[2],
                name=item[1][0],
                args=', '.join(emit_typed_var(pair) for pair in item[1][1:]),
                body='\n'.join(emit_statement(stmt) for stmt in item[3:]),
            )
            output.append(fn)

        output.append('')

    return '\n'.join(output)


def emit_for_first(case):
    if case[0] == 'let!':
        return '{} = {}'.format(emit_typed_var(case[1]), emit_expr(case[2], False))
    return emit_expr(case, False)


def emit_statement(stmt):
    assert isinstance(stmt, list)
    if stmt[0] == 'let!':
        return '{} = {};'.format(emit_typed_var(stmt[1]), emit_expr(stmt[2], False))
    if stmt[0] == 'set!':
        return '{} = {};'.format(stmt[1], emit_expr(stmt[2], False))
    elif stmt[0] == 'if':
        output = 'if ({cond}) {{\n{code}\n}}'.format(
            cond=emit_expr(stmt[1], False),
            code=emit_statement(stmt[2]),
        )
        if len(stmt) > 3:
            output += ' else {{\n{code}\n}}'.format(
                code=emit_statement(stmt[3]),
            )
        return output
    elif stmt[0] == 'for':
        return 'for ({first}; {test}; {after}) {{\n{body}\n}}'.format(
            first=emit_for_first(stmt[1][0]),
            test=emit_expr(stmt[1][1], False),
            after=emit_expr(stmt[1][2], False),
            body='\n'.join(emit_statement(s) for s in stmt[2:]),
        )
    elif stmt[0] == 'while':
        return 'while ({cond}) {{\n{body}\n}}'.format(
            cond=emit_expr(stmt[1], False),
            body='\n'.join(emit_statement(s) for s in stmt[2:]),
        )
    elif stmt[0] == 'block!':
        return '{{{items}}}'.format('\n'.join(emit_statement(s) for s in stmt[1:]))
    elif stmt[0] == 'return':
        return 'return {};'.format(emit_expr(stmt[1], False))
    else:
        return emit_expr(stmt, False) + ';'


def emit_expr(expr, parenthesize=True):
    if isinstance(expr, list):
        if len(expr) == 2 and expr[0] in ('+', '-', '++', '--', '~'):
            content = expr[0] + emit_expr(expr[1])
            if parenthesize:
                content = '({})'.format(content)
            return content
        if expr[0] in ('+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', '&&', '||'):
            op = ' ' + expr[0] + ' '
            content = op.join(emit_expr(e) for e in expr[1:])
            if parenthesize:
                content = '({})'.format(content)
            return content
        elif expr[0] == 'str!':
            return '"{}"'.format(' '.join(expr[1:]))
        else:
            return '{}({})'.format(
                expr[0],
                ', '.join(emit_expr(e, False) for e in expr[1:])
            )
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
                  (fib (- n 2)))))))

 (fn (fib1 (n int)) int
   (let! (a int) 0)
   (let! (b int) 1)
   (for ((let! (i int) 0)
         (< i n)
         (++ i))
     (let! (c int) b)
     (set! b (+ a b))
     (set! a c))
   (return a))

  (fn (mainloop (running bool)) void
    (while running
      (set! running false)))

  (fn (peano_add (a int) (b int)) int
    (while (> a 0)
      (-- a)
      (++ b))
    (return b)))
'''


def demo():
    print(emit_module(sexp.loads(code_sample)))
