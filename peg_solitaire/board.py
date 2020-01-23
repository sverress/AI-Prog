from abc import ABC, abstractmethod
import math
import numpy as np
from peg_solitaire.action import Action


class Board(ABC):
    """
    Abstract Board class for a general board
    """
    def __init__(self, board_size: int):
        """
        Initializes the board
        :param board_size: Size of the board
        """
        self.board = []
        self.board_size = board_size

    def __str__(self):
        """
        Creates a simple toString for a board object
        :return: string representation of the board
        """
        output = ""
        for row in self.board:
            for node in row:
                output += f"{node} "
            output += "\n"
        return output

    def get_cell(self, position: tuple):
        """
        Method for getting a cell value. If the position is outside board None will be returned
        :param position: (x_index: int, y_index: int)
        :return: content of cell or None if the request is outside the board
        """
        try:
            return self.board[position[0]][position[1]]
        except IndexError:
            return None

    def get_state(self):
        temp = [item for sublist in self.board for item in sublist]
        temp = (str(w) for w in temp)
        return ''.join(temp)

    def get_SAP(self, action: Action):
        state = [item for sublist in self.board for item in sublist]
        state = (str(w) for w in state)
        action = action.get_action_string()
        return ''.join(state) + ''.join(action)

    def filter_positions(self, position: tuple):
        """
        Standard filters for all position tuples in board class
        :param position: (x_index: int, y_index: int)
        :return: boolean describing if the position is within the board size
        """
        x, y = position
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def get_neighbors(self, position: tuple):
        """
        Gets all the neighbors for the given position of the board
        :param position: (x_index: int, y_index: int)
        :return: list of cell neighbors
        """
        # Get cells and remove cells outside board (None cells)
        return list(
            filter(
                lambda cell: cell is not None,
                map(
                    lambda pos: self.get_cell(pos),
                    self.get_neighbors_indices(position)
                )
            )
        )

    def is_end_state(self):
        actions = self.get_legal_actions()
        if not actions:
            return True
        return False

    def set_cell(self, position: tuple, value: int):
        self.board[position[0]][position[1]] = value

    def do_action(self, action: Action):
        for leaving_position in action.get_leaving_positions():
            self.set_cell(leaving_position, 0)
        for entering_position in action.get_entering_positions():
            self.set_cell(entering_position, 1)

    def get_reward(self):
        num_stones = sum([item for sublist in self.board for item in sublist])
        if self.is_end_state():
            return 1/num_stones
        return 0

    @abstractmethod
    def get_neighbors_indices(self, position: tuple):
        """
        Implementation specific method for different boards.
        :param position: (x_index: int, y_index: int)
        :return: list of positions: [(x_index_1: int, y_index_1: int), (x_index_2: int, y_index_2: int), ...]
        """
        pass

    def get_legal_actions(self):
        """
        :return: a list of the legal actions from the current board state
        """
        actions = []
        for parent_x, row in enumerate(self.board):
            for parent_y, cell_value in enumerate(row):
                # cell only relevant if empty
                if cell_value == 0:
                    indices_1st_gen_children = self.get_neighbors_indices((parent_x, parent_y))
                    for indices_index, children_position in enumerate(indices_1st_gen_children):
                        # 1st gen children must be filled
                        if self.get_cell(children_position) == 1:
                            parent_position_np = np.array((parent_x, parent_y))
                            direction = np.array(children_position) - parent_position_np
                            moving_cell_position = parent_position_np + 2*direction
                            # 2st gen children must be filled
                            if self.filter_positions(tuple(moving_cell_position)) and self.get_cell(moving_cell_position) == 1:
                                actions.append(Action(tuple(moving_cell_position), children_position, (parent_x, parent_y)))
        return actions


class Diamond(Board):
    def __init__(self, board_size):
        super().__init__(board_size)
        for i in range(board_size):
            self.board.append([])
            for j in range(board_size):
                self.board[i].append(1)
        # temporary way of testing different states
        self.board[math.floor((board_size-1)/2)][math.floor((board_size-1)/2)] = 0
        self.board[board_size - 1][board_size - 1] = 0
        self.board[board_size - 3][board_size - 1] = 0
        self.board[3][0] = 0

    def get_neighbors_indices(self, position):
        r, c = position
        indices = [(r-1, c), (r-1, c+1), (r, c-1), (r, c+1), (r+1, c-1), (r+1, c)]
        # Removing indices outside the board
        return list(filter(lambda pos: self.filter_positions(pos), indices))


class Triangle(Board):
    def __init__(self, board_size):
        super().__init__(board_size)
        for i in range(board_size):
            self.board.append([])
            for j in range(i+1):
                self.board[i].append(1)

    def get_neighbors_indices(self, position):
        r, c = position
        indices = [(r-1, c-1), (r-1, c), (r, c-1), (r, c+1), (r+1, c), (r+1, c+1)]
        # Removing indices outside the board
        return list(filter(lambda pos: self.filter_positions(pos), indices))


