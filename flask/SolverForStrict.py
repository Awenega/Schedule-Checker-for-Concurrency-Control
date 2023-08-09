def get_all_commits(schedule):
    committed_transaction_index = {}
    for action in schedule:
        if action.action_type == 'COMMIT' or action.isLastAction:
            committed_transaction_index[action.id_transaction] = schedule.index(action)
    return committed_transaction_index

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

def write_from(schedule):
    write_from = []
    for first in range(len(schedule)):
        firstAction = schedule[first]
        if firstAction.action_type == 'READ' or firstAction.action_type == 'COMMIT':
            continue

        for second in range(first + 1, len(schedule)):
            secondAction = schedule[second]

            if secondAction.action_type == 'WRITE' and firstAction.id_transaction != secondAction.id_transaction and firstAction.object == secondAction.object:
                write_from.append((secondAction, firstAction))
    return write_from

def check_read_from_committed_transaction(schedule, conflicting_pair, indexes_of_commits):
    #calcolo posizione nella schedule del commit della transazione che fa la write,
    #calcolo posizione nella schedule della read 
    #se posizione della read è successiva alla posizione del commit della write è ok, altrimenti NO STRICT
    read_action = conflicting_pair[0]
    write_action = conflicting_pair[1]
    index_of_commit_of_the_write = indexes_of_commits[write_action.id_transaction]
    index_of_read = schedule.index(read_action)
    if index_of_read < index_of_commit_of_the_write:
        return False
    else:
        return True

def check_write_from_committed_transaction(schedule, conflicting_pair, indexes_of_commits):
    #calcolo posizione nella schedule del commit della transazione che ha fatto l'ultima write sull'oggetto
    #calcolo posizione nella schedule della nuova write
    #se posizione della nuova write è successiva alla posizione del commit della precedente write è ok, altrimenti NO STRICT
    write_action_1 = conflicting_pair[0]
    write_action_2 = conflicting_pair[1]
    index_of_commit_of_the_write_action_2 = indexes_of_commits[write_action_2.id_transaction]
    index_of_write_action_1 = schedule.index(write_action_1)
    if index_of_write_action_1 < index_of_commit_of_the_write_action_2:
        return False
    else:
        return True
    
def SolveStrict(schedule):
    indexes_of_commits = get_all_commits(schedule)
    read_from_actions = read_from(schedule)
    write_from_actions = write_from(schedule)
    for conflicting_pair in read_from_actions:
        read_from_committed_transaction = check_read_from_committed_transaction(schedule, conflicting_pair, indexes_of_commits)
        if read_from_committed_transaction is not True:
            return False
    
    for conflicting_pair in write_from_actions:
        write_from_committed_transaction = check_write_from_committed_transaction(schedule, conflicting_pair, indexes_of_commits)
        if write_from_committed_transaction is not True:
            return False
    return True

# w1(A)w2(A)w3(A)w4(A)