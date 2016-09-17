import toposort

# Exporting a module:
#
# 1. Gather all definitions in an organized format
# 2. Determine what the set of exports are
# 3. Determine the dependency graph between type declarations
# 4. Reject it if the dependencies of any concrete public type is abstract or private


def definitions(items):
    assert items[0] == 'module'
    items = items[1:]

    structs = {item[1]: item for item in items if item[0] == 'struct'}
    fns = {item[1][0]: item for item in items if item[0] == 'fn'}

    def props(export):
        return {'abstract': ['abstract'] in export[2:]}

    exports = {e[1]: props(e) for e in items if e[0] == 'export'}

    return fns, structs, exports


def find_depsgraph(defs):
    _, structs, exports = defs
    deps = {}
    abs_deps = {}
    for name in structs.keys():
        members = set()
        abs_members = set()
        for var, ty in structs[name][2:]:
            ty, abstract = find_core_type(ty)
            if ty in structs:
                if abstract:
                    abs_members.add(ty)
                else:
                    members.add(ty)
        deps[name] = members
        abs_deps[name] = abs_members
    return deps, abs_deps


def check_export_qualifiers(defs, deps):
    fns, structs, exports = defs
    deps, abs_deps = deps
    struct_exports = {e for e, props in exports.items() if e in structs}
    concrete_exports = {e for e, props in exports.items()
                        if e in structs and not props['abstract']}
    errors = set()
    for name, props in exports.items():
        if name in structs and not props['abstract']:
            for dep in deps[name]:
                if dep not in struct_exports:
                    errors.add((name, dep, 'not exported'))
                elif dep not in concrete_exports:
                    errors.add((name, dep, 'not concrete'))
            for dep in abs_deps[name]:
                if dep not in struct_exports:
                    errors.add((name, dep, 'not exported'))
        elif name in fns:
            if props['abstract']:
                errors.add((name, None, 'abstract function'))
    return errors


def format_depsgraph_errors(errors):
    errors = []
    for name, relies, reason in errors:
        if reason == 'not exported':
            message = "Exported struct `{0}` contains " \
                      "`{1}`, but `{1}` is not exported.".format(name, relies)
        elif reason == 'not concrete':
            message = "Exported struct `{0}` contains `{1}`, " \
                      "but `{1}` is an abstract type.".format(name, relies)
        elif reason == 'abstract function':
            message = "Exported function `{}` was marked as abstract, " \
                      "but functions cannot be abstract".format(name)
        else:
            message = "Exported struct `{}` contains `{}`. " \
                      "Error: `{}`.".format(name, relies, reason)
        error.append(message)
    return error


def sort_deps(deps):
    return toposort.toposort(deps[0], True)


def find_core_type(ty, abstract=False):
    if isinstance(ty, list):
        if ty[0] == 'ptr!':
            return find_core_type(ty[1], True)
        elif ty[0] == 'arr!':
            return find_core_type(ty[-1], abstract)
    return (ty, abstract)


def sample():
    import sexp
    with open('sample.lc', 'r') as f:
        return sexp.loads(f.read())


def module_interface(mod):
    fns, structs, exports = defs = definitions(mod)

    def make_export(elem):
        name, props = elem
        if name in fns:
            return fns[name][:3]
        elif name in structs:
            if props['abstract']:
                return ['struct', name]
            return structs[name]

    return ['interface'] + [make_export(e) for e in exports.items()]

# def construct_module(mod):
#     fns, structs, exports = defs = definitions(mod)
#     deps = find_depsgraph(defs)
#     errors = check_export_qualifiers(defs, deps)
#     if errors:
#         raise ValueError(errors)
#     sorted_deps = sort_deps(deps)
#     results = [structs[s] for s in sorted_deps if s in exports]
#     results += [fn for name, fn in fns.items() if name in exports]
#     return results
