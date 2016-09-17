def reverse_edges(outgoing):
    result = {}
    for node, out in outgoing.items():
        if node not in result:
            result[node] = set()
        for edge in out:
            if edge not in result:
                result[edge] = set()
            result[edge].add(node)
    return result


def toposort(graph, inverse=False):
    if not inverse:
        incoming = reverse_edges(graph)
    else:
        incoming = extend_graph(graph)

    result = []
    while True:
        keep = {}
        remove = set()
        for node, deps in incoming.items():
            if not deps:
                result.append(node)
                remove.add(node)
            else:
                keep[node] = deps
        for node in keep.keys():
            keep[node] -= remove
        if not remove:
            break
        incoming = keep
    if keep:
        raise ValueError(keep)
    return result


def extend_graph(graph):
    for target in graph.values():
        for val in target:
            if val not in graph:
                graph[val] = set()
    return graph
