# saga transaction library
# Created By: Shubham Arora

# transaction api
# txn.start()
# txn.add( method, args, rollback_method, args )


class Transaction:
    def __init__(self):
        self.log = []
        self.execution_graph_head = self.Graph(None, None, None, None)

    def start(self):
        print("txn started")

    def commit(self):
        head = self.execution_graph_head
        while head is not None:
            head.run_action_method()
            head = head.next

        print("txn committed")

    def add(self, action_method_ref, action_method_args, rollback_method_ref, rollback_method_args):
        head = self.execution_graph_head
        while head.next is not None:
            head = head.next
        head.next = self.Graph(action_method_ref, action_method_args, rollback_method_ref, rollback_method_args)
        # print(f"head: {head}, head next: {head.next}")
        # print(f"global head: {self.execution_graph_head}, head next: {self.execution_graph_head.next}")
        self.print_graph()

    def print_graph(self):
        head = self.execution_graph_head
        i = 0
        while head is not None:
            print(f"pos i: {i}, node: {head}")
            head = head.next
            i += 1

    class Graph:
        def __init__(self, action_method_ref, action_method_args, rollback_method_ref, rollback_method_args):
            self.action_method_ref = action_method_ref
            self.action_method_args = action_method_args
            self.rollback_method_ref = rollback_method_ref
            self.rollback_method_args = rollback_method_args
            self.next = None

        def run_action_method(self):
            if self.action_method_ref is not None:
                self.action_method_ref(self.action_method_args)

        def run_rollback_method(self):
            if self.rollback_method_ref is not None:
                self.rollback_method_ref(self.rollback_method_args)


class Game:
    def __init__(self):
        self.val = 0

    def add(self, n):
        self.val += n

    def sub(self, n):
        self.val -= n

    def add_two(self, a, b):
        self.val = a + b

    def print_val(self):
        print(f"game val: {self.val}")


if __name__ == "__main__":
    txn = Transaction()
    game = Game()
    txn.start()
    txn.add(game.add, 4, game.sub, 3)
    txn.print_graph()
    txn.commit()
    game.print_val()
