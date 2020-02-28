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
        self.G.add_node(self.state_manager.state_to_string(state), state=state, times_encountered=0)

    def add_edge(self, parent_state, child_state):
        self.G.add_edge(self.state_manager.state_to_string(parent_state), self.state_manager.state_to_string(child_state), sap_value=0, times_encountered=0)

    def get_node(self, state: ([int], bool)):
        return dict(self.G.nodes()).get(self.state_manager.state_to_string(state))

    def get_visited_child_states(self, state):
        return list(self.G.predecessors(self.state_manager.state_to_string(state)))

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

    @staticmethod
    def pick_unvisited(possible_states, visited_states):
        unvisited_states = list(filter(lambda state: state not in visited_states, possible_states))
        if len(unvisited_states) == 0:
            return None
        return random.choice(unvisited_states)

    def best_child_node(self, state):
        hello = [predecessor for predecessor in self.G.predecessors(str(state))]
        return state

    def expand(self, state: ([int], bool)):
        for child_state in self.state_manager.generate_child_states(state):
            self.add_node(child_state)
            self.add_edge(state, child_state)

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
        self.get_node(state)['times_encountered'] += 1
        # Update edges
        self.backpropagate(self.G.predecessors(self.state_manager.state_to_string(state)))

    def sim_tree(self, state: [int]):
        path = [state]
        while not self.state_manager.is_end_state(state):
            if not bool(self.get_node(state)):  # If state not in tree
                self.add_node(state)
                self.add_edge()