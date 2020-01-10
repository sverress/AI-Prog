from abc import ABC, abstractmethod


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
        self.initialize_board(board_size)

    @abstractmethod
    def initialize_board(self, board_size: int):
        """
        Implementation specific function to init board
        :param board_size: Size of the board
        """
        pass

    def __str__(self):
        output = ""
        for row in self.board:
            for node in row:
                output += f"{node} "
            output += "\n"
        return output

    def get_cell(self, position: tuple):
        """
        :param position: (x_index: int, y_index: int)
        :return: content of cell or None if the request is outside the board
        """
        try:
            return self.board[position[0]][position[1]]
        except IndexError:
            return None

    def get_neighbors(self, position: tuple):
        """
        Gets all the neighbors for the given position of the board
        :param position: (x_index: int, y_index: int)
        :return: list of cell neighbors
        """
        # Removing negative indices
        filtered_indices = filter(lambda pos: pos[0] >= 0 and pos[1] >= 0, self.get_neighbors_indices(position))
        # Get cells and remove cells outside board (None cells)
        cells = filter(lambda cell: cell is not None, map(lambda pos: self.get_cell(pos), filtered_indices))
        return list(cells)

    @abstractmethod
    def get_neighbors_indices(self, position: tuple):
        """
        :param position: (x_index: int, y_index: int)
        :return: list of positions: [(x_index_1: int, y_index_1: int), (x_index_2: int, y_index_2: int), ...]
        """
        pass


class Diamond(Board):
    def initialize_board(self, board_size):
        cell_index = 1
        for i in range(board_size):
            self.board.append([])
            for j in range(board_size):
                self.board[i].append(chr(64+cell_index))
                cell_index += 1

    def get_neighbors_indices(self, position):
        r, c = position
        return [(r-1, c), (r-1, c+1), (r, c-1), (r, c+1), (r+1, c-1), (r+1, c)]


class Triangle(Board):
    def initialize_board(self, board_size):
        cell_index = 1
        for i in range(board_size):
            self.board.append([])
            for j in range(i+1):
                self.board[i].append(chr(64+cell_index))
                cell_index += 1

    def get_neighbors_indices(self, position):
        r, c = position
        return [(r-1, c-1), (r-1, c), (r, c-1), (r, c+1), (r+1, c), (r+1, c+1)]


board = Diamond(4)
print(board)
print(board.get_neighbors((2, 1)))
