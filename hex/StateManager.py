import networkx as nx
import math
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

    def __str__(self) -> str:
        """
        Docstring for StateManager Class
        :return:
        """
        return self.pretty_state_string()

    @staticmethod
    def get_player(state: str) -> int:
        """
        :param state: string representation of state
        :return: the player taking the next move from input state
        """
        return int(state[-1])

    def current_player(self) -> int:
        """
        :return: The the current player from the state as an integer
        """
        return StateManager.get_player(self.state)

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
        """
        :return: the string representation of the board and current player
        """
        return self.state

    @staticmethod
    def extract_state(state: str) -> (str, str):
        """
        Separate the board from the current player
        :param state: the string representation of the state
        :return: a tuple: (`string representation of the board`, `player string`)
        """
        return state.split(":")

    def get_extracted_state(self) -> (str, str):
        """
        Uses the extract state method on the current state to separate the board from the current player
        :return: a tuple: (`string representation of the current board`, `current player string`)
        """
        return StateManager.extract_state(self.get_state())

    def set_state_manager(self, state: str) -> None:
        """
        Sets the state manager to the given state building the networks for both players for computing end state.
        Sets the state and board variable of the object to the new state
        :param state: state to set the state manager to
        """
        if state == self.get_state():
            return
        # Setting both of the representations of the board
        self.state = state
        self.board = self.build_board(state)

        # Connect graph for both players
        for row_index, row in enumerate(self.board):
            for column_index, player_in_cell in enumerate(row):
                if player_in_cell == 0:
                    continue
                self.perform_action(
                    f"{row_index},{column_index}:{player_in_cell}",
                    only_graph_operations=True,
                )

    def check_and_extract_action_string(
        self, action: str, check_player_turn=True
    ) -> (int, int, int):
        """
        Checks that the incoming string is on the correct format and within limits of the board
        :param action: action string
        :param check_player_turn: boolean to indicate if we should check that the action comes from correct player
        :return: x_pos, y_pos, player
        """
        position, player = action.split(":")
        str_board, state_player = self.get_extracted_state()
        if check_player_turn and player != state_player:
            raise ValueError(
                f"Input action performed by {player}, but current player is {state_player}"
            )
        x_pos, y_pos = [int(str_index) for str_index in position.split(",")]
        if not self.filter_positions((x_pos, y_pos)):
            raise ValueError(
                f"Given action position ({x_pos},{y_pos}) is outside the board"
            )
        return x_pos, y_pos, int(player)

    def get_player_graph(self, player: int) -> nx.Graph:
        """
        Uses a dict as a switch to return the graph of the input player
        :param player: player id to find correct graph
        :return: graph of the input player. None if there is no graph for input player
        """
        return {1: self.P1graph, 2: self.P2graph}.get(player, None)

    def perform_action(self, action: str, only_graph_operations=False) -> None:
        """
        Performs the given action changing the current state of the state manager, and updating the graph for the player
        who did the action
        :param action: action on the form ´x_pos,y_pos:player_id´
        :param only_graph_operations: boolean to indicate if only player graphs should be updated.
        """
        x_pos, y_pos, player = self.check_and_extract_action_string(
            action, check_player_turn=(not only_graph_operations)
        )
        if not only_graph_operations:
            # Set action position to player id
            self.board[x_pos, y_pos] = player
            self.update_string_state(StateManager.get_opposite_player(player))
        # Add new node to player piece graph
        player_graph = self.get_player_graph(player)
        player_graph.add_node(action)
        # Add neighbor nodes of same player to player graph
        for neighbor in self.get_same_player_neighbors((x_pos, y_pos), player):
            neighbor_node_action_string = f"{neighbor[0]},{neighbor[1]}:{player}"
            player_graph.add_edge(neighbor_node_action_string, action)

    def update_string_state(self, player: int) -> None:
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
        Gets the neighbor cells of the given position, filtering out the cells occupied with the opposite player.
        :param position: the posistion on the board for the cell to find neighbors for
        :param player: the player id to filter out opposite player pieces
        :return: list of positions ex: `[(1,3), (5,2), ...]`
        """
        neighbors = self.get_neighbors_indices(position)
        return list(filter(lambda x: self.board[x[0]][x[1]] == player, neighbors))

    def get_neighbors_indices(self, position) -> [tuple]:
        """
        Gets all the neighbors for the given position of the board, filtering out those outside the board.
        :param position: (x_index: int, y_index: int)
        :return: list of cell neighbors positions ex: `[(1,3), (5,2), ...]`
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

    def generate_possible_actions(self, state: str) -> [str]:
        """
        Generates all possible actions from input state by going over
         all the cells in the board adding those who are not occupied
        :param state: string representation of the board
        :return: list of possible actions ex: `["1,3:2", "1,4:2", "3,6:2", ...]`
        """
        output = []
        board, player = StateManager.extract_state(state)
        for index, cell_value in enumerate(board):
            if cell_value == "0":
                x_pos, y_pos = (
                    math.floor(index / self.board_size),
                    index % self.board_size,
                )
                output.append(f"{x_pos},{y_pos}:{player}")
        return output

    @staticmethod
    def generate_child_states(state: str) -> [str]:
        """
        Takes in a parent state and returns the child states from this state.
        Goes through all the cells in the board and checks if they are occupied.
        Returns a new state for every open cell.
        :param state: string representing state of game
        :return: list of strings representing child states
        """
        children = []
        board, player = StateManager.extract_state(state)
        next_player = StateManager.get_opposite_player(int(player))
        for index, cell_value in enumerate(board):
            if cell_value == "0":
                children.append(
                    f"{board[:index]}{player}{board[index+1:]}:{next_player}"
                )
        return children

    def get_player_sides(self, player: int) -> ([str], [str]):
        """
        Returns the player nodes (action strings) at each end of the board where the players have to connect a path.
         Using dict as switch.
        :param player: the player to get the nodes for
        :return: a tuple with the lists of nodes for the two sides
        ex: `(["0,3:2", "0,4:2", "0,6:2", ...], ["7,3:2", "7,4:2", "7,6:2", ...])`
        """
        return {
            1: (
                [
                    f"{0},{i}:{player}"
                    for i in range(self.board_size)
                    if self.board[0][i] == player
                ],
                [
                    f"{self.board_size-1},{i}:{player}"
                    for i in range(self.board_size)
                    if self.board[self.board_size - 1][i] == player
                ],
            ),
            2: (
                [
                    f"{i},{0}:{player}"
                    for i in range(self.board_size)
                    if self.board[i][0] == player
                ],
                [
                    f"{i},{self.board_size-1}:{player}"
                    for i in range(self.board_size)
                    if self.board[i][self.board_size - 1] == player
                ],
            ),
        }.get(player, None)

    def is_end_state(self) -> bool:
        """
        Checks if the opposite player of the current states player has a path between his sides of the board
        :return: a boolean stating if the current state is end state
        """
        player = StateManager.get_opposite_player(self.current_player())
        # Get the two sides the player needs to connect a path between
        first, second = self.get_player_sides(player)
        player_graph = self.get_player_graph(player)
        # Check if there is a path between the two sides
        for start in first:
            for finish in second:
                if nx.has_path(player_graph, start, finish):
                    return True
        return False

    def pretty_state_string(self) -> str:
        """
        :return: nice looking string showing the board for console
        """
        return "\n" + "\n".join(
            ["".join(["{:2}".format(item) for item in row]) for row in self.board]
        )

    def get_action(self, current_state: str, next_state: str,) -> str:
        """
        :param next_state: current state as a string
        :param current_state: previous state as a string
        :return: the position of the placed piece and the
            player who did it as a string on the form : ´x_pos,y_pos:player_id´
        """
        current_board = next_state[:-2]
        previous_board = current_state[:-2]
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
        x_pos, y_pos = self.convert_flattened_index_to_cords(change_index)
        played_by_player = int(current_state[-1])
        return f"{x_pos},{y_pos}:{played_by_player}"

    def convert_flattened_index_to_cords(self, index: int) -> (int, int):
        return (
            math.floor(index / self.board_size),
            index % self.board_size,
        )

    def check_difference_and_perform_action(self, next_state: str) -> None:
        """
        Can only be used if the incoming state is one action away from the current state of the state manager.
        Takes in the state, checks where the difference is from the current state, creates a state from that
        difference and performs that action.
        :param next_state: next state
        """
        self.perform_action(self.get_action(self.get_state(), next_state))

    @staticmethod
    def get_opposite_player(player: int) -> int:
        """
        Takes in a player and returns the next player
        :param player: player id
        :return: opposite player id
        """
        if 0 < player < 3:
            return 1 if player == 2 else 2
        else:
            raise ValueError(f"Input player not 1 or 2, input player: {player}.")

    def get_action_from_flattened_board_index(self, index: int, state: str) -> str:
        """
        After getting the distribution from the network we use this method to find the
        action from the changed position. Use the previous state and input index to
        return the correct action.
        :param index: 1d index of the position of the move to be made
        :param state: the state before this action
        :return: the child state after insertion into index
        """
        board, player = StateManager.extract_state(state)
        x_pos, y_pos = self.convert_flattened_index_to_cords(index)
        return f"{x_pos},{y_pos}:{player}"

    @staticmethod
    def index_cell_is_occupied(index: int, state: str) -> bool:
        """
        Check if the input index of the string representation
         of the board contains a piece from either of the players
        :param index: index of string representation of board
        :param state: string represnetation of the board
        :return: true if it is occupied, false otherwise
        """
        return state[index] == "1" or state[index] == "2"
