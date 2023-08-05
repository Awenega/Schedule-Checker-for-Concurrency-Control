def ComputePrecedenceGraph(schedule):
    precedence_graph = set()  # Using a set to avoid duplicates

    for first in range(len(schedule)):
        firstAction = schedule[first]

        for second in range(first + 1, len(schedule)):
            secondAction = schedule[second]

            if firstAction.id_transaction != secondAction.id_transaction and firstAction.object == secondAction.object:
                if (firstAction.action_type == 'WRITE' and secondAction.action_type == 'WRITE') or \
                   (firstAction.action_type == 'READ' and secondAction.action_type == 'WRITE') or \
                   (firstAction.action_type == 'WRITE' and secondAction.action_type == 'READ'):
                    precedence_graph.add(
                        (firstAction.id_transaction, secondAction.id_transaction))

    return list(precedence_graph)
