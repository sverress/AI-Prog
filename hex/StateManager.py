import networkx as nx
import math
import copy
import matplotlib as plt
import numpy as np


class StateManager:
    """
    CLASS FOR STATE MANAGER
    Class uses internal representation of state as a graph to make computations.
    All communication with the outside is done with string representations
    """

    def __init__(self, k: int, p: int):
        self.k = k
        self.state = (":" + str(p)).zfill(k ** 2 + 2)
        self.board = self.build_board(self.state)
        self.P1graph = nx.Graph()
        self.P2graph = nx.Graph()

    def __str__(self):
        """
        Creates a simple toString for a board object
        :return: string representation of the board
        """
        output = ""
        for row in self.board:
            for col in row:
                output += f"{node} "
            output += "\n"
        return output

    def build_board(self, state):
        board = []
        for i in range(self.k):
            board.append([])
            for j in range(self.k):
                board[i].append(int(state[i * self.k + j]))
        return board

    def get_state(self):
        return self.state

    def reset_state_manager(self, state):
        self.state = state
        self.board = self._get_internal_state_rep(state)[0]
        for node in list(self.P1graph.nodes):
            if self.board[node[0]][node[1]] == 0:
                self.P1graph.remove_node(node)
        for node in list(self.P2graph.nodes):
            if self.board[node[0]][node[1]] == 0:
                self.P2graph.remove_node(node)

    def update_state_manager(self, state):
        error_check = 0
        for i in range(len(state[:-2])):
            row = math.floor(i / self.k)
            if state[i] != self.state[i]:
                col = i % self.k
                self.board[row][col] = int(state[i])
                cell = (row, col)
                if self.state[-1] == "1":
                    self.P1graph.add_node(cell)
                    same_player_neighbors = self.get_same_player_neighbors(cell, 1)
                    for neigh in same_player_neighbors:
                        if neigh in self.P1graph:
                            self.P1graph.add_edge(cell, neigh)
                else:
                    self.P2graph.add_node(cell)
                    same_player_neighbors = self.get_same_player_neighbors(cell, 2)
                    for neigh in same_player_neighbors:
                        if neigh in self.P2graph:
                            self.P2graph.add_edge(cell, neigh)
                error_check += 1
                if error_check > 1:
                    print("error in update state manager")
        self.state = state

    def generate_child_states(self, state: str) -> [str]:
        """
        Takes in a parent state and returns the child states from this state
        :param state: string representing state of game
        :return: list of strings representing child states
        """
        children = []
        player = state[-1]
        next_player = "1" if player == "2" else "2"
        state_list = list(state)
        for i, val in enumerate(state[:-2]):
            if val == "0":
                child_list = copy.deepcopy(state_list)
                child_list[i] = player
                child_list[-1] = next_player
                children.append("".join(child_list))
        return children

    def is_end_state(self) -> str:
        """
        :param state: string representing state of game
        :return: a boolean stating if state is end state
        """
        if len(self.P1graph.nodes) != [
            item for sublist in self.board for item in sublist
        ].count(1):
            print("erorororoor")
        if len(self.P2graph.nodes) != [
            item for sublist in self.board for item in sublist
        ].count(2):
            print("erorororoor")

        # Perhaps first check if player one is present in all rows or player 2 is present in all columns -> decr run time
        if self.state[-1] == "1":
            # Check if player 2 won with the last move
            for row1 in range(self.k):
                if self.board[row1][0] == 2:
                    for row2 in range(self.k):
                        if self.board[row2][self.k - 1] == 2:
                            if nx.has_path(self.P2graph, (row1, 0), (row2, self.k - 1)):
                                return True
        else:
            # Check if player 1 won with the last move
            for col1 in range(self.k):
                if self.board[0][col1] == 1:
                    for col2 in range(self.k):
                        if self.board[self.k - 1][col2] == 1:
                            if nx.has_path(self.P1graph, (0, col1), (self.k - 1, col2)):
                                return True
        return False

    def pretty_state_string(self) -> str:
        return str(self.board)

    def get_move_string(prev_state: str, state: str) -> str:
        prev_board, prev_player = StateManager._get_internal_state_rep(prev_state)
        current_board, current_player = StateManager._get_internal_state_rep(state)
        if prev_board[0] - current_board[0] == 1:
            return "picks up copper"
        if prev_board[0] - current_board[0] == 2:
            return "picks up gold"
        # Find changed indices
        to_cell_index, from_cell_index = [
            i for i in range(len(current_board)) if current_board[i] != prev_board[i]
        ]
        # Determine type of piece
        moved_piece_string = "gold" if prev_board[from_cell_index] == 2 else "copper"
        return (
            f"moves {moved_piece_string} from cell {from_cell_index} to {to_cell_index}"
        )

    def _get_internal_state_rep(self, state: str) -> ([[int]], bool):
        """
        Method to be used by subclass to convert from string state rep to internal representation
        :param state: string representing state of game
        :return: internal state representation
        """
        state_str, player_str = state.split(":")
        return self.build_board(state_str), player_str == "1"

    def _get_external_state_rep(self, state: ([[int]], bool)) -> str:
        """
        External representation format ´<state/board>:<player nr.>´
        :param state: internal representation of state
        :return: external representation of state
        """
        output = ""
        for row in state[0]:
            for col in state[0][row]:
                output += str(state[row][col])
        output += ":1" if state[1] else ":2"
        return output

    def is_P1(self, state: str) -> bool:
        return state[-1] == "1"

    def graph_label(self, state: str) -> str:
        return str(StateManager._get_internal_state_rep(state)[0])

    def get_same_player_neighbors(self, position: tuple, player: int) -> [tuple]:
        """
        Gets all the neighbors for the given position of the board
        :param position: (x_index: int, y_index: int)
        :return: list of cell neighbors
        """
        neighbors = self.get_neighbors_indices(position)
        return list(filter(lambda x: self.board[x[0]][x[1]] == player, neighbors))

    def get_neighbors_indices(self, position) -> [tuple]:
        r, c = position
        indices = [
            (r - 1, c),
            (r - 1, c + 1),
            (r, c - 1),
            (r, c + 1),
            (r + 1, c - 1),
            (r + 1, c),
        ]
        # Removing indices outside the board
        return list(filter(lambda pos: self.filter_positions(pos), indices))

    def filter_positions(self, position: tuple):
        """
        Standard filters for all position tuples in board class
        :param position: (x_index: int, y_index: int)
        :return: boolean describing if the position is within the board size
        """
        x, y = position
        return 0 <= x < self.k and 0 <= y < self.k

    def print_graph(self):
        """
        Print the DiGraph object representing the current tree
        """
        pos = nx.shell_layout(self.P1graph)
        nodes = []
        labels = {}
        for state in self.P1graph.nodes:
            labels[state] = self.graph_label(state)
            nodes.append(state)
        nx.draw_networkx_nodes(
            self.P1graph, pos, nodelist=nodes, node_color="b", alpha=0.5
        )
        nx.draw_networkx_edges(self.P1graph, pos)
        nx.draw_networkx_labels(self.P1graph, pos, labels, font_size=10)
        plt.show()
