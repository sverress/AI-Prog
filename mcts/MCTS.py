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

    def add_node(self, state: ([int], bool)):
        self.G.add_node(self.state_manager.state_to_key(state), state=state, n=0)

    def add_edge(self, parent_state, child_state):
        self.G.add_edge(
            self.state_manager.state_to_key(parent_state),
            self.state_manager.state_to_key(child_state),
            sap_value=0, n=0, flag=1)

    def get_node_attributes(self, state: ([int], bool)):
        """
        returns the desired state as dict. Ex; {'state': ([0, 1, 1, 3], 0), 'n': 0}
        :param state:
        :return: the node attributes: dict
        """
        return self.G.nodes[self.state_manager.state_to_key(state)]

    def get_edge_attributes(self, parent_state: ([int], bool), child_state: ([int], bool)):
        """
        Returns ex; {'sap_value': 0, 'n': 0}
        :param parent_state:
        :param child_state:
        :return: The desired edge attributes: dict
        """
        parent_state_key = self.state_manager.state_to_key(parent_state)
        child_state_key = self.state_manager.state_to_key(child_state)
        return self.G.get_edge_data(parent_state_key, child_state_key)

    def get_node_from_key(self, state_key: str):
        return self.G.nodes._nodes.get(state_key)

    def get_state_from_state_key(self, state_key: str):
        return self.G.nodes[state_key].get('state')

    def get_visited_child_states(self, state):
        return [self.get_node_from_key(child).get('state')
                for child in list(self.G.successors(self.state_manager.state_to_key(state)))]

    def get_predecessor(self, state: ([int], bool)):
        """

        :param state: ([int], bool)
        :return: parent state: ([int], bool)
        """
        state_key = self.state_manager.state_to_key(state)
        predecessor_key = sorted(self.G.in_edges(state_key, data=True), key= lambda x: x[2]['flag'], reverse=True)[0][0]
        return self.get_state_from_state_key(predecessor_key)

    def print_graph(self):
        pos = nx.shell_layout(self.G)
        blue_player_nodes = []
        red_player_nodes = []
        labels = {}
        for key in self.G.nodes._nodes:
            labels[key] = key
            node = self.get_node_attributes(self.get_state_from_state_key(key))
            if node.get('state')[1]:
                blue_player_nodes.append(key)
            else:
                red_player_nodes.append(key)
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

    def select(self, state: ([int], bool)):
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

    def pick_unvisited(self, state: ([int], bool), possible_child_states, visited_child_states):
        unvisited_states = list(filter(lambda s: s not in visited_child_states, possible_child_states))
        if len(unvisited_states) == 0:
            return None
        chosen_state = random.choice(unvisited_states)
        chosen_state_key = self.state_manager.state_to_key(chosen_state)
        if chosen_state_key in self.G.nodes:
            self.add_edge(state, chosen_state)
        else:
            self.add_node(chosen_state)
            self.add_edge(state, chosen_state)
        return chosen_state

    def best_child(self, state: ([int], bool)):
        state_key = self.state_manager.state_to_key(state)
        sorted_list = sorted(self.G.out_edges(state_key, data=True), key=lambda x: x[2]['sap_value'], reverse=True)
        if state[1]:
            best_state_key = sorted_list[0][1]
        else:
            best_state_key = sorted_list[-1][1]
        return self.get_state_from_state_key(best_state_key)

    def best_uct(self, state: ([int], bool)):
        visited_child_states = self.get_visited_child_states(state)
        best_child = None
        best_child_q = -float('Inf') if state[1] else float('Inf')
        for i in range(0, len(visited_child_states)):
            child = visited_child_states[i]
            edge_data = self.get_edge_attributes(state, child)
            u = self.u(self.get_node_attributes(state).get('n'), edge_data.get('n'))
            # Different functions for red and blue
            if state[1]: #child[1]
                q = edge_data.get('sap_value') + u
            else:
                q = edge_data.get('sap_value') - u
            # Argmax for blue
            if state[1] and q > best_child_q:
                best_child = child
                best_child_q = q
            # Argmin for red
            if not state[1] and q < best_child_q:
                best_child = child
                best_child_q = q
        self.get_edge_attributes(state, best_child)['flag'] = 1
        return best_child

    def u(self, number_of_visits_node, number_of_visits_edge):
        return self.c * math.sqrt(math.log(number_of_visits_node) / (1 + number_of_visits_edge))

    def simulate(self, state: ([int], bool)):
        """
        :param state:
        :return: return 1 if the simulation ends in player "true" winning, -1 otherwise
        """
        while not self.state_manager.is_end_state(state):
            state = random.choice(self.state_manager.generate_child_states(state))
        return 1 if state[1] else -1

    def backpropagate(self, state: ([int], bool), win_player1):
        if state == self.root_state:
            self.get_node_attributes(state)['n'] += 1
            return
        parent_state = self.get_predecessor(state)

        self.get_node_attributes(state)['n'] += 1
        self.get_edge_attributes(parent_state, state)['n'] += 1
        edge_times_enc = self.get_edge_attributes(parent_state, state)['n']
        edge_sap_value = self.get_edge_attributes(parent_state, state)['sap_value']
        self.get_edge_attributes(parent_state, state)['sap_value'] += (win_player1 - edge_sap_value) / edge_times_enc
        self.get_edge_attributes(parent_state, state)['flag'] = 0

        self.backpropagate(parent_state, win_player1)

    def cut_tree_at_state(self, state: ([int], bool)):
        sub_tree_nodes = nx.bfs_tree(self.G, self.state_manager.state_to_key(state))
        self.G = nx.DiGraph(self.G.subgraph(sub_tree_nodes))

