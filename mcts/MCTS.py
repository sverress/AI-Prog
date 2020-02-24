import networkx as nx
import matplotlib.pyplot as plt


class MCTS:
    def __init__(self, state: [int]):
        self.G = nx.Graph()
        self.parent_node = Node(state)
        self.nodes = [self.parent_node]
        self.G.add_node(self.parent_node)

    def run(self):
        selected_node = self.select()
        self.explore(selected_node)
        self.simulate()
        self.backpropegate()
        return Node(self.parent_node).state

    def select(self):
        pass

    def explore(self):
        pass

    def simulate(self):
        pass

    def backpropegate(self):
        pass


class Node:
    def __init__(self, state: [int]):
        self.state = state

