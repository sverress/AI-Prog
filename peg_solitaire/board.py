from abc import ABC, abstractmethod
import numpy as np
from peg_solitaire.action import Action


class Board(ABC):
    """
    Abstract Board class for a general board
    """
    def __init__(self, board_size: int, open_coordinates: [tuple]):
        """
        Initializes the board
        :param board_size: Size of the board
        :param open_coordinates: list of positions to be left open in the board. Positions are given as tuples
        """
        self.board = []
        self.board_size = board_size
        self.build_board(board_size)
        for coordinate in open_coordinates:
            self.board[coordinate[0]][coordinate[1]] = 0

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
        """
        Method for getting the state key (str)
        :return: state key: str
        """
        temp = [item for sublist in self.board for item in sublist]
        temp = (str(w) for w in temp)
        return ''.join(temp)

    def get_sap(self, action: Action):
        """
        Getting the state action pair key (str)
        :param action: The action object
        :return: State action pair key (str)
        """
        state = [item for sublist in self.board for item in sublist]
        state = (str(w) for w in state)
        action = action.get_action_string()
        return ''.join(state) + ''.join(action)

    def get_saps(self):
        """
        :return: List of state action pair keys for all
         legal actions from current state
        """
        return [self.get_sap(action) for action in self.get_legal_actions()]

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
        """
        Check if a state is end state by finding legal actions from state. If actions list is empty -> end state
        :return: bool
        """
        actions = self.get_legal_actions()
        if not actions:
            return True
        return False

    def set_cell(self, position: tuple, value: int):
        """
        Set presence or absence of stone in a cell
        :param position: (x_index: int, y_index: int)
        :param value: 0 or 1
        """
        self.board[position[0]][position[1]] = value

    def do_action(self, action: Action):
        for leaving_position in action.get_leaving_positions():
            self.set_cell(leaving_position, 0)
        for entering_position in action.get_entering_positions():
            self.set_cell(entering_position, 1)

    def get_reward(self):
        """
        Gets reward of a state. 0 if the state is not end state, 1/(number of stones left on board) if end state
        :return: the reward: float
        """
        if self.get_num_stones() == 1:
            return 1
        elif self.is_end_state():
            return 1 / (self.get_num_stones() ** 2)
        else:
            return 0.0

    def get_num_stones(self):
        return sum([item for sublist in self.board for item in sublist])

    @abstractmethod
    def get_neighbors_indices(self, position: tuple):
        """
        Implementation specific method for different boards.
        :param position: (x_index: int, y_index: int)
        :return: list of positions: [(x_index_1: int, y_index_1: int), (x_index_2: int, y_index_2: int), ...]
        """
        pass

    @abstractmethod
    def build_board(self, board_size):
        """
        Implementation specific method for different boards.
        :param board_size: dimension of board
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
    def build_board(self, board_size):
        for i in range(board_size):
            self.board.append([])
            for j in range(board_size):
                self.board[i].append(1)

    def get_neighbors_indices(self, position):
        r, c = position
        indices = [(r-1, c), (r-1, c+1), (r, c-1), (r, c+1), (r+1, c-1), (r+1, c)]
        # Removing indices outside the board
        return list(filter(lambda pos: self.filter_positions(pos), indices))


class Triangle(Board):
    def build_board(self, board_size):
        for i in range(board_size):
            self.board.append([])
            for j in range(i+1):
                self.board[i].append(1)

    def get_neighbors_indices(self, position):
        r, c = position
        indices = [(r-1, c-1), (r-1, c), (r, c-1), (r, c+1), (r+1, c), (r+1, c+1)]
        # Removing indices outside the board
        return list(filter(lambda pos: self.filter_positions(pos), indices))
