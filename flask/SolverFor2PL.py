from Scheduler import formatSchedule
from Actions import Action

states = {}
schedule = []
transactions = []
x_unlocks = []
unlocks = []
locks = []
use_xl_only = False

# Setup transactions and objects variables
def get_all_transactons_and_objects(schedule):
    transaction = []
    objects = []
    for action in schedule:
        if action.id_transaction not in transaction:
            transaction.append(action.id_transaction)
        if action.object not in objects:
            objects.append(action.object)
    return transaction, objects

# Represents if an object is available for locking/unlocking by the transaction. Values: 'BEGIN', 'sl', 'xl', 'u'
def setup_initial_states(transactions, objects):
    states = {}
    for transaction in transactions:
        if transaction not in states:
            states[transaction] = {}
        for object in objects:
            states[transaction][object] = 'BEGIN'
    return states

# Setup initial unlocks variables
def setup_initial_unlocks(transactions):
    x_unlocks = {} # true when the transaction has unlock the first exclusive lock
    unlocks = {} # true when the transaction has unlock the first lock (both shared or exclusive)
    for transaction in transactions:
        x_unlocks[transaction] = False
        unlocks[transaction] = False
    return x_unlocks, unlocks

# Store lock/unlock actions. An array [] for every transaction i in the schedule, +1 to add unlocks actions at the end
def setup_locks(schedule):
    ret = []
    for i in range(len(schedule)+1):
        ret.append([])
    return ret

# Given a 'state', it returns all the transactions with the object 'obj' in the state 'state' 
def getTransactionsToUnlock(transactions, states, type_of_unlock_needed, obj, currentTransaction):
    transaction_to_unlock = []
    for type_of_unlock in type_of_unlock_needed:
        ret_unlock = []
        for transaction in transactions:
            if states[transaction][obj] == type_of_unlock:
                ret_unlock.append(transaction)
        transaction_to_unlock.append(ret_unlock)
    ret = mergeUnlocks(transaction_to_unlock, currentTransaction)
    return ret

# Returns a list with all the transactions having unlocks to be done(both shared and exlusive) on the same object, without the currentTransaction
def mergeUnlocks(transaction_to_unlock, currentTransaction):
    final_to_unlock_list = []
    for to_unlock_list in transaction_to_unlock:
        for transaction in to_unlock_list:
            if transaction not in final_to_unlock_list and transaction != currentTransaction:
                final_to_unlock_list.append(transaction)
    return final_to_unlock_list

# Return lists of object that the currentTransaction will read or write in future
def get_object_to_read_and_write(remaining_schedule, currentTransaction):
    to_read = []
    to_write = []
    to_read_only = []
    # get to_write objects (for them we need the exclusive lock)
    for action in remaining_schedule:
        if action.id_transaction == currentTransaction and action.action_type == 'READ':  
            to_read.append(action.object)
        elif action.id_transaction == currentTransaction and action.action_type == 'WRITE':
            to_write.append(action.object)

    # get to_read_only objects (for them we only need the shared lock, not the exlusive)
    for elem in to_read:
        if elem not in to_write:
            to_read_only.append(elem)
    return to_read_only, to_write

# Unlock 'obj' for transaction 'currentTransaction'. We look in the future and check if, before unlocking an object, we need to acquire other locks.
def unlock(currentTransaction, obj, i):

    # The object is already unlocked or the transaction has just begun.
    if states[currentTransaction][obj] == 'u' or states[currentTransaction][obj] == 'BEGIN':
        return

    # We need to scan only the remaining schedule
    remaining_schedule = schedule[i+1:]

    # to_read_only contains objects that in the future will be readed-only by the transaction 'currentTransaction'. In this case we need only a shared lock
    # to_write contains objects that in the future will be written by the transaction 'currentTransaction'. In this case we need an exclusive lock
    to_read_only, to_write = get_object_to_read_and_write(remaining_schedule, currentTransaction)

    # for each object, we check if possible to acquire an exclusive lock ('xl'). 
    for obj_to_lock in to_write:
        ret = manageLocksAndState('xl', currentTransaction, obj_to_lock, i)
        if ret:
            return ret # Not 2PL

    # for each object, we check if possible to acquire a shared lock ('sl'). 
    for obj_to_lock in (to_read_only):
        ret = manageLocksAndState('sl', currentTransaction, obj_to_lock, i)
        if ret:
            return ret # Not 2PL

    # After all locks acquired, we can unlock the object 'obj' by the transaction 'currentTransaction'
    manageLocksAndState('u', currentTransaction, obj, i)

