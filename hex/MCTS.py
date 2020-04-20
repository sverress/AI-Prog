import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import numpy as np

from hex.StateManager import StateManager


class MCTS:
    def __init__(self, state_manager: StateManager, actor_net, max_tree_height=5, c=1):
        self.state_manager = StateManager(
            state_manager.board_size, state_manager.current_player()
        )
        self.tree = StateTree(self.state_manager.get_state())
        self.tree.add_state_node(
            self.tree.root_state, is_end_state=self.state_manager.is_end_state()
        )
        self.c = c
        self.max_tree_height = max_tree_height
        self.actor_net = actor_net

    def run(self, m: int):
        """
        Main method: Runs the monte carlo tree search algorithm, tree traversal -> rollout -> backprop, m times.
        Then finds the greedy best move from root state of the current tree
        :param m: number of iterations to run
        :return: the greedy best action from root node of the current tree
        """
        for i in range(m):
            rollout_state = self.traverse_tree(self.tree.root_state, depth=0)
            simulation_reward = self.simulate(rollout_state)
            self.backpropagate(rollout_state, simulation_reward)
            self.state_manager.set_state_manager(self.tree.root_state)
        distribution = self.get_distribution(self.tree.root_state)
        self.actor_net.add_case(self.tree.root_state, distribution.copy())
        action = self.greedy_best_action(self.tree.root_state)
        self.state_manager.perform_action(action)
        self.tree.cut_tree_with_new_root_node(self.state_manager.get_state())
        return action

    # MAIN ALGORITHM METHODS

    def traverse_tree(self, state: str, depth: int) -> str:
        """
        Traversing the tree expanding nodes by using the tree policy (tree_policy)
        :param state: current state
        :param depth: current depth of the tree
        :return chosen state to simulate from
        """
        if depth == self.max_tree_height or self.tree.is_end_state(state):
            return state
        # If the current state has not explored it's children yet: Add all to graph and chose one to simulate from
        elif not self.tree.get_outgoing_edges(state):
            children = self.expand(state)
            return self.choose_random_child(state, children)
        # If the current state still has unvisited children: chose one at random and simulate from it
        elif self.tree.get_outgoing_edges(state, only_unvisited=True):
            return self.choose_random_child(
                state,
                [
                    child
                    for (parent, child) in self.tree.get_outgoing_edges(
                        state, only_unvisited=True
                    )
                ],
            )
        else:
            child = self.tree_policy(state)
            self.state_manager.check_difference_and_perform_action(child)
            return self.traverse_tree(child, depth + 1)

    def expand(self, state) -> [str]:
        """
        Expanding all child nodes from the input state and adding them to the graph.
        :param state: state to find all children from
        :return: list of all child states
        """
        children = StateManager.generate_child_states(state)
        for child in children:
            if child not in self.tree.get_nodes():
                self.tree.add_state_node(child)
            self.tree.add_edge(state, child)
        return children

    def simulate(self, state: str):
        """
        Performs one roll-out using the actor net as policy
        :param state: start state of simulation
        :return: return 1 if the simulation ends in player "true" winning, -1 otherwise
        """
        start_state = state
        self.state_manager.set_state_manager(state)
        while not self.state_manager.is_end_state():
            distribution = self.actor_net.predict(self.state_manager.get_state())
            chosen_action = self.epsilon_greedy_action_from_distribution(
                distribution, self.state_manager.get_state()
            )
            self.state_manager.perform_action(chosen_action)
        return MCTS.get_end_state_reward(self.state_manager.current_player())

    def backpropagate(self, state: str, simulation_reward: int):
        """
        Starts at rollout start state and jumps up in the tree updating the nodes sap and number of visits
        :param state: rollout start state
        :param simulation_reward: reward from simulation
        """
        if state == self.tree.root_state:
            self.tree.increment_state_number_of_visits(state)
            return
        parent_state = self.tree.get_parent(state)

        self.tree.increment_state_number_of_visits(state)
        self.tree.increment_edge_number_of_visits(parent_state, state)
        edge_times_enc = self.tree.get_edge_number_of_visits(parent_state, state)
        edge_sap_value = self.tree.get_sap_value(parent_state, state)
        new_sap_value = (
            self.tree.get_sap_value(parent_state, state)
            + (simulation_reward - edge_sap_value) / edge_times_enc
        )
        self.tree.set_sap_value(parent_state, state, new_sap_value)
        self.tree.set_active_edge(parent_state, state, False)

        self.backpropagate(parent_state, simulation_reward)

    # HELPER METHODS

    def tree_policy(self, state: str) -> str:
        """
        Using the uct score to determine the child state of a input state
        :param state: input state
        :return: child state
        """
        state_number_of_visits = self.tree.get_state_number_of_visits(state)
        if self.state_manager.get_player(state) == 1:
            best_edge = self.tree.get_outgoing_edges(
                state,
                sort_by_function=lambda edge: self.compute_uct(
                    self.tree.get_sap_value(*edge),
                    state_number_of_visits,
                    self.tree.get_edge_number_of_visits(*edge),
                    True,
                ),
            )[0]
        else:
            best_edge = self.tree.get_outgoing_edges(
                state,
                sort_by_function=lambda edge: self.compute_uct(
                    self.tree.get_sap_value(*edge),
                    state_number_of_visits,
                    self.tree.get_edge_number_of_visits(*edge),
                    False,
                ),
            )[-1]
        parent, best_child = best_edge
        self.tree.set_active_edge(parent, best_child, True)
        return best_child

    def compute_uct(
            self,
            sap_value: float,
            number_of_visits_node: int,
            number_of_visits_edge: int,
            maximizing_player: bool,
    ) -> float:
        """
        Computes the uct for the tree policy
        :param sap_value: sap value for the edge
        :param number_of_visits_node: number of visits for the parent state
        :param number_of_visits_edge: number of visits for the edge between the two nodes
        :param maximizing_player: if the current player is the maximizing player
        :return: uct value
        """
        uct = sap_value
        usa_term = self.c * math.sqrt(
            math.log(number_of_visits_node) / (1 + number_of_visits_edge)
        )
        if maximizing_player:
            uct += usa_term
        else:
            uct -= usa_term
        return uct

    def greedy_best_action(self, state: str) -> str:
        sorted_list = self.tree.get_outgoing_edges(
            state, sort_by_function=lambda edge: self.tree.get_sap_value(*edge)
        )
        if self.state_manager.get_player(state) == 1:
            best_edge = sorted_list[0]
        else:
            best_edge = sorted_list[-1]
        return self.state_manager.get_action(*best_edge)

    def choose_random_child(self, parent_state: str, child_list: [str]) -> str:
        """
        Helper method choosing a random state from the child list and adding edge and node parameters
        :param parent_state: parent state for the child list (to set edge parameters)
        :param child_list: list of children from parent state
        :return: chosen child
        """
        child = random.choice(child_list)
        self.state_manager.check_difference_and_perform_action(child)
        self.tree.set_end_state(child, self.state_manager.is_end_state())
        self.tree.set_active_edge(parent_state, child, True)
        return child


    def epsilon_greedy_action_from_distribution(
        self, distribution: np.ndarray, state: str, epsilon=0.2
    ):
        """
        Chooses an epsilon greedy index from the distribution converting that index to an action
        :param distribution: distribution from number of simulations per node
        :param state: current state to calculate action
        :param epsilon: the epsilon value to be used
        :return: actionstring
        """
        if random.random() > epsilon:
            chosen_index = int(np.argmax(distribution))
        else:
            # Choose random state from those with positive probability
            # prob == 0 might be occupied cells on the board
            chosen_index = random.choice(
                [i[0] for i, prob in np.ndenumerate(distribution) if prob > 0]
            )
        return self.state_manager.get_action_from_flattened_board_index(
            chosen_index, state
        )

    @staticmethod
    def get_end_state_reward(current_player: int) -> int:
        """
        We have chosen player 1 to be "us", giving a positive reward if player 1 wins.
        :param current_player: current player for the state manager
        :return: reward for end state
        """
        return -1 if current_player == 1 else 1

    def get_distribution(self, state: str):
        """
        Returns the distribution of total visits for child nodes of input state
        :param state: state to get distribution from
        :return: a normalized list of length equal to the total number of positions on the board
        """

        parent_board, parent_player = StateManager.extract_state(state)
        child_states = self.tree.get_child_states(state)
        change_indices_dict = {}
        total_visits = 0
        for child in child_states:
            child_board, child_player = StateManager.extract_state(child)
            for i in range(len(child_board)):
                if parent_board[i] != child_board[i]:
                    child_number_of_visits = self.tree.get_state_number_of_visits(child)
                    change_indices_dict[i] = child_number_of_visits
                    total_visits += child_number_of_visits
                    break

        return [
            change_indices_dict[index] / total_visits
            if index in change_indices_dict
            else 0
            for index in range(self.state_manager.board_size ** 2)
        ]


