import networkx as nx
import matplotlib.pyplot as plt


class MCTS:
    def __init__(self, state: [int]):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        G.add_node(3)
        G.add_edge(1, 2)
        nx.draw(G)
        plt.show()


class Node:
    def __init__(self, state:[int]):
        self.state = state

