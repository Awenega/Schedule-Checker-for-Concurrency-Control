from collections import defaultdict
from Actions import Action


rts = dict()
wts = dict()
wts_c = dict()
cb = dict()
timestamps = dict()
waiting = dict()
pending_action = []
rollback = dict()
write_on = dict()
last_write = dict()
RTS = 'RTS'
WTS = 'WTS'
WTS_C = 'WTS-C'
CB = 'CB'
deadlock = dict()


def SolveTimestamps(schedule):
    objects = []
    transactions = []
    pending_action = []
    for action in schedule:
        if action.object not in objects:
            rts[action.object] = 0
            wts[action.object] = 0
            wts_c[action.object] = 0
            cb[action.object] = True
            last_write[action.object] = None
            objects.append(action.object)
        if action.id_transaction not in transactions:
            waiting[action.id_transaction] = (False, None)
            rollback[action.id_transaction] = False
            write_on[action.id_transaction] = set()
            transactions.append(action.id_transaction)

    formatted_schedule = format_schedule(schedule)
    deadlock['end'] = False

    solution = 'The initial situation is:<br>'

    for object in rts:
        solution += "wts(" + str(object) + ")=" + "wts-c(" + str(object) + ")=" + \
            "rts(" + str(object) + ")=0 and cb(" + str(object) + ")=True<br>"

    solution += "<br>The system responds as follows:<br><ul class=\"list-group\">"

    clock_value = 1
    for action in formatted_schedule:
        isFirst = False
        if deadlock['end']:
            break
        elif waiting[action.id_transaction][0]:
            pending_action.append(action)
            solution += "<li class=\"list-group-item\">" + str(action) + " --> SKIP: because T" + \
                action.id_transaction + " is in WAITING state, skipped for now."
        elif rollback[action.id_transaction]:
            solution += "<li class=\"list-group-item\">" + str(action) + \
                " --> SKIP: because T" + action.id_transaction + " has done a rollback before."
        elif action.action_type == 'READ':
            if action.id_transaction not in timestamps:
                isFirst = True
                timestamps[action.id_transaction] = clock_value
            solution += read_action(action,
                                    action.id_transaction, action.object, isFirst)
        elif action.action_type == 'WRITE':
            if action.id_transaction not in timestamps:
                isFirst = True
                timestamps[action.id_transaction] = clock_value
            solution += write_action(action,
                                     action.id_transaction, action.object, isFirst)
        else:
            solution += commit_action(action.id_transaction)
        clock_value += 1

    solution += "</ul><br>"
    return solution


def read_action(action, transaction_id, object, isFirst):
    if timestamps[transaction_id] >= wts[object]:
        if cb[object] or timestamps[transaction_id] == wts[object]:
            rts[object] = max(timestamps[transaction_id], rts[object])
            action_solution = "<li class=\"list-group-item\">" + \
                str(action) + " --> ok --> "
            if isFirst:
                action_solution += "ts(T" + str(transaction_id) + ")=" + \
                    str(timestamps[transaction_id]) + ", "
            action_solution += "rts(" + str(object) + ")=" + str(rts[object])

        else:
            waiting[transaction_id] = (True, object)
            pending_action.append(action)
            if not waiting[last_write[object]][0]:
                action_solution = "<li class=\"list-group-item\">" + \
                    str(action) + " --> no: T" + \
                    str(transaction_id) + " must WAIT"
                if isFirst:
                    action_solution += " and ts(T" + str(transaction_id) + \
                        ")=" + str(timestamps[transaction_id])
            else:
                action_solution = "<li class=\"list-group-item\">" + \
                    str(action) + " --> no: T" + \
                    str(transaction_id) + " DEADLOCK"
                deadlock['end'] = True

    else:
        action_solution = rollback_action(action, transaction_id, isFirst)

    return action_solution


