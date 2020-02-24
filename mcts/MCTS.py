import networkx as nx
from mcts.StateManager import StateManager
import matplotlib.pyplot as plt
from typing import Type


class MCTS:
    def __init__(self, state: [int], state_manager: Type[StateManager]):
        self.G = nx.DiGraph()
        self.root_state = state
        self.add_node(state)
        self.c = 1
        self.state_manager = state_manager

    def add_node(self, state: [int]):
        self.G.add_node(str(state), state=state, times_encountered=0)

    def add_edge(self, parent_state, child_state, sap_value, times_encountered):
        self.G.add_edge(str(parent_state), str(child_state), sap_value = sap_value, times_encountered = times_encountered)

    def print_graph(self):
        nx.draw(self.G)
        plt.show()

    def run(self):
        self.select()
        self.expand()
        self.simulate()
        self.backpropegate()

    def get_node(self, state: [int]):
        return dict(self.G.nodes()).get(str(state))

    def select(self):
        pass

    def expand(self):
        for child_state in self.state_manager.generate_child_states(self.root_state):
            self.add_node(child_state)
            self.add_edge(self.root_state, child_state)

    def explore(self):
        for child_state in self.state_manager.generate_child_states(self.root_state):
            self.add_node(child_state)
            self.add_edge(self.root_state, child_state)

    def simulate(self, state: [int]):
        path = self.sim_tree(state)

    def sim_tree(self, state: [int]):
        while not self.state_manager.is_end_state(state):
            if

    def backpropegate(self):
        pass


