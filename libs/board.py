from abc import ABC, abstractmethod


class Board(ABC):
    """
    Abstract Board class for a general board
    """

    def __init__(self, board_size: int):
        """
        Initializes the board
        :param board_size: Size of the board
        :param open_coordinates: list of positions to be left open in the board. Positions are given as tuples
        """
        self.board = []
        self.board_size = board_size
        self.build_board(board_size)

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
        return "".join(temp)

    def filter_positions(self, position: tuple):
        """
        Standard filters for all position tuples in board class
        :param position: (x_index: int, y_index: int)
        :return: boolean describing if the position is within the board size
        """
        x, y = position
        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def set_cell(self, position: tuple, value: int):
        """
        Set presence or absence of peg in a cell
        :param position: (x_index: int, y_index: int)
        :param value: 0 or 1
        """
        self.board[position[0]][position[1]] = value

    def get_num_tiles(self):
        """
        :return: number of tiles of the board: int
        """
        count = 0
        for listElem in self.board:
            count += len(listElem)
        return count

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
