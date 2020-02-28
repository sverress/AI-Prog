import networkx as nx
from mcts.StateManager import StateManager
import matplotlib.pyplot as plt
from typing import Type
import random
import math


class MCTS:
    def __init__(self, state: ([int], bool), state_manager: Type[StateManager]):
        self.state_manager = state_manager
        self.G = nx.DiGraph()
        self.root_state = state
        self.add_node(state)
        self.c = 1

    def add_node(self, state: ([int], bool)):
        self.G.add_node(self.state_manager.state_to_string(state), state=state, n=1)

    def add_edge(self, parent_state, child_state):
        self.G.add_edge(
            self.state_manager.state_to_string(parent_state),
            self.state_manager.state_to_string(child_state),
            sap_value=0, n=1)

    def get_node_data(self, state: ([int], bool)):
        return self.G.nodes._nodes.get(self.state_manager.state_to_string(state))  # Need another way of doing this

    def get_edge_data(self, parent_state, child_state):
        return self.G.get_edge_data(
            self.state_manager.state_to_string(parent_state),
            self.state_manager.state_to_string(child_state)
        )

    def get_node_from_key(self, state: str):
        return self.G.nodes._nodes.get(state)

    def get_visited_child_states(self, state):
        return [self.get_node_from_key(child).get('state')
                for child in list(self.G.successors(self.state_manager.state_to_string(state)))]

    def print_graph(self):
        pos = nx.shell_layout(self.G)
        blue_player_nodes = []
        red_player_nodes = []
        labels = {}
        for key in self.G.nodes._nodes:
            labels[key] = key
            node = self.G.nodes._nodes.get(key)
            if node.get('state')[1]:
                blue_player_nodes.append(key)
            else:
                red_player_nodes.append(key)
        nx.draw_networkx_nodes(self.G, pos, nodelist=blue_player_nodes, node_color='b', alpha=0.5)
        nx.draw_networkx_nodes(self.G, pos, nodelist=red_player_nodes, node_color='r', alpha=0.5)
        nx.draw_networkx_edges(self.G, pos)
        nx.draw_networkx_labels(self.G, pos, labels, font_size=10)
        plt.show()

    def run(self):
        for i in range(10):
            state = self.select(self.root_state)
            simulation_result = self.simulate(state)
            self.backpropagate(state, simulation_result)
            self.print_graph()
        return self.best_child_node(self.root_state)

    def select(self, state: [int]):
        # while fully_expanded
        possible_child_states = self.state_manager.generate_child_states(state)
        visited_child_states = self.get_visited_child_states(state)
        # Only move to next tree depth if all the children is visited
        while len(possible_child_states) == len(visited_child_states) and len(possible_child_states) > 0:
            # Get the best child node from the current node
            state = self.best_child_node(state)
            possible_child_states = self.state_manager.generate_child_states(state)
            visited_child_states = self.get_visited_child_states(state)
        # If there still are unvisited nodes we pick them
        return self.pick_unvisited(state) or state

    def pick_unvisited(self, state):
        possible_child_states = self.state_manager.generate_child_states(state)
        visited_child_states = self.get_visited_child_states(state)
        unvisited_states = list(filter(lambda state: state not in visited_child_states, possible_child_states))
        if len(unvisited_states) == 0:
            return None
        chosen_state = random.choice(unvisited_states)
        self.add_node(chosen_state)
        self.add_edge(state, chosen_state)
        return chosen_state

    def best_child_node(self, state):
        visited_child_states = self.get_visited_child_states(state)
        best_child = None
        best_child_q = -float('Inf') if state[1] else float('Inf')
        for i in range(0, len(visited_child_states)):
            child = visited_child_states[i]
            edge_data = self.get_edge_data(state, child)
            u = self.u(self.get_node_data(state).get('n'), edge_data.get('n'))
            # Different functions for red and blue
            if child[1]:
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
        return best_child

    def u(self, number_of_visits_node, number_of_visits_edge):
        return self.c * math.sqrt(abs(math.log(number_of_visits_node/(1+number_of_visits_edge))))

    def simulate(self, state: ([int], bool)):
        """
        #sudocode:
        while non_terminal(node):
            node = rollout_policy(node)
        return result(node)

        :param state:
        :return: return 1 if the simulation ends in player "true" winning, 0 otherwise
        """
        return 1 if random.random() > 0.1 else -1

    def backpropagate(self, state: ([int], bool), win_player1):
        pass