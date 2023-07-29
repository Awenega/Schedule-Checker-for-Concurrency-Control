class Operation:
    """
    Class describing an operation of the schedule
    """

    def __init__(self, operation_type, id_transaction, object):
        if operation_type is None or id_transaction is None or object is None:
            raise ValueError

        # can be either READ, WRITE, UNLOCKED, SHARED_L, XCLUSIVE_L
        self.operation_type = str(operation_type)
        # identifier of the id_transactionaction executing this operation
        self.id_transaction = str(id_transaction)
        # objectect on which this operation is executed
        self.object = str(object)

        # Boolean telling if this operation is the last performed by id_transactionaction 'id_transaction'
        # It is False if it is the last one, True otherwise. It will be set accordingly by 'parse_schedule'
        self.tx_continues = True

    def __str__(self):
        if self.operation_type == 'READ':
            s = 'r'
        elif self.operation_type == 'WRITE':
            s = 'w'
        elif self.operation_type == 'UNLOCKED':
            s = 'u'
        elif self.operation_type == 'SHARED_L':
            s = 'sl'
        elif self.operation_type == 'XCLUSIVE_L':
            s = 'xl'
        else:
            print('WARNING: op operation_type not recognized')
            s = self.operation_type
        return s+self.id_transaction+'('+self.object+')'

    def __repr__(self):  # debugging
        return self.__str__()
