import networkx as nx
from hex.StateManager import StateManager
import matplotlib.pyplot as plt
import random
import math


class MCTS:
    def __init__(self, state_manager: StateManager, max_tree_height=5, c=1):
        self.state_manager = state_manager
        self.G = nx.DiGraph()
        self.root_state = self.state_manager.get_state()
        self.add_node(self.root_state, end_state = self.state_manager.is_end_state())
        self.c = c
        self.max_tree_height = max_tree_height

    # MCTS METHODS

    def run(self, m: int):
        """
        Runs the monte carlo tree search algorithm, tree traversal -> rollout -> backprop, m times. Then finds the greedy
            best move from root state of the current tree
        :param m: int
        :return: the greedy best move from root node of the current tree
        """
        for i in range(m):
            self.traverse_tree(self.root_state, depth=0)
            self.state_manager.reset_state_manager(self.root_state)
        return self.greedy_best_child(self.root_state)

    def traverse_tree(self, state: str, depth):
        if depth == self.max_tree_height or self.is_end_state(state):
            self.simulate(state)
            return
        out_edgs = list(self.G.out_edges(state, data=True))
        if not out_edgs:
            self.expand(state)
            return
        unvisited_out_edgs = list(filter(lambda x: x[2]['n'] == 0, out_edgs))
        if unvisited_out_edgs:
            child = random.choice(unvisited_out_edgs)[1]
            self.state_manager.update_state_manager(child)
            self.G.nodes[child]['end_state'] = self.state_manager.is_end_state()
            self.G.get_edge_data(state, child)['flag'] = 1
            self.simulate(child)
            return
        child = self.best_child_uct(state, out_edgs)
        self.state_manager.update_state_manager(child)
        self.traverse_tree(child, depth + 1)

    def expand(self, state):
        children = self.state_manager.generate_child_states(state)
        for child in children:
            # Could this cause some problems?
            if child in self.G.nodes:
                self.add_edge(state, child)
            else:
                self.add_node(child)
                self.add_edge(state, child)
        chosen_child = random.choice(children)
        self.state_manager.update_state_manager(chosen_child)
        self.G.nodes[chosen_child]['end_state'] = self.state_manager.is_end_state()
        self.G.get_edge_data(state, chosen_child)['flag'] = 1
        self.simulate(chosen_child)

    def greedy_best_child(self, state: str) -> str:
        sorted_list = sorted(self.G.out_edges(state, data=True), key=lambda x: x[2]['sap_value'], reverse=True)
        if self.state_manager.is_P1(state):
            best_child = sorted_list[0][1]
            self.state_manager.update_state_manager(best_child)
            return best_child
        else:
            best_child = sorted_list[-1][1]
            self.state_manager.update_state_manager(best_child)
            return best_child

    def best_child_uct(self, state: str, out_edgs) -> str:
        node_n = self.G.nodes[state]['n']
        if self.state_manager.is_P1(state):
            best_edge = max(out_edgs,
                                 key=lambda x: x[2]['sap_value'] + self.c * math.sqrt(math.log(node_n) / (1+x[2]['n'])))
        else:
            best_edge = min(out_edgs,
                            key=lambda x: x[2]['sap_value'] - self.c * math.sqrt(math.log(node_n) / (1 + x[2]['n'])))
        best_edge[2]['flag'] = 1
        return best_edge[1]

    def simulate1(self, state: str) -> int: # Is not compatible with the if not out_edgs check in traverse_tree
                                            # Nor compatible with state manager check if end state when we add nodes
        """
        :param state:
        :return: return 1 if the simulation ends in player "true" winning, -1 otherwise
        """
        start_state = state
        while not self.state_manager.is_end_state():
            out_edgs = list(self.G.out_edges(state))
            if not out_edgs:
                children = self.state_manager.generate_child_states(state)
                for child in children:
                    if child in self.G.nodes:
                        self.add_edge(state, child)
                    else:
                        self.add_node(child)
                        self.add_edge(state, child)
                out_edgs = list(self.G.out_edges(state))
            state = random.choice(out_edgs)[1]
        win_player1 = -1 if self.state_manager.is_P1(state) else 1
        self.backpropagate(start_state, win_player1)

    def simulate(self, state: str):
        """
        :param state:
        :return: return 1 if the simulation ends in player "true" winning, -1 otherwise
        """
        start_state = state
        while not self.state_manager.is_end_state():
            children = self.state_manager.generate_child_states(state)
            state = random.choice(children)
            self.state_manager.update_state_manager(state)
        win_player1 = -1 if self.state_manager.is_P1(state) else 1
        self.backpropagate(start_state, win_player1)

    def backpropagate(self, state: str, win_player1: int):
        if state == self.root_state:
            self.G.nodes[state]['n'] += 1
            return
        parent_state = self.get_parent(state)

        self.G.nodes[state]['n'] += 1
        self.G.get_edge_data(parent_state, state)['n'] += 1
        edge_times_enc = self.G.get_edge_data(parent_state, state)['n']
        edge_sap_value = self.G.get_edge_data(parent_state, state)['sap_value']
        self.G.get_edge_data(parent_state, state)['sap_value'] += (win_player1 - edge_sap_value) / edge_times_enc
        self.G.get_edge_data(parent_state, state)['flag'] = 0

        self.backpropagate(parent_state, win_player1)

    # GRAPH METHODS

    def add_node(self, state: str, end_state = None):
        """
        Adds node to the DiGraph G with initial number of encounters to zero
        :param state: (list representing board state, player to move): ([int], bool)
        """
        self.G.add_node(state, n=0, end_state = end_state)

    def add_edge(self, parent_state, child_state):
        """
        Adds edge to the DiGraph G with initial sap_value = 0, number of encounters = 0 and flag meaning this was the
            edge used in the latest tree traversal
        :param parent_state: (list representing board state, player to move): ([int], bool)
        :param child_state: (list representing board state, player to move): ([int], bool)
        """
        self.G.add_edge(parent_state, child_state, sap_value=0, n=0, flag=0)

    def get_child_states(self, state):
        return list(self.G.successors(state))

    def get_parent(self, state: str) -> str:
        parent_list = list(self.G.predecessors(state))
        if len(parent_list) == 1:
            return parent_list[0]
        else:
            flagged_parent_list = [parent for parent in parent_list if self.G.get_edge_data(parent, state)['flag'] == 1]
            if len(flagged_parent_list) == 1:
                return flagged_parent_list[0]
            else:
                raise ValueError('More than one parent of input state with positive flag')

    def cut_tree_at_state(self, state: str):
        sub_tree_nodes = nx.bfs_tree(self.G, state)
        self.G = nx.DiGraph(self.G.subgraph(sub_tree_nodes))

    def is_end_state(self, state):
        return self.G.nodes[state]['end_state']

    def print_graph(self):
        """
        Print the DiGraph object representing the current tree
        """
        pos = nx.shell_layout(self.G)
        blue_player_nodes = []
        red_player_nodes = []
        labels = {}
        for state in self.G.nodes:
            labels[state] = self.state_manager.graph_label(state)
            if self.state_manager.is_P1(state):
                blue_player_nodes.append(state)
            else:
                red_player_nodes.append(state)
        nx.draw_networkx_nodes(self.G, pos, nodelist=blue_player_nodes, node_color='b', alpha=0.5)
        nx.draw_networkx_nodes(self.G, pos, nodelist=red_player_nodes, node_color='r', alpha=0.5)
        nx.draw_networkx_edges(self.G, pos)
        nx.draw_networkx_labels(self.G, pos, labels, font_size=10)
        plt.show()

