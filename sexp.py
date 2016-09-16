def loads(string):
    """
    Return a nested list representing the deserialized s-expression.

    Examples
    >>> loads('()')
    []
    >>> loads('(+ 1 1)')
    ['+', 1, 1]
    >>> loads('(+ (* x1 x2) (* y1 y2))')
    ['+', ['*', 'x1', 'x2'], ['*', 'y1', 'y2']]
    >>> loads('"hello world"')
    ['(str)', 'hello world']
    """
    # result = None
    # result_stack = []
    # for char in string:
    #     pass

    tokens = string.replace('(', ' ( ').replace(')', ' ) ').split()
    return parse_tokens(tokens)


def dumps(sexp):
    """
    Return the string representation of an s-expression.

    Examples
    >>> dumps([])
    '()'
    >>> dumps(['+', 1, 1])
    '(+ 1 1)'
    >>> dumps(['+', ['*', 'x1', 'x2'], ['*', 'y1', 'y2']])
    '(+ (* x1 x2) (* y1 y2))'
    >>> dumps(['(str)', 'hello world'])
    '"hello world"'
    """
    if isinstance(sexp, list):
        if sexp and sexp[0] == '(str)':
            return '"{}"'.format(sexp[1])
        return '({})'.format(' '.join(dumps(s) for s in sexp))
    else:
        return str(sexp)


def parse_tokens(tokens):
    result = None
    result_stack = []
    for token in tokens:
        if result is not None:
            raise ValueError("s-exp parse error: unexpected " + token)

        if token == '(':
            result_stack.append([])
        elif token == ')':
            if not result_stack:
                raise ValueError("s-exp parse error: unexpected " + token)

            exp = result_stack.pop()
            if result_stack:
                result_stack[-1].append(exp)
            else:
                result = exp
        else:
            value = token
            # Attempt to convert to the best available number type
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass

            if result_stack:
                result_stack[-1].append(value)
            else:
                result = value

    if result_stack:
        raise ValueError("s-exp parse error: expected )")
    return result
