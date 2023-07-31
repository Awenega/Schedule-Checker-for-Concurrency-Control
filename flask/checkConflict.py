def solveConflict(schedule):
    """
    Checks if the schedule is conflict serializable
    """

# initialize set of transactions
    transactions = set([op.id_transaction for op in schedule])

    # initialize precedence graph
    graph = {tx: set() for tx in transactions}

    # populate precedence graph
    for op1, i in zip(schedule, range(len(schedule))):
        for op2 in schedule[i+1:]:
            if op1.object != op2.object:
                continue
            if op1.id_transaction == op2.id_transaction:
                continue
            if op1.operation_type == 'WRITE' or op2.operation_type == 'WRITE':
                graph[op1.id_transaction].add(op2.id_transaction)

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

    precedence_graph = []
    start = 0
    num_operations = len(schedule)
    while start < num_operations:
        end = start + 1
        while end < num_operations:
            op1 = schedule[start]
            op2 = schedule[end]
            if op1 != op2 and (op2.operation_type == 'WRITE' or op1.operation_type == 'WRITE') and op1.id_transaction != op2.id_transaction and op1.object == op2.object:
                # An edge exists between op1 and op2 if op1 is a write operation and op2 is a read operation on the same object
                precedence_graph.append(
                    [op1.id_transaction, op2.id_transaction])
            end += 1
        start += 1
    return not any(cycle_on_node), precedence_graph
