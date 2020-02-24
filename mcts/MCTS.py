import networkx as nx
from mcts.StateManager import StateManager
import matplotlib.pyplot as plt
from typing import Type
import random

class MCTS:
    def __init__(self, state: [int], state_manager: Type[StateManager]):
        self.G = nx.DiGraph()
        self.root_state = state
        self.add_node(state)
        self.c = 1
        self.state_manager = state_manager

    def add_node(self, state: [int]):
        self.G.add_node(self.state_manager.state_to_string(state), state=state, times_encountered=0)

    def add_edge(self, parent_state, child_state):
        self.G.add_edge(self.state_manager.state_to_string(parent_state), self.state_manager.state_to_string(child_state), sap_value=0, times_encountered=0)

    def get_node(self, state: [int]):
        return dict(self.G.nodes()).get(self.state_manager.state_to_string(state))

    def print_graph(self):
        nx.draw(self.G, with_labels=True)
        plt.show()

    def run(self):
        for i in range(1):  # 1 iteration
            state = self.select(self.root_state)
            simualtion_result = self.simulate(state)
            self.backpropagate(state, simualtion_result)
        return self.best_child_node(self.root_state)

    def select(self, state: [int]):
        # while fully_expanded
        possible_child_states = self.state_manager.generate_child_states(state)
        visited_child_states = list(self.G.predecessors(str(state)))
        while len(possible_child_states) == len(visited_child_states):
            # Get the best child node from the current node
            state = self.best_child_node(state)
            possible_child_states = self.state_manager.generate_child_states(state)
            visited_child_states = list(self.G.predecessors(str(state)))
        unvisited =
        return

    def best_child_node(self, state):
        hello = [predecessor for predecessor in self.G.predecessors(str(state))]
        return state

    def expand(self, state: ([int], bool)):
        for child_state in self.state_manager.generate_child_states(state):
            self.add_node(child_state)
            self.add_edge(state, child_state)

    def simulate(self, state: ([int], bool)):
        while non_terminal(node):
            node = rollout_policy(node)
        return result(node)


    def backpropagate(self):
        if is_root(node):
            return
        node.stats = update_stats(node, result)
        backpropagate(node.parent)

    def sim_tree(self, state: [int]):
        path = [state]
        while not self.state_manager.is_end_state(state):
            if not bool(self.get_node(state)):  # If state not in tree
                self.add_node(state)
                self.add_edge()