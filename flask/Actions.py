class Action:
    def __init__(self, action_type, id_transaction, object):
        if action_type is None or id_transaction is None or (action_type != "COMMIT" and object is None):
            raise ValueError(
                'Must exist an operation type, id transaction and an object')

        self.action_type = str(action_type)
        self.id_transaction = str(id_transaction)
        self.object = str(object)
        self.isLastAction = False

    def __str__(self):
        if self.action_type == 'READ':
            operationType = 'r'
        elif self.action_type == 'WRITE':
            operationType = 'w'
        elif self.action_type == 'UNLOCKED' or self.action_type =='u':
            operationType = 'u'
        elif self.action_type == 'SHARED_LOCK' or self.action_type =='sl':
            operationType = 'sl'
        elif self.action_type == 'EXCLUSIVE_LOCK' or self.action_type =='xl':
            operationType = 'xl'
        elif self.action_type == 'COMMIT':
            operationType = 'c'
        else:
            print('WARNING: action type not recognized for this Action')
            operationType = self.action_type
        return operationType + self.id_transaction + '(' + self.object + ')'

    def __repr__(self):
        return self.__str__()
