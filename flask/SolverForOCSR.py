from SolverForViewSerializability import read_from, last_write
from itertools import permutations
from collections import Counter


def get_initial_order(schedule):
    order_to_preserve = []
    for action in schedule:
        if action.id_transaction not in order_to_preserve:
            order_to_preserve.append(action.id_transaction)
    return order_to_preserve

def completely_precedes(transaction_1, transaction_2, schedule, commit_as_last_action):
    first_index_T1 = 0
    last_index_T1 = 0
    already_updated = False
    for action in schedule:
        if action.id_transaction == transaction_1:
            if action.action_type == 'COMMIT' or (action.isLastAction and not commit_as_last_action):
                last_index_T1 = schedule.index(action)
            elif not already_updated:
                first_index_T1 = schedule.index(action)
                already_updated = True

    for action in schedule[first_index_T1 : last_index_T1]:
        if action.id_transaction == transaction_2:
            return False
    
    return True

def is_schedule_containing_commits(schedule):
    for action in schedule:
        if action.action_type == 'COMMIT':
            return True
    return False

def get_all_possible_serial_schedule(schedule):
    transactions = set(action.id_transaction for action in schedule)

    read_from_schedule = read_from(schedule)
    last_write_schedule = last_write(schedule)
    serial_schedules = []
    for ordering in permutations(transactions):
        reordered_schedule = []
        for transaction_id in ordering:
            transaction_action = [
                action for action in schedule if action.id_transaction == transaction_id]
            reordered_schedule.extend(transaction_action)
        if (Counter(read_from(reordered_schedule)) == Counter(read_from_schedule) and last_write(reordered_schedule) == last_write_schedule):
            possible_order = []
            for id in ordering:
                possible_order.append(id)
            serial_schedules.append(possible_order)

    if len(serial_schedules) > 0:
        return serial_schedules
    else:
        return None

def is_ocsr(serial_schedule, must_comes_before):
    for transactions in must_comes_before:
        transaction_comes_before = transactions[0]
        transaction_comes_after = transactions[1]
        # ordine rispettato se indice di comes_before < indice di comes_after
        if serial_schedule.index(transaction_comes_before) > serial_schedule.index(transaction_comes_after):
            return False, f"because T{transaction_comes_before} must come before T{transaction_comes_after}"
    serial_schedule_to_print = [f"T{transaction}" for transaction in serial_schedule]
    return True, f"<br>Serial Schedule Conflict Equivalent to S and OCSR: <strong>{''.join(serial_schedule_to_print)}</strong>"

def solveOCSR(schedule):
    order = get_initial_order(schedule)
    commit_as_last_action = is_schedule_containing_commits(schedule)
    must_comes_before = []
    for index, transaction_1 in enumerate(order):
        for transaction_2 in order[index+1:]:
            if completely_precedes(transaction_1, transaction_2, schedule, commit_as_last_action):
                must_comes_before.append([transaction_1, transaction_2])
    
    possible_serial_schedules = get_all_possible_serial_schedule(schedule)        
    if possible_serial_schedules != None:
        for serial_schedule in possible_serial_schedules:
            result, msg = is_ocsr(serial_schedule, must_comes_before)
            if result:
                return result, msg
        return result, msg
            
    return False, "because not exist any serial schedule"

# w1(x)r2(x)c2w3(y)c3w1(y)c1 FALSE because T2 comes before T3, but in serial T3T1T2 doesn't come before
# w1(x)
# w1(x)r2(x)w1(y)c1c2 TRUE perchè la schedule originale non ha nessun ordine da rispettare, quindi basta avere una serial schedule conflict equivalent?
# w1(x)r2(x)r2(y)c2c1 #TRUE T1T2
# w3(y)c3w1(x)r2(x)c2w1(y)c1 #TRUE T3T1T2 dalle slide
# r1(x)r2(x)r3(x) #TRUE