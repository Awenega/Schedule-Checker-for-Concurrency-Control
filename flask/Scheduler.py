from Actions import Action


def parseTheSchedule(schedule):

    scheduleFormatted = []
    currentId = 0
    lastAction = dict()
    number_of_actions = len(schedule)
    isTerminated = dict()
    transaction_ids = dict()

    try:
        while currentId < number_of_actions:
            action = None
            id_transaction = None
            object = None

            if schedule[currentId] == 'r':
                action = 'READ'
            elif schedule[currentId] == 'w':
                action = 'WRITE'
            elif schedule[currentId] == 'c':
                action = 'COMMIT'

                currentId += 1
                if currentId == number_of_actions:
                    return scheduleMalformed('Missing transaction ID after COMMIT')

                id_transactionCommited = schedule[currentId]

                if not (id_transactionCommited in transaction_ids):
                    return scheduleMalformed('Must COMMIT an existing transaction')

                isTerminated[id_transactionCommited] = True
                ActionCurrent = Action(action, id_transactionCommited, None)

                scheduleFormatted.append(ActionCurrent)
                currentId += 1
                continue
            else:
                return scheduleMalformed('Current action types must be \'<b>r</b>\' (READ), \'<b>w</b>\' (WRITE) or \'<b>c</b>\' (COMMIT)')
            currentId += 1

            id_transactionEnd = schedule[currentId:].find('(')
            id_transaction = schedule[currentId:currentId+id_transactionEnd]
            if id_transaction == '':
                return scheduleMalformed()
            elif id_transaction in isTerminated:
                return scheduleMalformed("Can not add actions after COMMIT")
            transaction_ids[id_transaction] = True
            currentId = currentId+id_transactionEnd+1

            objectEnd = schedule[currentId:].find(')')
            object = schedule[currentId:currentId+objectEnd]
            if object == '':
                return scheduleMalformed()
            currentId = currentId+objectEnd+1

            ActionCurrent = Action(action, id_transaction, object)

            lastAction[id_transaction] = ActionCurrent
            scheduleFormatted.append(ActionCurrent)

        for action in lastAction.values():
            action.isLastAction = True

        return scheduleFormatted

    except ValueError:
        return scheduleMalformed()


def formatSchedule(schedule):
    scheduleFormatted = ''
    for action in schedule:
        if action.action_type != 'READ' and action.action_type != 'WRITE' and action.action_type != 'COMMIT':
            scheduleFormatted += '<b>' + str(action) + ' </b>'
        else:
            scheduleFormatted += str(action)+' '
    return scheduleFormatted+'\n'


def scheduleMalformed(message=None):
    message = message if message else 'The given schedule is malformed!'
    hintMessage = "<br><br>Enter a schedule that is formatted like <b>w1(A)r1(B)r3(C)c3r1(A)c1</b>"
    return message + hintMessage
