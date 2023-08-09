def SolveACR(schedule):
    isACR, ConflictPair = read_from_ACR(schedule)
    return isACR, ConflictPair


def read_from_ACR(schedule):
    commitedTransactions = set()
    for action in schedule:
        if action.action_type == 'COMMIT':
            commitedTransactions.add(action.id_transaction)

    for first in range(len(schedule)):
        firstAction = schedule[first]
        if firstAction.action_type == 'READ' or firstAction.action_type == 'COMMIT':
            continue

        haveCommit = False
        if firstAction.isLastAction and not (firstAction.id_transaction in commitedTransactions):
            haveCommit = True
        for second in range(first + 1, len(schedule)):
            secondAction = schedule[second]
            if not haveCommit and ((secondAction.action_type == 'COMMIT' and secondAction.id_transaction == firstAction.id_transaction) or (secondAction.isLastAction and secondAction.id_transaction == firstAction.id_transaction and not (secondAction.id_transaction in commitedTransactions))):
                haveCommit = True

            if secondAction.action_type == 'READ' and secondAction.id_transaction != firstAction.id_transaction and firstAction.object == secondAction.object:
                if not haveCommit:
                    return False, (secondAction.id_transaction, firstAction.id_transaction)
                else:
                    break

    return True, None