class TreeConstants:
    # Node attributes
    IS_END_STATE = "is_end_state"

    # Edge attributes
    SAP_VALUE = "sap_value"
    IS_ACTIVE = "is_active"

    # Both
    NUMBER_OF_VISITS = "n"

    # Graph Colors
    PLAYER1_COLOR = "b"
    PLAYER2_COLOR = "r"


class StateTree:
    def __init__(self, root_state: str):
        self.graph = nx.DiGraph()
        self.root_state = root_state

    def set_root_state(self, state: str) -> None:
        self.root_state = state

    def get_nodes(self):
        return self.graph.nodes

    def add_state_node(self, state: str, is_end_state=False):
        """
        Adds node to the DiGraph G with initial number of encounters to zero
        :param state: string representation of state
        :param is_end_state: boolean stating if the new state is an end state
        """

        self.graph.add_node(
            state,
            **{
                TreeConstants.NUMBER_OF_VISITS: 0,
                TreeConstants.IS_END_STATE: is_end_state,
            }
        )

    def get_child_states(self, state: str) -> [str]:
        return list(self.graph.successors(state))

    def get_state_number_of_visits(self, state: str) -> int:
        return self.graph.nodes[state][TreeConstants.NUMBER_OF_VISITS]

    def increment_state_number_of_visits(self, state: str) -> None:
        self.graph.nodes[state][TreeConstants.NUMBER_OF_VISITS] += 1

    def cut_tree_with_new_root_node(self, state: str) -> None:
        self.set_root_state(state)
        sub_tree_nodes = nx.bfs_tree(self.graph, state)
        self.graph = nx.DiGraph(self.graph.subgraph(sub_tree_nodes))

    def edge_is_unvisited(self, edge):
        parent, child = edge
        return self.get_edge_number_of_visits(parent, child) == 0

    def get_outgoing_edges(
        self, state: str, only_unvisited=False, sort_by_function=None
    ) -> [(str, str)]:

        outgoing_edges = list(self.graph.out_edges(state))
        if sort_by_function:
            outgoing_edges = sorted(outgoing_edges, key=sort_by_function, reverse=True,)
        if only_unvisited:
            outgoing_edges = [
                edge for edge in outgoing_edges if self.edge_is_unvisited(edge)
            ]
        return outgoing_edges

    def is_end_state(self, state: str) -> bool:
        return self.graph.nodes[state][TreeConstants.IS_END_STATE]

    def set_end_state(self, state: str, value: bool) -> None:
        self.graph.nodes[state][TreeConstants.IS_END_STATE] = value

    def add_edge(self, parent_state, child_state):
        """
        Adds edge to the DiGraph G with initial sap_value = 0, number of encounters = 0 and flag meaning this was the
            edge used in the latest tree traversal
        :param parent_state: (list representing board state, player to move): ([int], bool)
        :param child_state: (list representing board state, player to move): ([int], bool)
        """
        self.graph.add_edge(
            parent_state,
            child_state,
            **{
                TreeConstants.SAP_VALUE: 0.0,
                TreeConstants.NUMBER_OF_VISITS: 0,
                TreeConstants.IS_ACTIVE: 0,
            }
        )

    def get_sap_value(self, parent_state: str, child_state: str) -> float:
        return self.graph.get_edge_data(parent_state, child_state)[
            TreeConstants.SAP_VALUE
        ]

    def set_sap_value(self, parent_state: str, child_state: str, value: float) -> None:
        self.graph.get_edge_data(parent_state, child_state)[
            TreeConstants.SAP_VALUE
        ] = value

    def set_active_edge(self, parent_state: str, child_state: str, value: bool) -> None:
        """
        This is what previously was called a `flag` meaning this
            edge was used in the latest tree traversal
        """
        self.graph.get_edge_data(parent_state, child_state)[
            TreeConstants.IS_ACTIVE
        ] = value

    def is_active_edge(self, parent_state: str, child_state: str) -> bool:
        """
        This is what previously was called a `flag` meaning this
            edge was used in the latest tree traversal
        """
        return self.graph.get_edge_data(parent_state, child_state)[
            TreeConstants.IS_ACTIVE
        ]

    def get_edge_number_of_visits(self, parent_state: str, child_state: str) -> int:
        return self.graph.get_edge_data(parent_state, child_state)[
            TreeConstants.NUMBER_OF_VISITS
        ]

    def increment_edge_number_of_visits(
        self, parent_state: str, child_state: str
    ) -> None:
        self.graph.get_edge_data(parent_state, child_state)[
            TreeConstants.NUMBER_OF_VISITS
        ] += 1

    def get_parent(self, state: str) -> str:
        parent_list = list(self.graph.predecessors(state))
        if len(parent_list) == 1:
            return parent_list[0]
        else:
            active_parent_list = [
                parent for parent in parent_list if self.is_active_edge(parent, state)
            ]
            if len(active_parent_list) == 1:
                return active_parent_list[0]
            else:
                raise ValueError(
                    "More than one parent of input state with positive flag"
                )

    def print_graph(self, state_manager):
        """
        Print the DiGraph object representing the current tree
        """
        pos = nx.shell_layout(self.graph)
        blue_player_nodes = []
        red_player_nodes = []
        labels = {}
        for state in self.graph.nodes:
            labels[state] = state_manager.graph_label(state)
            if state_manager.get_player(state) == 1:
                blue_player_nodes.append(state)
            else:
                red_player_nodes.append(state)
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            nodelist=blue_player_nodes,
            node_color=TreeConstants.PLAYER1_COLOR,
            alpha=0.5,
        )
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            nodelist=red_player_nodes,
            node_color=TreeConstants.PLAYER2_COLOR,
            alpha=0.5,
        )
        nx.draw_networkx_edges(self.graph, pos)
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=10)
        plt.show()
