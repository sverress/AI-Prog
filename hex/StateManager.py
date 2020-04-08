import networkx as nx
import math
import copy
import matplotlib as plt
import numpy as np

from libs.board import Board


class StateManager(Board):
    """
    STATE MANAGER
    Class uses internal representation of state as a graph to make computations.
    All communication with the outside is done with string representations ´board_string:current_player´ ex: 0201:2
    """

    def __init__(self, board_size: int, starting_player: int) -> None:
        """
        Constructor of StateManager. Inherits from the Board class.
        Builds emtpy self.board from the self.state variable created.
        Creates two graphs for each player keeping track of the structure of their pieces
        :param board_size: number of rows/cols in the board
        :param starting_player: the player that starts, either 1 or 2.
        """
        if starting_player > 2 or starting_player < 1:
            raise ValueError("Starting player should be either 1 or 2")
        if board_size > 10:
            raise Warning("Board not tested for boards bigger than board size 10")
        self.state = (":" + str(starting_player)).zfill(board_size ** 2 + 2)
        super().__init__(board_size, self.state)
        self.P1graph = nx.Graph()
        self.P2graph = nx.Graph()
        # Variable to indicate to get_state_function if is has to update self.state first
        self.can_use_cache = True

    def build_board(self, state: str) -> [[int]]:
        """
        Build and return a board as a 2d-array numpy array
        :param state: str of board
        :return: 2d np array
        """
        board = []
        for i in range(self.board_size):
            board.append([])
            for j in range(self.board_size):
                board[i].append(int(state[i * self.board_size + j]))
        return np.array(board)

    def get_state(self) -> str:
        return self.state

    @staticmethod
    def extract_state(state: str) -> (str, str):
        return state.split(":")

    def get_extracted_state(self) -> (str, str):
        return StateManager.extract_state(self.get_state())

    def set_state_manager(self, state: str) -> None:
        """
        Sets the state manager to the given state building the networks for both players for computing end state.
        Sets the state and board variable of the object to the new state
        :param state: state to set the state manager to
        """
        self.state = state
        self.board = self._get_internal_state_rep(state)[0]
        for node in list(self.P1graph.nodes):
            if self.board[node[0]][node[1]] == 0:
                self.P1graph.remove_node(node)
        for node in list(self.P2graph.nodes):
            if self.board[node[0]][node[1]] == 0:
                self.P2graph.remove_node(node)

    def check_and_extract_action_string(self, action: str) -> (int, int, int):
        """
        Checks that the incoming string is on the correct format and within limits of the board
        :param action: action string
        :return: x_pos, y_pos, player
        """
        position, player = action.split(":")
        str_board, state_player = self.get_extracted_state()
        if player != state_player:
            raise ValueError(f"Input action performed by {player}, but current player is {state_player}")
        x_pos, y_pos = [int(str_index) for str_index in position.split(",")]
        if not self.filter_positions((x_pos, y_pos)):
            raise ValueError(f"Given action position ({x_pos},{y_pos}) is outside the board")
        return x_pos, y_pos, int(player)

    def get_player_graph(self, player: int):
        if player == 1:
            return self.P1graph
        else:
            return self.P2graph

    def perform_action(self, action: str) -> None:
        """
        Performs the given action changing the current state of the state manager
        :param action: action on the form ´x_pos,y_pos:player_id´
        """
        x_pos, y_pos, player = self.check_and_extract_action_string(action)
        # Set action position to player id
        self.board[x_pos, y_pos] = player
        self.update_string_state(StateManager.get_opposite_player(player))
        # Add new node to player piece graph
        player_graph = self.get_player_graph(player)
        player_graph.add_node(action)
        # Add neighbor nodes of same player to player graph
        for neighbor in self.get_same_player_neighbors((x_pos, y_pos), player):
            neighbor_node_action_string = f"{neighbor[0]},{neighbor[1]}:{player}"
            neighbor_node = player_graph.nodes[neighbor_node_action_string]
            player_graph.add_edge(neighbor_node, action)

    def update_string_state(self, player: str):
        """
        Syncs the string state with the board state
        :param player: player id of current player
        """
        self.state = ""
        for row in self.board:
            for cell in row:
                self.state += str(cell)
        self.state = f"{self.state}:{player}"

    def get_same_player_neighbors(self, position: tuple, player: int) -> [tuple]:
        """
        Gets the neighbor cells of the given player
        :param position:
        :param player:
        :return:
        """
        neighbors = self.get_neighbors_indices(position)
        return list(filter(lambda x: self.board[x[0]][x[1]] == player, neighbors))

    def get_neighbors_indices(self, position) -> [tuple]:
        """
        Gets all the neighbors for the given position of the board
        :param position: (x_index: int, y_index: int)
        :return: list of cell neighbors
        """
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

        # Perhaps first check if player one is present in all rows or player 2 is present in all columns -> decr run time
        if self.state[-1] == "1":
            # Check if player 2 won with the last move
            for row1 in range(self.board_size):
                if self.board[row1][0] == 2:
                    for row2 in range(self.board_size):
                        if self.board[row2][self.board_size - 1] == 2:
                            if nx.has_path(
                                self.P2graph, (row1, 0), (row2, self.board_size - 1)
                            ):
                                return True
        else:
            # Check if player 1 won with the last move
            for col1 in range(self.board_size):
                if self.board[0][col1] == 1:
                    for col2 in range(self.board_size):
                        if self.board[self.board_size - 1][col2] == 1:
                            if nx.has_path(
                                self.P1graph, (0, col1), (self.board_size - 1, col2)
                            ):
                                return True
        return False

    def pretty_state_string(self) -> str:
        return "\n" + "\n".join(
            ["".join(["{:2}".format(item) for item in row]) for row in self.board]
        )

    def get_move_string(self, prev_state: str, state: str) -> str:
        for i in range(len(state[:-2])):
            row = math.floor(i / self.board_size)
            if state[i] != prev_state[i]:
                col = i % self.board_size
                cell = (row, col)
        return f"place at cell {cell}"

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

    def get_action(self, current_state: str, previous_state: str):
        """
        :param current_state: current state as a string
        :param previous_state: previous state as a string
        :return: the position of the placed piece and the
            player who did it as a string on the form : ´x_pos,y_pos:player_id´
        """
        current_board = current_state[:-2]
        previous_board = previous_state[:-2]
        change_indices = [
            i
            for i in range(len(current_board))
            if current_board[i] != previous_board[i]
        ]
        if len(change_indices) != 1:
            raise ValueError(
                f"Number of changed piece locations are not 1, but {len(change_indices)}"
            )
        change_index = change_indices[0]
        x_pos, y_pos = (
            change_index % self.board_size,
            math.floor(change_index / self.board_size),
        )
        played_by_player = int(previous_state[-1])
        return f"{x_pos},{y_pos}:{played_by_player}"

    @staticmethod
    def get_opposite_player(player: int) -> str:
        if 0 < player < 3:
            return "1" if player == 2 else "2"
        else:
            raise ValueError(
                f"Input player not 1 or 2, input player: {player}."
            )

    @staticmethod
    def get_next_state_from_distribution_position(index: int, state: str):
        """
        After getting the distribution from the network we use this method to find the
        child state from the changed position. Use the previous state and input index to
        return the correct child state.
        :param index: 1d index of the position of the move to be made
        :param state: the state before this action
        :return: the child state after insertion into index
        """
        board, player = state.split(":")
        opposite_player = StateManager.get_opposite_player(player)
        output_state = ""
        for board_index, cell_value in enumerate(board):
            if board_index == index:
                output_state += player
            else:
                output_state += cell_value
        return f"{output_state}:{opposite_player}"

    @staticmethod
    def extract_board_and_player_from_state(state: str) -> (str, str):
        return state.split(":")

    @staticmethod
    def index_cell_is_occupied(index: int, state: str) -> bool:
        return state[index] == "1" or state[index] == "2"
