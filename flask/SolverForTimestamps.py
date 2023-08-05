
from collections import defaultdict
from Scheduler import parse_schedule, _sched_malformed_err


from os.path import isfile
DEBUG = isfile('.DEBUG')


def debug(*args):
    msg = ''
    for arg in args:
        msg += str(arg)+' '
    if DEBUG:
        print(msg)


# WORK IN PROGRESS


def solveTimestamps(schedule):
    """
    Returns true of false whether the schedule is serializable through timestamps
    """

    # timestamps information for each object
    # indices of the dummy_entry array where the timestamp information is stored
    RTS, WTS, WTS_C, CB = 'RTS', 'WTS', 'WTS_C', 'CB'
    # dummy entry, all entries initialized like this
    dummy_entry = {RTS: -1, WTS: -1, WTS_C: -1, CB: 1}
    timestamps_data = {op.object: dummy_entry.copy() for op in schedule}

    # save objects written by each transaction
    # dict[transaction] = written objects by transaction
    written_obj = defaultdict(set)

    # Set of waiting transactions
    # if 'T' is a waiting transaction, then waiting_tx['T'] is the index of the Actions of 'T' in the schedule where 'T' is blocked
    waiting_tx = dict()

    # final solution. Its entries are lists
    solution = list()
    solution_entry = list()

    # - - - - Scheduler - - -

    def commit(tx):
        """Performs the commit of transaction 'tx'
        """
        solution_entry.append('commit')
        debug('committing', tx)
        for obj in written_obj[tx]:
            data = timestamps_data[obj]
            set_timestamp_data(obj, WTS_C, data[WTS])
            set_timestamp_data(obj, CB, True)

    def rollback(tx):
        """Performs the rollback of transaction 'tx'
        """
        solution_entry.append('rollback')
        debug('rollbacking', tx)
        for obj in written_obj[tx]:
            data = timestamps_data[obj]
            set_timestamp_data(obj, WTS, data[WTS_C])
            set_timestamp_data(obj, CB, True)

    def execute(op):
        """Execute Actions op. Write in the solution its execution and,
        whether it is the last, the commit of its transaction
        """
        if op.action_type == 'WRITE':
            written_obj[op.id_transaction].add(op.object)
        if not Actions.isLastAction:
            commit(Actions.id_transaction)

    def set_timestamp_data(obj, key, value):
        if key != CB and key != WTS and key != WTS_C and key != RTS:
            raise ValueError
        timestamps_data[obj][key] = value
        solution_entry.append(f'{key}({str(obj)})={value}')

    def TS(tx):
        """Returns the timestamp of a transaction.
        we ASSUME that timestamp of transaction 'i' is 'i'
        """
        return int(tx)

    # sanity check on the timestamps
    try:
        err = None
        all_timestamps = [TS(op.action_type) for op in schedule]
        negative_ts = filter(lambda x: x < 0, all_timestamps)
        if len(list(negative_ts)) > 0:
            err = _sched_malformed_err(
                'Transactions (their timestamps) must be non negative')
    except ValueError:
        err = _sched_malformed_err(
            'Transactions (their timestamps) must be integers')
    finally:
        if err:
            return {'err': err}

    # - - - - main - - -

    i = 0
    while True:

        debug('\nNEW STEP')

        # Fetch new Actions

        # First try to fetch the next Actions if a transaction has been unlocked
        locking_ops_index = sorted(waiting_tx.values())
        for i_lock in locking_ops_index:
            obj = schedule[i_lock].object
            # if the commit bit of an object, waited by some transaction, becomes true then fetch the Actions
            if timestamps_data[obj][CB] == True:
                Actions = schedule[i_lock]
                waiting_tx.pop(Actions.id_transaction)
                solution_entry.append(
                    f'resume {str(Actions.id_transaction)}')
                break

        else:  # no waiting Actions, go on with the schedule
            if i >= len(schedule):
                # If here, there are no waiting Actions and the schedule is empty, can return solution
                # return solution
                return {'err': None, 'sol': format_solution(solution), 'waiting_tx': waiting_tx}

            Actions = schedule[i]
            debug('Picked Actions from schedule', Actions)
            # Check if transaction of the Actions is in wait, if so skip it
            tx = Actions.id_transaction
            if tx in waiting_tx:
                debug('Transaction is in waiting', Actions)
                i += 1
                continue

        # Now we have fetched the next Actions, execute it
        debug('executing Actions', Actions)

        # New entry that will be populated and pushed into the solution
        solution_entry.append(str(Actions))

        transaction = Actions.id_transaction
        obj = Actions.object
        ts_obj = timestamps_data[obj]

        if Actions.id_transaction == 'READ':
            if TS(transaction) >= ts_obj[WTS]:
                if ts_obj[CB] or TS(transaction) == ts_obj[WTS]:
                    set_timestamp_data(obj, RTS, max(
                        TS(transaction), ts_obj[RTS]))
                    execute(Actions)
                else:
                    debug('put Actions in wait', Actions)
                    waiting_tx[transaction] = i
                    solution_entry.append('Wait')
            else:
                rollback(transaction)

        elif Actions.id_transaction == 'WRITE':
            if TS(transaction) >= ts_obj[RTS] and TS(transaction) >= ts_obj[WTS]:
                if ts_obj[CB]:
                    set_timestamp_data(obj, WTS, TS(transaction))
                    set_timestamp_data(obj, CB, False)
                    execute(Actions)
                else:
                    debug('put Actions in wait', Actions)
                    waiting_tx[transaction] = i
                    solution_entry.append('Wait')
            else:
                if TS(transaction) >= ts_obj[RTS] and TS(transaction) < ts_obj[WTS]:
                    if ts_obj[CB]:
                        solution_entry.append('Ignored (Thomas rule)')
                    else:
                        debug('put Actions in wait', Actions)
                        waiting_tx[transaction] = i
                        solution_entry.append('Wait')
                else:
                    rollback(transaction)

        else:
            raise ValueError('Bad Actions type')

        i += 1  # update schedule index
        # append data to solution
        solution.append(solution_entry.copy())
        solution_entry.clear()


def format_solution(sol):
    # s = '<table><tr><th><b>Action</b></th><th><b>Action</b></th></tr>'
    s = '<table>'
    for action in sol:
        s += f'<tr><td>{action[0]}</td><td>'  # action[0] is the Actions
        for op in action[1:]:
            s += op + ' '
        s += '</td></tr>'
    return s + '</table>'


if __name__ == '__main__':
    schedule = parse_schedule('w1(x)r2(x)w1(y)')
    # schedule = parse_schedule('')
    solution = solveTimestamps(schedule)
    from pprint import pprint
    pprint(solution)
