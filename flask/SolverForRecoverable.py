def SolveRecoverability(schedule):
    isRecoverable = True
    ConflictPair = None

    transactions = set(action.id_transaction for action in schedule)

    commitedTransactions = set()
    for action in schedule:
        if action.action_type == 'COMMIT':
            commitedTransactions.add(action.id_transaction)

    for id in transactions:
        read_from_id = read_from(schedule, id)
        if len(read_from_id) > 0:
            ended = False
            for action in schedule:
                if ended:
                    if action.id_transaction in read_from_id:
                        return False, (id, action.id_transaction)
                else:
                    if action.id_transaction == id and (action.action_type == 'COMMIT' or (action.isLastAction and not (action.id_transaction in commitedTransactions))):
                        ended = True
    return isRecoverable, ConflictPair


def read_from(schedule, transaction_id):
    read_from_id = set()
    for first in range(len(schedule)):
        firstAction = schedule[first]
        if firstAction.action_type == 'READ' or firstAction.action_type == 'COMMIT' or firstAction.id_transaction == transaction_id:
            continue

        for second in range(first + 1, len(schedule)):
            secondAction = schedule[second]

            if secondAction.action_type == 'READ' and secondAction.id_transaction == transaction_id and firstAction.object == secondAction.object:
                read_from_id.add(firstAction.id_transaction)
    return read_from_id
