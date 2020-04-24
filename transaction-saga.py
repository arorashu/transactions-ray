# saga transaction library
# Created By: Shubham Arora

# transaction api
# txn.start()
# txn.add( method, args, rollback_method, args )


class Transaction:
    """
    trans class
    """

    # a Transaction class contains method references and arguments for that method
    # it is responsible for calling methods
    #

    def __init__(self, method_ref, method_args):
        # self.id = -1
        self.method_ref = method_ref
        self.method_args = method_args

    def run(self) -> bool:
        is_success = True
        if self.method_ref is not None:
            is_success = self.method_ref(self.method_args)
        else:
            print("empty method ref, txn not run")

        return is_success


class Log:
    def __init__(self):
        self.entries = []
        self.count = 0

    def add(self, desc: str):
        self.entries.append(desc)
        self.count += 1

    def print(self):
        i = 0
        while i < self.count - 1:
            print(f"{self.entries[i]} -> ", end=" ")
            i += 1
        print(f"{self.entries[i]}")

    def query(self, keyword: str):
        pass


class Saga:
    """
    a Saga class defines and coordinates transactions
    it is responsible for commit and or rollback of transactions
    """

    def __init__(self):
        self.log = Log()
        self.execution_graph_head = None
        self.execution_graph_tail = None
        self.current_transaction_id = 0
        self.reverse_graph_head = None

    def start(self):
        self.execution_graph_head = self.Graph(None, None, id=self.current_transaction_id, name="saga_start")
        self.execution_graph_tail = self.execution_graph_head
        self.current_transaction_id += 1
        print("txn started")

    def commit(self):
        # does not increase self.current_current_transaction_id

        self.execution_graph_tail.next = self.Graph(None, None, id=self.current_transaction_id, name="saga_end")
        self.execution_graph_tail = self.execution_graph_tail.next
        head = self.execution_graph_head
        failure = False
        while head is not None:
            # add to log
            self.log.add(head.name + "-start")
            is_success = head.run_action_method()
            if is_success:
                self.log.add(head.name + "-success")
            else:
                self.log.add(head.name + "-fail")
                failure = True
                break
            head = head.next
        if failure:
            self.rollback()
            return

        self.log.print()
        print("txn committed")

    def rollback(self):
        """
        reverse the saga DAG and run the new DAG
        :return:
        """

        prev_node = None
        cur_node = self.execution_graph_head
        while cur_node.next is not None:
            next_node = cur_node.next
            cur_node.next = prev_node
            prev_node = cur_node
            cur_node = next_node
        cur_node.next = prev_node

        self.reverse_graph_head = cur_node
        # self.reverse_graph_head.print_graph()
        head = cur_node
        self.log.add("rollback-start")
        while head is not None:
            self.log.add(head.name + "rollback-start")
            is_success = head.run_rollback_method()
            if is_success:
                self.log.add(head.name + "-rollback-success")
            else:
                self.log.add(head.name + "-rollback-fail")
            head = head.next
        self.log.add("rollback-end")
        self.log.print()
        print("rollback complete")

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

        def run_action_method(self) -> bool:
            is_success = True
            if self.action_transaction is not None:
                is_success = self.action_transaction.run()
            return is_success

        def run_rollback_method(self):
            is_success = True
            if self.rollback_transaction is not None:
                is_success = self.rollback_transaction.run()
            return is_success


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

    txn1, rollback_txn1 = Transaction(game1.add, 4), Transaction(game1.sub, 4)
    txn2, rollback_txn2 = Transaction(game2.add, 5), Transaction(game2.sub, 5)
    saga.add(txn1, rollback_txn1, name="txn1")
    saga.add(txn2, rollback_txn2, name="txn2")

    # saga.print_graph()
    saga.commit()
    saga.print_graph()

    print("game 1: ", end="")
    game1.print_val()
    print("game 2: ", end="")
    game2.print_val()
