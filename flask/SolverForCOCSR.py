from SolverForOCSR import get_all_possible_serial_schedule, is_schedule_containing_commits

def get_commit_order(schedule, commit_as_last_action):
    commit_order = []
    for action in schedule:
        if action.action_type == 'COMMIT' or (action.isLastAction and not commit_as_last_action):
            commit_order.append(action.id_transaction)
    return commit_order

def is_cocsr(serial_schedule, commit_order):
    print(serial_schedule, commit_order)
    for transaction_serial_schedule, transaction_commit_order in zip(serial_schedule, commit_order):
        if transaction_serial_schedule != transaction_commit_order:
            return False, f"because any possible serial schedule, doens't follow the commit order of S"
    serial_schedule_to_print = [f"T{transaction}" for transaction in serial_schedule]
    return True, f"<br>Serial Schedule Conflict Equivalent to S and is COCSR: <strong>{''.join(serial_schedule_to_print)}</strong>"

def solveCOCSR(schedule):
    # get che commit order transactions of S
    commit_as_last_action = is_schedule_containing_commits(schedule)
    commit_order = get_commit_order(schedule, commit_as_last_action)
    # get, if exist, all possible serial schedules that is conflict-equivalent to schedule
    possible_serial_schedules = get_all_possible_serial_schedule(schedule)
    # check that the commit order transaction of S is equal to the order of transactions in the serial schedule
    if possible_serial_schedules != None:
        for serial_schedule in possible_serial_schedules:
            result, msg = is_cocsr(serial_schedule, commit_order)
            if result:
                return result, msg
        return result, msg
    
    return False, "because not exist any serial schedule"

#w1(x)r2(x)c2w3(y)c3w1(y)c1 False, le possibili schedule seriali non hanno lo stesso ordine dei commit originali
#w1(x)r2(x)w3(y)c3w1(y)c1c2 True, T3T1T2
#r1(x)r2(x)r3(x) True, T1T2T3
#w3(y)c3w1(x)r2(x)c2w1(y)c1 # False, (commit order = 3-2-1, seriale = 3-1-2 )
#w3(y)c3w1(x)r2(x)w1(y)c1c2 # True, (commit order = 3-2-1, seriale = 3-2-1 )