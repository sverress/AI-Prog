from tkinter import *
import math
from hex.StateManager import StateManager

# COLORS
PLAYER_ONE_COLOR = "#3232ff"  # Blue
PLAYER_TWO_COLOR = "#ff3333"  # Red
BOARD_COLOR = "#D3D3D3"  # Light Gray
BOARD_OUTLINE_COLOR = "#000"  # Black

# FONT SETTINGS
FONT = "Arial"
FONT_SIZE = 10
FONT_COLOR = "#FFF"


class GameVisualizer:
    def __init__(self, k, frame_rate=1000, initial_state=None, cartesian_cords=False):
        self.k = k
        self.frame_rate = frame_rate
        self.initial_state_given = initial_state is not None
        self.initial_state = initial_state
        self.master = Tk()
        self.master.title("HexGameVisualizer")
        self.start_pos = (60, 30)

        self.canvas = Canvas(
            self.master,
            width=self.start_pos[0] + self.k * 55 + self.start_pos[0],
            height=self.start_pos[1] + self.k * 33 + self.start_pos[1],
        )
        self.canvas.pack()
        self.counter = 0
        self.board = []
        self.board_border = []
        self.border_size = 10
        self.size = 20
        self.actions = []
        self.player_pieces = []
        self.cartesian_cords = cartesian_cords

    def add_action(self, action: str):
        self.actions.append(action)

    def preprocess_actions(self):
        new_actions = []
        for action in self.actions:
            positions, player = action.split(":")
            x_pos, y_pos = positions.split(",")
            # row and col are opposite of state manager
            new_actions.append((int(y_pos), int(x_pos), int(player)))
        return new_actions

    def run(self):
        self.actions = self.preprocess_actions()
        self.build_and_draw_board()
        if self.initial_state_given:
            self.draw_initial_state()
        if len(self.actions):
            self.master.after(self.frame_rate, self.draw)
        mainloop()

    def draw_initial_state(self):
        initial_board = self.initial_state[:-2]
        for i, char in enumerate(initial_board):
            new_piece_pos = (
                i % self.k,
                math.floor(i / self.k),
            )
            player = int(char)
            if player:
                self.player_pieces.append(
                    Cell(
                        self.canvas,
                        self.board[self.get_board_pos(new_piece_pos)].top,
                        player=player,
                    )
                )

    def build_and_draw_board(self):
        starting_x, starting_y = self.start_pos
        for i in range(self.k):
            cell = Cell(
                self.canvas, (starting_x + i * 40, starting_y), draw_on_init=False,
            )
            self.board.append(cell)
            for j in range(self.k - 1):
                cell = Cell(self.canvas, cell.right2, draw_on_init=False)
                self.board.append(cell)
        [
            cell.set_cords(self.get_cords(board_pos))
            for board_pos, cell in enumerate(self.board)
        ]  # Set cartesian cords for cells
        self.board_border = self.draw_board_border()
        [cell.draw() for cell in self.board]  # Draw all board cells

    def draw_board_border(self):
        borders = []
        first_row = [self.board[self.get_board_pos((i, 0))] for i in range(self.k)]
        borders.append(
            self.canvas.create_polygon(
                first_row[0].left1[0],
                first_row[0].left1[1],
                first_row[0].left1[0] - self.border_size,
                first_row[0].left1[1] - self.border_size,
                first_row[0].left1[0],
                first_row[0].left1[1] - 2 * self.border_size,
                first_row[-1].top[0] + 2 * self.border_size,
                first_row[-1].right1[1] - 2 * self.border_size,
                first_row[-1].top[0],
                (first_row[-1].right1[1] + first_row[-1].right2[1]) / 2,
                fill=PLAYER_ONE_COLOR,
            )
        )
        [
            borders.append(
                self.canvas.create_text(
                    cell.top[0] - 1.5 * self.border_size,
                    cell.top[1],
                    text=str(i) if self.cartesian_cords else chr(65 + i),
                    fill=FONT_COLOR,
                    font=(FONT, FONT_SIZE),
                )
            )
            for i, cell in enumerate(first_row)
        ]
        first_column = [self.board[self.get_board_pos((0, i))] for i in range(self.k)]
        borders.append(
            self.canvas.create_polygon(
                first_column[0].left1[0],
                first_column[0].left1[1],
                first_column[0].left1[0] - self.border_size,
                first_column[0].left1[1] - self.border_size,
                first_column[0].left1[0] - 2 * self.border_size,
                first_column[0].left1[1],
                first_column[-1].bottom[0] - 2 * self.border_size,
                first_column[-1].left2[1] + 2 * self.border_size,
                first_column[-1].bottom[0],
                (first_column[-1].left2[1] + first_column[-1].left1[1]) / 2,
                fill=PLAYER_TWO_COLOR,
            )
        )
        [
            borders.append(
                self.canvas.create_text(
                    cell.left1[0] - self.border_size / 1.5,
                    (cell.left1[1] + cell.left2[1]) / 2,
                    text=str(i) if self.cartesian_cords else str(i + 1),
                    fill=FONT_COLOR,
                    font=(FONT, FONT_SIZE),
                )
            )
            for i, cell in enumerate(first_column)
        ]
        last_row = [
            self.board[self.get_board_pos((i, self.k - 1))] for i in range(self.k)
        ]
        borders.append(
            self.canvas.create_polygon(
                last_row[0].bottom[0],
                (last_row[0].right1[1] + last_row[0].right2[1]) / 2,
                last_row[0].bottom[0] - 2 * self.border_size,
                last_row[0].right2[1] + 2 * self.border_size,
                last_row[-1].right2[0],
                last_row[-1].right2[1] + 2 * self.border_size,
                last_row[-1].right2[0] + self.border_size,
                last_row[-1].right2[1] + self.border_size,
                last_row[-1].right2[0],
                last_row[-1].right2[1],
                fill=PLAYER_ONE_COLOR,
            )
        )
        [
            borders.append(
                self.canvas.create_text(
                    cell.bottom[0] + 1.2 * self.border_size,
                    cell.bottom[1],
                    text=str(i) if self.cartesian_cords else chr(65 + i),
                    fill=FONT_COLOR,
                    font=(FONT, FONT_SIZE),
                )
            )
            for i, cell in enumerate(last_row)
        ]
        last_column = [
            self.board[self.get_board_pos((self.k - 1, i))] for i in range(self.k)
        ]
        borders.append(
            # Bottom up
            self.canvas.create_polygon(
                last_column[-1].right2[0],
                last_column[-1].right2[1],
                last_column[-1].right2[0] + self.border_size,
                last_column[-1].right2[1] + self.border_size,
                last_column[-1].right2[0] + 2 * self.border_size,
                last_column[-1].right2[1],
                last_column[0].top[0] + 2 * self.border_size,
                last_column[0].right1[1] - 2 * self.border_size,
                last_column[0].top[0],
                (last_column[0].right1[1] + last_column[0].right2[1]) / 2,
                fill=PLAYER_TWO_COLOR,
            )
        )
        [
            borders.append(
                self.canvas.create_text(
                    cell.right1[0] + self.border_size / 1.5,
                    (cell.left1[1] + cell.left2[1]) / 2,
                    text=str(i) if self.cartesian_cords else str(i + 1),
                    fill=FONT_COLOR,
                    font=(FONT, FONT_SIZE),
                )
            )
            for i, cell in enumerate(last_column)
        ]
        return borders

    def get_board_pos(self, pos: (int, int)):
        return self.k * pos[0] + pos[1]

    def get_cords(self, board_pos: int):
        return math.floor(board_pos / self.k), board_pos % self.k

    def draw_player_cell(self, pos: (int, int), player: int):
        return Cell(self.canvas, self.board[self.get_board_pos(pos)].top, player=player)

    def draw(self):
        action = self.actions.pop(0)
        new_piece_pos = action[:-1]
        self.player_pieces.append(
            Cell(
                self.canvas,
                self.board[self.get_board_pos(new_piece_pos)].top,
                player=action[-1],
            )
        )
        if len(self.actions) > 0:
            self.master.after(self.frame_rate, self.draw)


