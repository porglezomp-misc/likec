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
            args=', '.join('{} {}'.format(ty, name) for name, ty in decl[1][1:])
        ))
    output.append('')

    for item in items:
        print(item)

    return '\n'.join(output)

code_sample = '''
(module
 (struct person
   (name (ptr! char))
   (age int))
 (fn (person_summary (p person)) void
   (printf "%s is %d years old!" p.name p.age)))
'''

def demo():
    print(emit_module(sexp.loads(code_sample)))
