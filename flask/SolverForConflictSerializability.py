def SolveConflictSerializability(schedule):
    transactions = set([op.id_transaction for op in schedule])

    graph = {tx: set() for tx in transactions}

    for op1, i in zip(schedule, range(len(schedule))):
        if op1.action_type == 'COMMIT':
            continue
        for op2 in schedule[i+1:]:
            if op1.object != op2.object:
                continue
            if op1.id_transaction == op2.id_transaction:
                continue
            if op1.action_type == 'WRITE' or op2.action_type == 'WRITE':
                graph[op1.id_transaction].add(op2.id_transaction)

    def DFS(node_current, node_start, visited):
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

    return not any(cycle_on_node)
