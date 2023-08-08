from itertools import permutations
from collections import Counter


def SolveViewSerializability(schedule):
    isViewSerializable = False

    transactions = set(action.id_transaction for action in schedule)

    read_from_schedule = read_from(schedule)
    last_write_schedule = last_write(schedule)

    for ordering in permutations(transactions):
        reordered_schedule = []
        for transaction_id in ordering:
            transaction_action = [
                action for action in schedule if action.id_transaction == transaction_id]
            reordered_schedule.extend(transaction_action)
        if (Counter(read_from(reordered_schedule)) == Counter(read_from_schedule) and last_write(reordered_schedule) == last_write_schedule):
            res_equivalent = ''
            for id in ordering:
                res_equivalent += 'T' + str(id)
            return True, res_equivalent

    return isViewSerializable, None


def last_write(schedule):
    last_write = {}
    for action in schedule:
        if action.action_type == 'READ' or action.action_type == 'COMMIT':
            continue
        else:
            last_write[action.object] = action.id_transaction

    return dict(last_write)


def read_from(schedule):
    read_from = []
    for first in range(len(schedule)):
        firstAction = schedule[first]
        if firstAction.action_type == 'READ' or firstAction.action_type == 'COMMIT':
            continue

        for second in range(first + 1, len(schedule)):
            secondAction = schedule[second]

            if secondAction.action_type == 'READ' and firstAction.id_transaction != secondAction.id_transaction and firstAction.object == secondAction.object:
                read_from.append((secondAction, firstAction))
    return read_from
