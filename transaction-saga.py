# saga transaction library
# Created By: Shubham Arora

# transaction api
# txn.start()
# txn.add( method, args, rollback_method, args )


class Transaction:
    # a Transaction class contains method references and arguments for that method
    # it is responsible for calling methods
    #

    def __init__(self, method_ref, method_args):
        # self.id = -1
        self.method_ref = method_ref
        self.method_args = method_args

    def run(self):
        if self.method_ref is not None:
            self.method_ref(self.method_args)
        else:
            print("empty method ref, txn not run")


class Log:
    def __init__(self, id):
        self.id = 0


class Saga:
    # a Saga class defines and coordinates transactions
    # it is responsible for commit and or rollback of transactions

    def __init__(self):
        self.log = []
        self.execution_graph_head = None
        self.execution_graph_tail = None
        self.current_transaction_id = 0

    def start(self):
        self.execution_graph_head = self.Graph(None, None, id=self.current_transaction_id, name="default_start")
        self.execution_graph_tail = self.execution_graph_head
        self.current_transaction_id += 1
        print("txn started")

    def commit(self):
        # does not increase self.curent_current_transaction_id

        self.execution_graph_tail.next = self.Graph(None, None, id=self.current_transaction_id, name="default_end")
        self.execution_graph_tail = self.execution_graph_tail.next
        head = self.execution_graph_head
        while head is not None:
            # add to log
            head.run_action_method()
            head = head.next

        print("txn committed")

    def add(self, action_transaction: Transaction, rollback_transaction: Transaction, **kwargs):
        head = self.execution_graph_head
        kwargs['id'] = self.current_transaction_id
        self.current_transaction_id += 1
        # print(f"add func kwargs: {kwargs}")
        self.execution_graph_tail.next = self.Graph(action_transaction, rollback_transaction, **kwargs)
        self.execution_graph_tail = self.execution_graph_tail.next

    def print_graph(self):
        head = self.execution_graph_head
        while head.next is not None:
            print(f"id: {head.id}, {head.name} --> ", end=" ")
            head = head.next
        print(f"id: {head.id}, {head.name}")

    class Graph:
        # a node in graph is a tuple of
        # action_transaction AND rollback_transaction
        # currently, assume each node has only one next node, i.e. it is a directed chain

        def __init__(self, action_transaction: Transaction, rollback_transaction: Transaction, **kwargs):
            self.action_transaction = action_transaction
            self.rollback_transaction = rollback_transaction
            # print(f"graph kwargs: {kwargs}")
            self.id = kwargs.get('id')

            if kwargs.get('name'):
                self.name = kwargs['name']
            else:
                self.name = "default"
            self.next = None

        def run_action_method(self):
            if self.action_transaction is not None:
                self.action_transaction.run()

        def run_rollback_method(self):
            if self.rollback_transaction is not None:
                self.rollback_transaction.run()


class Game:
    def __init__(self):
        self.val = 0

    def add(self, n: int) -> bool:
        if self.val != -1:
            self.val += n
            return True
        else:
            return False

    # the response of a method call, can be anything,
    # a simple true false indicating whether the Api call succeeded or not
    # in the wild, an API call can receive an error response,
    # which might be a string, depending on the use case
    # we assume such an API call is wrapped by a func that returns a simple true, false for success, failure

    def sub(self, n: int):
        self.val -= n

    def add_two(self, a, b):
        self.val = a + b

    def print_val(self):
        print(f"game val: {self.val}")


if __name__ == "__main__":
    game1 = Game()
    game2 = Game()
    game2.sub(1)
    print("game 1: ", end="")
    game1.print_val()
    print("game 2: ", end="")
    game2.print_val()

    saga = Saga()
    saga.start()

    txn1 = Transaction(game1.add, 4)
    rollback_txn1 = Transaction(game1.sub, 4)
    txn2, rollback_txn2 = Transaction(game2.add, 5), Transaction(game2.sub, 5)
    saga.add(txn1, rollback_txn1, name="txn1")
    saga.add(txn2, rollback_txn2, name="txn2")

    saga.print_graph()
    saga.commit()
    saga.print_graph()

    print("game 1: ", end="")
    game1.print_val()
    print("game 2: ", end="")
    game2.print_val()