# Change the state of an 'obj' of 'transaction' to state 'target', adding the corresponding lock/unlock actions to solution list, and check if it is feasible.
def manageLocksAndState(target, currentTransaction, obj, i):
    
    if use_xl_only and target == 'sl':
        target = 'xl'

    if states[currentTransaction][obj] == target:
        return
    
    #if I want to do a shared lock, first I need to unlock the object from the transaction that has an exclusive lock
    #if I want to do a exclusive lock, then I need to unlock the object from the transaction that has any type of lock
    type_of_unlock_needed = ['xl'] if target == 'sl' else ['xl', 'sl']

    if target == 'sl' or target == 'xl':
        # Unlock transactions holding 'obj' in exclusive or shared lock before obtaining the desidered type of lock
        while True:
            transactions_to_unlock = getTransactionsToUnlock(transactions, states, type_of_unlock_needed, obj, currentTransaction)             
            # Check if there are transactions to unlock 
            if len(transactions_to_unlock) > 0:
                # If so, I take the last element in the list and start the unlock process for that object
                transaction_to_process = transactions_to_unlock.pop()
                # If the unlock is permitted, I will add the unlock in the locks array at position i
                ret = unlock(transaction_to_process, obj, i)
                if ret:
                    return ret  # Not 2PL
            else:
                break

    # strictness: check if the schedule unlocks an exclusive lock
    if states[currentTransaction][obj] == 'xl' and target == 'u':
        x_unlocks[currentTransaction] = True

    # strong strictness: check if the schedule unlocks any lock
    if (states[currentTransaction][obj] == 'xl' or states[currentTransaction][obj] == 'sl') and target == 'u':
        unlocks[currentTransaction] = True

    states[currentTransaction][obj] = target  # set target state
    
    # add the lock/unlock action to the solution
    tmp = Action(target, currentTransaction, obj)
    locks[i].append(tmp)

def solve2PL(schedule, use_xl_only_flag):
    global transactions
    global states
    global x_unlocks
    global unlocks
    global locks
    global use_xl_only

    ## SETUP VARIABLES ##
    use_xl_only = use_xl_only_flag
    transactions, objects = get_all_transactons_and_objects(schedule)
    states = setup_initial_states(transactions, objects)
    x_unlocks, unlocks = setup_initial_unlocks(transactions)
    is_strict, is_strong_strict = True, True
    locks = setup_locks(schedule)
    
    ## MAIN ##
    for i in range(len(schedule)):
        
        action = schedule[i]
        obj_state = states[action.id_transaction][action.object]          

        if x_unlocks[action.id_transaction]: #The transaction has unlocked an exclusive lock and executes another action
            is_strict = False
        elif unlocks[action.id_transaction]: #The transaction has unlocked a lock and executes another action
            is_strong_strict = False

        # READ operation needs to get share lock
        if action.action_type == 'READ' and obj_state == 'BEGIN':
            ret = manageLocksAndState('sl', action.id_transaction, action.object, i)
            if ret:
                return ret # Not 2PL
        elif action.action_type == 'READ' and obj_state == 'u': #the action is trying to read from an unlocked object.
            return f'Not 2PL: <strong>{action}</strong> is trying to read from an unlocked object', None, None

        # WRITE operation needs to get exclusive lock
        if action.action_type == 'WRITE' and (obj_state == 'BEGIN' or obj_state == 'sl'):
            err = manageLocksAndState('xl', action.id_transaction, action.object, i)
            if err:
                return err
        elif action.action_type == 'WRITE' and obj_state == 'u': #the action is trying to write to an unlocked object
                return f'Not 2PL: <strong>{action}</strong> is trying to write to an unlocked object', None, None

    # Unlocks all the resources in use at the end of the schedule
    for currentTransaction in transactions:
            for obj in objects:
                state = states[currentTransaction][obj]
                if state == 'sl' or state == 'xl':
                    manageLocksAndState('u', currentTransaction, obj, len(schedule))
    
    # get the final schedule with operation and locks/unlocks
    final_schedule = []
    for i in range(len(schedule)):
        final_schedule += locks[i] + [schedule[i]]
    final_schedule += locks[len(schedule)]
    final_schedule = formatSchedule(final_schedule)
    return final_schedule, is_strict, is_strong_strict

#  r1(A)r2(A)r3(B)w1(A)r2(C)r2(B)w2(B)w1(C) Not true if only exlusive lock, True if shared and exclusive locks
