import networkx as nx
from mcts.StateManager import StateManager
import matplotlib.pyplot as plt
from typing import Type
import random
import math


class MCTS:
    def __init__(self, state: ([int], bool), state_manager: Type[StateManager], max_tree_height=5):
        self.state_manager = state_manager
        self.G = nx.DiGraph()
        self.root_state = state
        self.add_node(state)
        self.c = 1
        self.max_tree_height = max_tree_height

    def add_node(self, state: str):
        self.G.add_node(state, n=0)

    def add_edge(self, parent_state, child_state):
        self.G.add_edge(parent_state, child_state, sap_value=0, n=0, flag=1)

    def get_visited_child_states(self, state):
        return list(self.G.successors(state))

    def get_parent(self, state: str):
        """
        :param state: ([int], bool)
        :return: parent state: ([int], bool)
        """
        parent_list = list(self.G.predecessors(state))
        if len(parent_list) == 1:
            return parent_list[0]
        else:
            flagged_parent_list = [parent for parent in parent_list if self.G.get_edge_data(parent, state)['flag'] == 1]
            if len(flagged_parent_list) == 1:
                return flagged_parent_list[0]
            else:
                raise ValueError('More than one parent of input state with positive flag')

    def print_graph(self):
        pos = nx.shell_layout(self.G)
        blue_player_nodes = []
        red_player_nodes = []
        labels = {}
        for state in self.G.nodes:
            labels[state] = self.state_manager.graph_label(state)
            if self.state_manager.is_player_1(state):
                blue_player_nodes.append(state)
            else:
                red_player_nodes.append(state)
        nx.draw_networkx_nodes(self.G, pos, nodelist=blue_player_nodes, node_color='b', alpha=0.5)
        nx.draw_networkx_nodes(self.G, pos, nodelist=red_player_nodes, node_color='r', alpha=0.5)
        nx.draw_networkx_edges(self.G, pos)
        nx.draw_networkx_labels(self.G, pos, labels, font_size=10)
        plt.show()

    def run(self, m):
        for i in range(m):
            state = self.select(self.root_state)
            simulation_result = self.simulate(state)
            self.backpropagate(state, simulation_result)
        return self.best_child(self.root_state)

    def select(self, state: str) -> str:
        # while fully_expanded
        possible_child_states = self.state_manager.generate_child_states(state)
        visited_child_states = self.get_visited_child_states(state)
        # Only move to next tree depth if all the children is visited
        tree_height = 1
        while len(possible_child_states) == len(visited_child_states) and \
                len(possible_child_states) > 0 and \
                tree_height <= self.max_tree_height:
            # Get the best child node from the current node
            state = self.best_uct(state)
            possible_child_states = self.state_manager.generate_child_states(state)
            visited_child_states = self.get_visited_child_states(state)
            tree_height += 1
        # If there still are unvisited nodes we pick them
        return self.pick_unvisited(state, possible_child_states, visited_child_states) or state

    def pick_unvisited(self, state: str, possible_child_states: [str], visited_child_states: [str]) -> str:
        unvisited_states = list(filter(lambda s: s not in visited_child_states, possible_child_states))
        if len(unvisited_states) == 0:
            return ""
        chosen_state = random.choice(unvisited_states)
        if chosen_state in self.G.nodes:
            self.add_edge(state, chosen_state)
        else:
            self.add_node(chosen_state)
            self.add_edge(state, chosen_state)
        return chosen_state

    def best_child(self, state: str) -> str:
        sorted_list = sorted(self.G.out_edges(state, data=True), key=lambda x: x[2]['sap_value'], reverse=True)
        if self.state_manager.is_player_1(state):
            return sorted_list[0][1]
        else:
            return sorted_list[-1][1]

    def best_uct(self, state: str) -> str:
        visited_child_states = self.get_visited_child_states(state)
        best_child = None
        best_child_q = -float('Inf') if self.state_manager.is_player_1(state) else float('Inf')
        for i in range(0, len(visited_child_states)):
            child = visited_child_states[i]
            edge_data = self.G.get_edge_data(state, child)
            u = self.u(self.G.nodes[state]['n'], edge_data['n'])
            # Different functions for red and blue
            if self.state_manager.is_player_1(state):
                q = edge_data.get('sap_value') + u
            else:
                q = edge_data.get('sap_value') - u
            # Argmax for blue
            if self.state_manager.is_player_1(state) and q > best_child_q:
                best_child = child
                best_child_q = q
            # Argmin for red
            if not self.state_manager.is_player_1(state) and q < best_child_q:
                best_child = child
                best_child_q = q
        self.G.get_edge_data(state, best_child)['flag'] = 1
        return best_child

    def u(self, number_of_visits_node, number_of_visits_edge):
        return self.c * math.sqrt(math.log(number_of_visits_node) / (1 + number_of_visits_edge))

    def simulate(self, state: str) -> int:
        """
        :param state:
        :return: return 1 if the simulation ends in player "true" winning, -1 otherwise
        """
        while not self.state_manager.is_end_state(state):
            state = random.choice(self.state_manager.generate_child_states(state))
        return 1 if state[1] else -1

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

    def cut_tree_at_state(self, state: str):
        sub_tree_nodes = nx.bfs_tree(self.G, state)
        self.G = nx.DiGraph(self.G.subgraph(sub_tree_nodes))

