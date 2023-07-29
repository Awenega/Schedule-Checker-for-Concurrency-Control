
def solveConflict(schedule):
    """
    Checks if the schedule is conflict serializable
    """

# initialize set of transactions
    transactions = set([op.operation_type for op in schedule])

    # initialize precedence graph
    graph = {tx: set() for tx in transactions}

    # populate precedence graph
    for op1, i in zip(schedule, range(len(schedule))):
        for op2 in schedule[i+1:]:
            if op1.object != op2.object:
                continue
            if op1.operation_type == op2.operation_type:
                continue
            if op1.id_transaction == 'WRITE' or op2.id_transaction == 'WRITE':
                graph[op1.operation_type].add(op2.operation_type)

    def DFS(node_current, node_start, visited):
        """ Returns True whether there is a cycle starting and ending to node_start"""
        for children in graph[node_current]:
            if children == node_start:
                return True
            if not children in visited:
                visited.add(children)
                is_cycle = DFS(children, node_start, visited)
                if is_cycle:
                    return is_cycle
        return False

    cycle_on_node = map(lambda n: DFS(n, n, set()), graph)
    # if there is a cycle on any node is not c.s., hence return False
    return not any(cycle_on_node)


if __name__ == '__main__':
    import sys
    from utils import parse_schedule

    # schedule_str = 'w3(A)w2(C)r1(A)w1(B)r1(C)r4(A)w4(D)'
    # schedule_str = 'w1(x)r2(x)w1(z)r2(z)r3(x)r4(z)w4(z)w2(x)'
    schedule_str = 'w1(x)r1(z)r2(z)w1(z)r3(x)r4(z)w4(z)w2(x)'
    # schedule_str = 'r3(z)r1(z)w2(y)w4(x)w3(z)w3(y)r1(x)w2(x)'

    schedule = parse_schedule(schedule_str)

    res = solveConflict(schedule)

    print('Is ser?', res)