class Cell:
    def __init__(self, canvas, pos: tuple, player=None, size=20, draw_on_init=True):
        # Player colors
        self.is_player_cell = player is not None
        if self.is_player_cell:
            # Player one is blue. Player 2 red.
            self.color = PLAYER_ONE_COLOR if player == 1 else PLAYER_TWO_COLOR
        else:
            self.color = BOARD_COLOR

        self.canvas = canvas

        # Constants
        self.size = size
        self.divide_by = 1.7

        self.object = None
        self.cords = (None, None)

        # Positions on the canvas
        self.top = pos
        self.right1 = (pos[0] + self.size, pos[1] + self.size / self.divide_by)
        self.right2 = (
            pos[0] + self.size,
            pos[1] + self.size / self.divide_by + self.size,
        )
        self.left1 = (pos[0] - self.size, pos[1] + self.size / self.divide_by)
        self.left2 = (self.left1[0], self.left1[1] + self.size)
        self.bottom = (
            self.right2[0] - self.size,
            self.right2[1] + self.size / self.divide_by,
        )

        if draw_on_init:
            self.draw()

    def set_cords(self, cords):
        self.cords = cords

    def delete(self):
        self.canvas.delete(self.object)

    def draw(self):
        x_top, y_top = self.top
        x_right1, y_right1 = self.right1
        x_right2, y_right2 = self.right2
        x_bottom, y_bottom = self.bottom
        x_left1, y_left1 = self.left1
        x_left2, y_left2 = self.left2

        self.object = self.canvas.create_polygon(
            x_top,
            y_top,
            x_right1,
            y_right1,
            x_right2,
            y_right2,
            x_bottom,
            y_bottom,
            x_left2,
            y_left2,
            x_left1,
            y_left1,
            fill=self.color,
            outline=BOARD_OUTLINE_COLOR,
        )



# EXAMPLES OF USE
def play_random_game():
    """
    Play a random game using the StateManager
     to generate new states and check if game is over
    """
    import random

    my_k = 4
    game = GameVisualizer(my_k)
    state_manager = StateManager(my_k, 1)
    while not state_manager.is_end_state():
        previous_state = state_manager.get_state()
        print(previous_state)
        possible_states = state_manager.generate_child_states(previous_state)
        current_state = random.choice(possible_states)
        taken_action = state_manager.get_action(previous_state, current_state)
        state_manager.perform_action(taken_action)
        game.add_action(taken_action)
    game.run()



def initial_state():
    initial_state = "2112102122011010211221002101022212201222122111011220021110221001:1"
    game = GameVisualizer(8, initial_state=initial_state, cartesian_cords=True)
    game.run()


def test():
    state_manager = StateManager(8, 1)
    actions = ["1,2:1", "7,3:2"]
    game = GameVisualizer(
        8, cartesian_cords=True, initial_state=state_manager.get_state()
    )
    for action in actions:
        state_manager.perform_action(action)
        game.add_action(action)
    print(state_manager.pretty_state_string())
    game.run()
