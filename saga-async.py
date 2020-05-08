# saga transaction library
# Created By: Shubham Arora

"""
transaction api

saga = Saga()
saga.start()

txn1, rollback_txn1 = Transaction(action_method, action_method_arg), Transaction(rollback_method, rollback_method_arg)
txn2, rollback_txn2 = Transaction(action_method, action_method_arg), Transaction(rollback_method, rollback_method_arg)
saga.add(txn1, rollback_txn1, name="txn1")
saga.add(txn2, rollback_txn2, name="txn2")

saga.commit()
"""

import logging
import sys
import time

import ray


class Transaction:
    """
    transaction class
    a Transaction class contains method references and arguments for that method
    it is responsible for calling methods, with supplied args
    """

    def __init__(self, method_ref, method_args):
        # self.id = -1
        self.method_ref = method_ref
        self.method_args = method_args

    # the response of a method call, can be anything,
    # a simple true false indicating whether the Api call succeeded or not
    # in the wild, an API call can receive an error response,
    # which might be a string, depending on the use case
    # we assume such an API call is wrapped by a func that returns a simple true, false for success, failure
    # TODO: find a way to pass this response to users defined rollback func
    #     save it in saga log?

    def run(self) -> bool:
        is_success = True
        if self.method_ref is not None:
            is_success = ray.get(self.method_ref.remote(self.method_args))
            # print(f"txn run result: {is_success}")
        else:
            print("empty method ref, txn not run")

        return is_success


# constants
COMMAND_START = 1
COMMAND_END = 2
COMMAND_ABORT = 3

ROLLBACK_START = 4
ROLLBACK_END = 5
ROLLBACK_ABORT = 6


# STATUS_SUCCESS = 4
# STATUS_FAIL = 5


class Log:
    """
    the saga Log
    supports methods to:
     - add entries to log
     - query log
     - debug print log
     - clear log

    """

    def __init__(self):
        self.entries = []
        self.count = 0

    def add_entry(self, action_id: int, action_name: str, action_command_type: str):
        entry = {
            "id": action_id,
            "name": action_name,
            "command": action_command_type
        }
        self.entries.append(entry)
        self.count += 1

    def print(self):
        i = 0
        while i < self.count - 1:
            print(f"{self.entries[i]} -> ", end=" ")
            i += 1
        print(f"{self.entries[i]}")

    def query(self, action_id: int) -> []:
        all_entries_for_action = []
        for entry in self.entries:
            if entry["id"] == action_id:
                all_entries_for_action.append(entry)
        return all_entries_for_action

    def clear(self):
        self.entries.clear()


