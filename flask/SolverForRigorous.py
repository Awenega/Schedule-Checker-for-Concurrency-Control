def SolveRigorousness(schedule):
    confliction_actions_dict = get_conflicting_actions(schedule)
    print(confliction_actions_dict)
    for object in confliction_actions_dict:
        for action_1 in confliction_actions_dict[object]:
            id_transaction_1 = action_1[0]
            action_type_1 = action_1[1]
            index_1 = action_1[2]
            for action_2 in confliction_actions_dict[object]:
                id_transaction_2 = action_2[0]
                action_type_2 = action_2[1]
                index_2 = action_2[2]
                print(action_1, action_2)
                if index_1 == index_2 or id_transaction_1 == id_transaction_2 or (action_type_1 == 'READ' and action_type_2 == 'READ') or index_1 > index_2:
                    continue
                else:
                    commit_operation = 'c'+id_transaction_1+'(None)'
                    commit_between_conflicting_actions, msg = check_commit_between(index_1, commit_operation, index_2, schedule)
                    if not commit_between_conflicting_actions:
                        return False, msg
    return True, f"because for every pair of conflicting action there is a commit between them"

def check_commit_between(index_1, commit_operation, index_2, schedule):
    portion_schedule = schedule[index_1 + 1: index_2]
    index_last_action_of_transaction_1 = get_index_of_last_action(schedule, schedule[index_1].id_transaction)
    print(commit_operation, schedule[index_1].isLastAction, index_last_action_of_transaction_1 < index_2 )
    if commit_operation in portion_schedule or schedule[index_1].isLastAction or index_last_action_of_transaction_1 < index_2:
        return True, None
    return False, f"because <strong>{commit_operation[:2]}</strong> <strong>is not</strong> between <strong>{schedule[index_1]}</strong> and <strong>{schedule[index_2]}</strong>"

def get_index_of_last_action(schedule, id_transaction_1):
    for action in schedule:
        if action.id_transaction == id_transaction_1 and action.isLastAction:
            return schedule.index(action)

def  get_conflicting_actions(schedule):
    confliction_actions = {}
    # Setup che dict with all object used by transactions
    for action in schedule:
        if action.object != 'None' and action.object not in confliction_actions:
            confliction_actions[action.object] = []

    # For each object, we have an array of actions that use that object
    for i in range(len(schedule)):
        action = schedule[i]
        if action.action_type == 'COMMIT':
            continue
        else:
            confliction_actions[action.object].append([action.id_transaction, action.action_type,i])
    
    return confliction_actions
    
# w1(A)w2(B)r2(A)w3(A) True
# r1(B)r2(A)w2(A)r1(A)w1(A) True
# r1(A)w1(A)r2(A)w2(A) True
# r1(A)r2(B)r3(A)r2(A)w1(A)w3(A) False, because c3 is not between r3(A) and w1(A)
# r1(B)w1(A)w2(B)w1(B)r2(A) False, False because c1 is not between r1(B) and w2(B)
