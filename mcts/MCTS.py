import networkx as nx
import matplotlib.pyplot as plt


class MCTS:
    def __init__(self, state: [int]):
        self.G = nx.DiGraph()
        self.G.add_node(str(state), state=state, times_encountered=0)

    def run(self):
        self.select()
        self.explore()
        self.simulate()
        self.backpropegate()

    def get_node(self, state: [int]):
        return dict(self.G.nodes()).get(str(state))

    def select(self):
        pass

    def explore(self):
        pass

    def simulate(self):
        pass

    def backpropegate(self):
        pass


