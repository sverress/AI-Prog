import networkx as nx
from mcts.StateManager import StateManager
import matplotlib.pyplot as plt


class MCTS:
    def __init__(self, state: [int], state_manager: StateManager):
        self.G = nx.DiGraph()
        self.root_state = state
        self.add_node(state)
        self.c = 1
        self.state_manager = state_manager

    def add_node(self, state: [int]):
        self.G.add_node(str(state), state=state, times_encountered=0)

    def add_edge(self, parent_state, child_state):
        self.G.add_edge(str(parent_state), str(child_state))

    def run(self):
        self.select()
        self.explore()
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

    def simulate(self):
        pass

    def backpropegate(self):
        pass