def write_action(action, transaction_id, object, isFirst):
    if timestamps[transaction_id] >= rts[object] and timestamps[transaction_id] >= wts[object]:
        if cb[object]:
            set_of_objects = write_on.get(transaction_id)
            set_of_objects.add(object)
            write_on[transaction_id] = set_of_objects

            wts[object] = timestamps[transaction_id]
            cb[object] = False
            last_write[action.object] = transaction_id

            action_solution = "<li class=\"list-group-item\">" + \
                str(action) + " --> ok --> "
            if isFirst:
                action_solution += "ts(T" + str(transaction_id) + ")=" + \
                    str(timestamps[transaction_id]) + ", "
            action_solution += "wts(" + str(object) + ")=" + \
                str(timestamps[transaction_id]) + \
                " and cb(" + str(object) + ")=False"

        else:
            waiting[transaction_id] = (True, object)
            pending_action.append(action)
            if not waiting[last_write[object]][0]:
                action_solution = "<li class=\"list-group-item\">" + \
                    str(action) + " --> no: T" + \
                    str(transaction_id) + " must WAIT"
                if isFirst:
                    action_solution += " and ts(T" + str(transaction_id) + \
                        ")=" + str(timestamps[transaction_id])
            else:
                action_solution = "<li class=\"list-group-item\">" + \
                    str(action) + " --> no: T" + \
                    str(transaction_id) + " DEADLOCK"
                deadlock['end'] = True

    else:
        if timestamps[transaction_id] >= rts[object] and timestamps[transaction_id] < wts[object]:
            if cb[object]:
                action_solution = "<li class=\"list-group-item\">" + str(action) + \
                    " --> SKIP: the action has been skipped for the THOMAS RULE"
                if isFirst:
                    action_solution += " and ts(T" + str(transaction_id) + \
                        ")=" + str(timestamps[transaction_id])

            else:
                waiting[transaction_id] = (True, object)
                pending_action.append(action)
                if not waiting[last_write[object]][0]:
                    action_solution = "<li class=\"list-group-item\">" + \
                        str(action) + " --> no: T" + \
                        str(transaction_id) + " must WAIT"
                    if isFirst:
                        action_solution += " and ts(T" + str(transaction_id) + \
                            ")=" + str(timestamps[transaction_id])
                else:
                    action_solution = "<li class=\"list-group-item\">" + \
                        str(action) + " --> no: T" + \
                        str(transaction_id) + " DEADLOCK"
                    deadlock['end'] = True

        else:
            action_solution = rollback_action(action, transaction_id, isFirst)
    return action_solution


def commit_action(transaction_id):
    set_of_objects = write_on.get(transaction_id)
    action_solution = "<li class=\"list-group-item\">" + \
        "c" + str(transaction_id) + " --> COMMIT: "
    for object in set_of_objects:
        action_solution += "cb(" + str(object) + ")=True, wts_c(" + \
            object + ")=" + str(timestamps[transaction_id]) + ", "
        cb[object] = True
        wts_c[object] = timestamps[transaction_id]
        for transaction in waiting:
            if waiting[transaction][0] and waiting[transaction][1] == object:
                waiting[transaction] = (False, None)
                action_solution += handle_pending_actions()

    return action_solution


def rollback_action(action, transaction_id, isFirst):
    set_of_objects = write_on.get(transaction_id)
    action_solution = "<li class=\"list-group-item\">" + str(action) + \
        " --> no: Rollback of T" + \
        str(transaction_id) + ", after the action set: "
    for object in set_of_objects:
        wts[object] = wts_c.get(object)
        cb[object] = True
        action_solution += "cb(" + str(object) + ")=True, wts(" + \
            object + ")=" + str(wts_c.get(object)) + ", "
        for transaction in waiting:
            if waiting[transaction][0] and waiting[transaction][1] == object:
                waiting[transaction] = (False, None)
                action_solution += handle_pending_actions()
    if isFirst:
        action_solution += " and ts(T" + str(transaction_id) + ")=" + \
            timestamps[transaction_id]

    rollback[transaction_id] = True
    return action_solution


def format_schedule(schedule):
    formatted_schedule = []
    commitedTransactions = set()
    for action in schedule:
        if action.action_type == 'COMMIT':
            commitedTransactions.add(action.id_transaction)

    for action in schedule:
        if action.isLastAction and not (action.id_transaction in commitedTransactions):
            formatted_schedule.append(action)
            current_action = 'COMMIT'
            ActionCurrent = Action(current_action, action.id_transaction, None)
            formatted_schedule.append(ActionCurrent)
        else:
            formatted_schedule.append(action)
    return formatted_schedule


def handle_pending_actions():
    actions_solution = ""
    for action in pending_action:
        isFirst = False
        if deadlock['end']:
            break
        elif waiting[action.id_transaction][0]:
            continue
        elif rollback[action.id_transaction]:
            actions_solution += "<li class=\"list-group-item\">" + str(action) + \
                " --> SKIP: because T" + action.id_transaction + " has done a rollback before."
        elif action.action_type == 'READ':
            actions_solution += read_action(action,
                                            action.id_transaction, action.object, isFirst)
        elif action.action_type == 'WRITE':
            actions_solution += write_action(action,
                                             action.id_transaction, action.object, isFirst)
        else:
            actions_solution += commit_action(action.id_transaction)
    return actions_solution

# r1(A)w2(A)c2r3(B)w3(A)w1(A)c3r1(B) HANDLE WAITING and THOMAS RULE
# r1(B)w1(A)w2(B)w1(B)r2(A) DEADLOCK
# r1(A)r2(B)r3(A)r2(A)w1(A)w3(A)
