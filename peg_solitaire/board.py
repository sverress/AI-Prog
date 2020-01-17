from abc import ABC, abstractmethod
import math


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

    def get_neighbors(self, position: tuple, board_size):
        """
        Gets all the neighbors for the given position of the board
        :param position: (x_index: int, y_index: int)
        :return: list of cell neighbors
        """
        # Removing indices outside board
        filtered_indices = filter(lambda pos: pos[0] >= 0 and pos[1] >= 0 and pos[0] < board_size and pos[1] < board_size, self.get_neighbors_indices(position, board_size))
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
        for i in range(board_size):
            self.board.append([])
            for j in range(board_size):
                self.board[i].append(1)
        #temproary way of testing different states
        self.board[math.floor((board_size-1)/2)][math.floor((board_size-1)/2)] = 0
        self.board[board_size - 1][board_size - 1] = 0
        self.board[board_size - 3][board_size - 1] = 0
        self.board[3][0] = 0

    def get_neighbors_indices(self, position, board_size):
        r, c = position
        indices = [(r-1, c), (r-1, c+1), (r, c-1), (r, c+1), (r+1, c-1), (r+1, c)]
        # Removing indices outside the board
        filtered_indices = filter(lambda pos: pos[0] >= 0 and pos[1] >= 0 and pos[0] < board_size and pos[1] < board_size, indices)
        return list(filtered_indices)

    def get_state(self):
        return [item for sublist in self.board for item in sublist]

    def get_legal_actions(self, board_size):
        actions = []
        for row, valueR in enumerate(self.board):
            for col, valueC in enumerate(valueR):
                if valueC == 0:
                    indicesN = self.get_neighbors_indices((row,col), board_size)
                    for index, valueN in enumerate(self.get_neighbors((row, col), board_size)):
                        if valueN == 1:
                            indexN = indicesN[index]
                            indexNN = (indexN[0] - row + indexN[0], indexN[1] - col + indexN[1])
                            if indexNN[0] < 0 or indexNN[1] < 0 or indexNN[0] >= board_size or indexNN[1] >= board_size:
                                continue
                            if self.board[indexNN[0]][indexNN[1]] == 1:
                                actions.append([indexNN[0], indexNN[1], row, col])
        return actions


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

board_size = 6
board = Diamond(board_size)
print(board)
print(board.get_state())
print(board.get_legal_actions(board_size))
