import networkx as nx
from mcts.StateManager import StateManager
import matplotlib.pyplot as plt
from typing import Type
import random


class MCTS:
    def __init__(self, state: ([int], bool), state_manager: Type[StateManager]):
        self.state_manager = state_manager
        self.G = nx.DiGraph()
        self.root_state = state
        self.add_node(state)
        self.c = 1

    def add_node(self, state: ([int], bool)):
        self.G.add_node(self.state_manager.state_to_string(state), state=state, n=0)

    def add_edge(self, parent_state, child_state):
        self.G.add_edge(
            self.state_manager.state_to_string(parent_state),
            self.state_manager.state_to_string(child_state),
            sap_value=0, n=0)

    def get_node_data(self, state: ([int], bool)):
        return self.G.nodes._nodes.get(self.state_manager.state_to_string(state))  # Need another way of doing this

    def get_edge_data(self, parent_state, child_state):
        return self.G.get_edge_data(
            self.state_manager.state_to_string(parent_state),
            self.state_manager.state_to_string(child_state)
        )

    def get_node_attributes(self, state: ([int], bool)):
        """
        returns the desired state as dict. Ex; {'state': ([0, 1, 1, 3], 0), 'times_encountered': 0}
        :param state:
        :return: the node attributes: dict
        """
        return self.G.nodes[self.state_manager.state_to_string(state)]

    def get_edge_attributes(self, parent_state: ([int], bool), child_state: ([int], bool)):
        """
        Returns ex; {'sap_value': 0, 'times_encountered': 0}
        :param parent_state:
        :param child_state:
        :return: The desired edge attributes: dict
        """
        parent_state_key = self.state_manager.state_to_string(parent_state)
        child_state_key = self.state_manager.state_to_string(child_state)
        return self.G.get_edge_data(parent_state_key, child_state_key)

    def get_node_from_key(self, state: str):
        return self.G.nodes._nodes.get(state)

    def get_state_from_state_key(self, state_key: str):
        return self.G.nodes[state_key]['state']

    def get_visited_child_states(self, state):
        return [self.get_node_from_key(child).get('state')
                for child in list(self.G.successors(self.state_manager.state_to_string(state)))]

    def get_predecessor(self, state: ([int], bool)):
        """

        :param state: ([int], bool)
        :return: parent state: ([int], bool)
        """
        predecessor_key = [pred for pred in self.G.predecessors(self.state_manager.state_to_string(state))][0]
        return self.get_state_from_state_key(predecessor_key)

    def print_graph(self):
        nx.draw(self.G, with_labels=True)
        plt.show()

    def run(self):
        for i in range(10):  # 1 iteration
            state = self.select(self.root_state)
            simulation_result = self.simulate(state)
            self.backpropagate(state, simulation_result)
        return self.best_child_node(self.root_state)

    def select(self, state: [int]):
        # while fully_expanded
        possible_child_states = self.state_manager.generate_child_states(state)
        visited_child_states = self.get_visited_child_states(state)
        while len(possible_child_states) == len(visited_child_states):
            # Get the best child node from the current node
            state = self.best_child_node(state)
            possible_child_states = self.state_manager.generate_child_states(state)
            visited_child_states = self.get_visited_child_states(state)
        return MCTS.pick_unvisited(possible_child_states, visited_child_states) or state

    def pick_unvisited(possible_states, visited_states):
        unvisited_states = list(filter(lambda state: state not in visited_states, possible_states))
        if len(unvisited_states) == 0:
            return None
        return random.choice(unvisited_states)

    def best_child_node(self, state):
        hello = [predecessor for predecessor in self.G.predecessors(str(state))]
        return state

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
        if state == self.root_state:
            return
        parent_state = self.get_predecessor(state)

        node_times_enc = self.get_node_attributes(state)['times_encountered']
        node_times_enc += 1
        edge_times_enc = self.G.get_edge_attributes(parent_state, state)['times_encountered']
        edge_times_enc += 1
        edge_sap_value = self.G.get_edge_attributes(parent_state, state)['sap_value']
        edge_sap_value += (win_player1 - edge_sap_value)/node_times_enc
        self.backpropagate(parent_state, win_player1)