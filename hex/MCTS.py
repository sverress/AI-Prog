import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import numpy as np

from hex.StateManager import StateManager


class MCTS:
    def __init__(self, state_manager: StateManager, actor_net, max_tree_height=5, c=1):
        self.state_manager = state_manager
        self.tree = StateTree()
        self.root_state = self.state_manager.get_state()
        self.tree.add_state_node(
            self.root_state, is_end_state=self.state_manager.is_end_state()
        )
        self.c = c
        self.max_tree_height = max_tree_height
        self.actor_net = actor_net

    # MCTS METHODS
    def get_distribution(self, state: str):
        """
        Returns the distribution of total visits for child nodes of input state
        :param state: state to get distribution from
        :return: a normalized list of length equal to the total number of positions on the board
        """

        split_board = lambda input_state: input_state.split(":")
        parent_board, parent_player = split_board(state)
        child_states = self.tree.get_child_states(state)
        change_indices_dict = {}
        total_visits = 0
        for child in child_states:
            child_board, child_player = split_board(child)
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

    def run(self, m: int):
        """
        Runs the monte carlo tree search algorithm, tree traversal -> rollout -> backprop, m times. Then finds the greedy
            best move from root state of the current tree
        :param m: number of iterations to run
        :return: the greedy best move from root node of the current tree
        """
        for i in range(m):
            self.traverse_tree(self.root_state, depth=0)
            self.state_manager.set_state_manager(self.root_state)
        distribution = self.get_distribution(self.root_state)
        self.actor_net.add_case(self.root_state, distribution.copy())
        child = self.greedy_best_child(self.root_state)
        self.root_state = child
        self.tree.cut_at_state(child)
        return child

    def traverse_tree(self, state: str, depth):
        if depth == self.max_tree_height or self.tree.is_end_state(state):
            self.simulate(state)
            return
        outgoing_edges = self.tree.get_outgoing_edges(state)
        if not outgoing_edges:
            self.expand(state)
            return
        unvisited_outgoing_edges = self.tree.get_outgoing_edges(state, only_unvisited=True)
        if unvisited_outgoing_edges:
            child = random.choice(unvisited_outgoing_edges)[1]
            self.state_manager.set_state_manager(child)
            self.tree.set_end_state(child, self.state_manager.is_end_state())
            self.tree.set_active_edge(state, child, True)
            self.simulate(child)
            return
        child = self.best_child_uct(state, outgoing_edges)
        self.state_manager.set_state_manager(child)
        self.traverse_tree(child, depth + 1)

    def expand(self, state):
        children = StateManager.generate_child_states(state)
        for child in children:
            # Could this cause some problems?
            if child in self.tree.get_nodes():
                self.tree.add_edge(state, child)
            else:
                self.tree.add_state_node(child)
                self.tree.add_edge(state, child)
        chosen_child = random.choice(children)
        self.state_manager.set_state_manager(chosen_child)
        self.tree.set_end_state(chosen_child, self.state_manager.is_end_state())
        self.tree.set_active_edge(state, chosen_child, True)
        self.simulate(chosen_child)

    def greedy_best_child(self, state: str) -> str:
        sorted_list = self.tree.get_outgoing_edges(state, sorted_by_saps=True)
        if self.state_manager.get_player(state) == 1:
            best_child = sorted_list[0][1]  # Why is this the best one?
            self.state_manager.set_state_manager(best_child)
            return best_child
        else:
            best_child = sorted_list[-1][1]
            self.state_manager.set_state_manager(best_child)
            return best_child

    def best_child_uct(self, state: str, out_edgs) -> str:
        node_n = self.tree.get_state_number_of_visits(state)
        if self.state_manager.get_player(state) == 1:
            best_edge = max(
                out_edgs,
                key=lambda x: x[2]["sap_value"]
                + self.c * math.sqrt(math.log(node_n) / (1 + x[2]["n"])),
            )
        else:
            best_edge = min(
                out_edgs,
                key=lambda x: x[2]["sap_value"]
                - self.c * math.sqrt(math.log(node_n) / (1 + x[2]["n"])),
            )
        best_edge[2]["flag"] = 1
        return best_edge[1]

    def simulate1(
        self, state: str
    ) -> int:  # Is not compatible with the if not out_edgs check in traverse_tree
        # Nor compatible with state manager check if end state when we add nodes
        """
        :param state:
        :return: return 1 if the simulation ends in player "true" winning, -1 otherwise
        """
        start_state = state
        while not self.state_manager.is_end_state():
            outgoing_edges = list(self.tree.get_outgoing_edges(state))
            if not outgoing_edges:
                children = StateManager.generate_child_states(state)
                for child in children:
                    if child in self.tree.get_nodes():
                        self.tree.add_edge(state, child)
                    else:
                        self.tree.add_state_node(child)
                        self.tree.add_edge(state, child)
                outgoing_edges = self.tree.get_outgoing_edges(state)
            state = random.choice(outgoing_edges)[1]
        win_player1 = -1 if self.state_manager.get_player(state) == 1 else 1
        self.backpropagate(start_state, win_player1)

    def epsilon_greedy_child_state_from_distribution(
        self, distribution: np.ndarray, state: str, epsilon=0.2
    ):
        if random.random() > epsilon:
            chosen_index = int(np.argmax(distribution))
        else:
            # Choose random state from those with positive probability
            # prob == 0 might be occupied cells on the board
            chosen_index = random.choice(
                [i[0] for i, prob in np.ndenumerate(distribution) if prob > 0]
            )
        return StateManager.get_next_state_from_distribution_position(
            chosen_index, state
        )

    def simulate(self, state: str):
        """
        Performs one roll-out using the actor net as policy
        :param state: start state of simulation
        :return: return 1 if the simulation ends in player "true" winning, -1 otherwise
        """
        start_state = state
        while not self.state_manager.is_end_state():
            distribution = self.actor_net.predict(state)
            new_state = self.epsilon_greedy_child_state_from_distribution(
                distribution, state
            )
            self.state_manager.set_state_manager(new_state)
            state = new_state
        # If we are in an end state the opposite player of the current player is the winner
        win_player1 = (
            -1 if self.state_manager.current_player() == 1 else 1
        )  # Reward for end states
        self.backpropagate(start_state, win_player1)

    def backpropagate(self, state: str, win_player1: int):
        if state == self.root_state:
            self.tree.increment_state_number_of_visits(state)
            return
        parent_state = self.tree.get_parent(state)

        self.tree.increment_state_number_of_visits(state)
        self.tree.increment_edge_number_of_visits(parent_state, state)
        edge_times_enc = self.tree.get_edge_number_of_visits(parent_state, state)
        edge_sap_value = self.tree.get_sap_value(parent_state, state)
        new_sap_value = (
            self.tree.get_sap_value(parent_state, state)
            + (win_player1 - edge_sap_value) / edge_times_enc
        )
        self.tree.set_sap_value(parent_state, state, new_sap_value)
        self.tree.set_active_edge(parent_state, state, False)

        self.backpropagate(parent_state, win_player1)


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
    def __init__(self):
        self.graph = nx.DiGraph()

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

    def cut_at_state(self, state: str) -> None:
        sub_tree_nodes = nx.bfs_tree(self.graph, state)
        self.graph = nx.DiGraph(self.graph.subgraph(sub_tree_nodes))

    def edge_is_unvisited(self, edge):
        parent, child = edge
        return self.get_edge_number_of_visits(parent, child) == 0

    def get_outgoing_edges(
        self, state: str, only_unvisited=False, sorted_by_saps=False
    ) -> [(str, str)]:

        outgoing_edges = list(self.graph.out_edges(state))
        if sorted_by_saps:
            outgoing_edges = sorted(
                self.graph.out_edges(state, data=True),
                key=lambda x: x[2]["sap_value"],
                reverse=True,
            )
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