@ray.remote
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
        self.current_transaction_id = 1
        self.log.clear()
        # print("txn started")

    def commit(self):
        # does not increase self.current_current_transaction_id

        self.execution_graph_tail.next = self.Graph(None, None, id=self.current_transaction_id, name="saga_end")
        self.execution_graph_tail = self.execution_graph_tail.next
        head = self.execution_graph_head
        failure = False
        while head is not None:
            # add to log
            # self.log.add(head.name + "-start")
            self.log.add_entry(head.id, head.name, COMMAND_START)

            # is_success_handle = head.run_action_method()
            is_success = head.run_action_method()
            # print(f"received result is: {is_success}")
            # print(f"received result type is: {type(is_success)}")
            # print(f"received result get is: {ray.get(is_success)}")
            # if is_success_handle == False:
            #     is_success = False
            # else:
            #     is_success = ray.get(is_success_handle)

            if is_success:
                # print(f"true returned by: {head.name}\n")
                logging.debug(f"false returned by: {head.name}\n")
                self.log.add_entry(head.id, head.name, COMMAND_END)
            else:
                # print(f"false returned by: {head.name}\n")
                logging.debug(f"false returned by: {head.name}\n")
                self.log.add_entry(head.id, head.name, COMMAND_ABORT)
                failure = True
                break
            head = head.next
        if failure:
            self.rollback()
            return

        # self.log.print()
        # print("txn committed")

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
        head = cur_node
        # print("rollback start")
        while head is not None:
            # query if the action has been done, what all command are complete for the txn
            # if aborted, do nothing
            # if started, and ended, abort
            # else, do nothing
            # currently, the code assumes synchronous functioning
            # i.e. all commands return immediately
            # TODO: extend for possible async execution

            command_entries = self.log.query(head.id)
            is_started, is_ended, is_aborted = False, False, False
            for entry in command_entries:
                if entry['command'] == COMMAND_START:
                    is_started = True
                if entry['command'] == COMMAND_ABORT:
                    is_aborted = True
                if entry['command'] == COMMAND_END:
                    is_ended = True

            # print(f"log parse complete for node id: {head.id}")

            if is_aborted:
                # this command was already aborted, do nothing
                pass
            elif is_started and is_ended:
                self.log.add_entry(head.id, head.name, ROLLBACK_START)
                is_success = head.run_rollback_method()
                if is_success:
                    self.log.add_entry(head.id, head.name, ROLLBACK_END)
                else:
                    self.log.add_entry(head.id, head.name, ROLLBACK_ABORT)

            head = head.next
        # self.log.print()
        # print("rollback complete")

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
        """
        a node in graph is a tuple of
        action_transaction AND rollback_transaction
        currently, assume each node has only one next node, i.e. it is a directed chain
        """

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
            is_success = True
            if self.action_transaction is not None:
                is_success = self.action_transaction.run()
                # print(f"action run result: {is_success}")

            return is_success

        def run_rollback_method(self):
            is_success = True
            if self.rollback_transaction is not None:
                is_success = self.rollback_transaction.run()
            return is_success


@ray.remote
class Game:
    def __init__(self):
        self.val = 0

    def add(self, n: int) -> bool:
        # print(f"add called with values: {n}, val: {self.val}")
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
        return True

    def add_two(self, a, b):
        self.val = a + b

    def print_val(self):
        print(f"val: {self.val}")

    def get_val(self):
        return self.val

    def set_val(self, n: int):
        self.val += n


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    ray.init()

    game1 = Game.remote()
    game2 = Game.remote()
    game3 = Game.remote()
    # uncomment the below line to create rollback
    # ray.get(game2.sub.remote(1))
    print(f"game 1: {ray.get(game1.get_val.remote())}")
    print(f"game 2: {ray.get(game2.get_val.remote())}")
    print(f"game 3: {ray.get(game3.get_val.remote())}")

    saga = Saga.remote()
    timings = []
    totalTime = 0
    # print("txn, time(s)")
    timings.append("txn, time(s), txnPerSec")
    for i in range(1, 20):
        totalTime = 0
        for j in range(i*100):
            startTime = time.perf_counter()
            # saga = Saga.remote()
            saga.start.remote()

            txn1, rollback_txn1 = Transaction(game1.add, 4), Transaction(game1.sub, 4)
            txn2, rollback_txn2 = Transaction(game2.add, 5), Transaction(game2.sub, 5)
            txn3, rollback_txn3 = Transaction(game3.sub, 10), Transaction(game3.add, 10)
            saga.add.remote(txn1, rollback_txn1, name="txn1")
            saga.add.remote(txn2, rollback_txn2, name="txn2")
            saga.add.remote(txn3, rollback_txn3, name="txn3")

            # saga.print_graph()
            ray.get(saga.commit.remote())
            endTime = time.perf_counter()
            # print(f"time elapsed: {endTime - startTime:0.4f} sec")
            timeElapsed = endTime - startTime
            # print(f"{i}, {timeElapsed:0.4f}")
            totalTime += timeElapsed
            # del saga
        # print(f"{i*10}, {totalTime:0.4f}")
        txn_per_sec = i*100 / totalTime
        timings.append(f"{i*100}, {totalTime:0.4f}, {txn_per_sec:0.4f}")

    # saga.print_graph.remote()
    print(f"game 1: {ray.get(game1.get_val.remote())}")
    print(f"game 2: {ray.get(game2.get_val.remote())}")
    print(f"game 3: {ray.get(game3.get_val.remote())}")

    print(timings)
