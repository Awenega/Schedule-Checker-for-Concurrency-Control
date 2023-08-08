def SolveACR(schedule):
    isACR, ConflictPair = read_from_ACR(schedule, id)
    return isACR, ConflictPair


def read_from_ACR(schedule, transaction_id):
    read_from_id = set()
    commitedTransactions = set()
    for action in schedule:
        if action.action_type == 'COMMIT':
            commitedTransactions.add(action.id_transaction)
    for first in range(len(schedule)):
        firstAction = schedule[first]
        if firstAction.action_type == 'READ' or firstAction.action_type == 'COMMIT' or firstAction.id_transaction == transaction_id:
            continue

        for second in range(first + 1, len(schedule)):
            secondAction = schedule[second]

            if secondAction.action_type == 'READ' and secondAction.id_transaction == transaction_id and firstAction.object == secondAction.object:
                read_from_id.add(firstAction.id_transaction)
    return True, None
