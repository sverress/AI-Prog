from tkinter import *
import math
import numpy as np
import random

from hex.StateManager import StateManager
from hex.ANET import ANET

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
    def __init__(
        self,
        board_size,
        player1=None,
        player2=None,
        starting_player=1,
        random_play=False,
        frame_rate=1000,
        initial_state=None,
        cartesian_cords=True,
    ):
        # Game logic
        self.board_size = board_size
        self.initial_state = initial_state
        self.state_manager = StateManager(board_size, starting_player)
        if initial_state:
            self.state_manager.set_state_manager(initial_state)
        self.random_play = random_play

        # Setting players
        self.player1 = player1
        self.player2 = player2

        # WINDOW
        self.master = Tk()
        self.master.title("HexGameVisualizer")
        self.master.protocol("WM_DELETE_WINDOW", self.quit_application)

        self.action_input = Entry(self.master)
        self.action_input.bind("<Return>", lambda event: self.button_clicked())
        self.action_input.pack()

        self.perform_action_button = Button(
            self.master, text="perform move", command=self.button_clicked
        )
        self.perform_action_button.pack()

        # TODO: Add label to describe the players currently playing
        self.label = Label(self.master)
        self.label.pack()

        self.start_pos = (60, 30)
        self.canvas = Canvas(
            self.master,
            width=self.start_pos[0] + self.board_size * 55 + self.start_pos[0],
            height=self.start_pos[1] + self.board_size * 33 + self.start_pos[1],
        )
        self.canvas.pack()

        # CONSTANTS
        self.frame_rate = frame_rate
        self.border_size = 10
        self.counter = 0
        self.size = 20
        self.cartesian_cords = cartesian_cords

        # LISTS CONTROLLING GAME AND DRAWING OF BOARD
        self.board = []
        self.board_border = []
        self.actions = []
        self.player_pieces = []

    def quit_application(self):
        import sys

        self.master.quit()
        sys.exit()

    def add_action(self, action: str):
        self.actions.append(action)

    def preprocess_actions(self):
        new_actions = []
        for action in self.actions:
            new_actions.append(GameVisualizer.preprocess_action(action))
        return new_actions

    @staticmethod
    def preprocess_action(action: str):
        positions, player = action.split(":")
        x_pos, y_pos = positions.split(",")
        return int(x_pos), int(y_pos), int(player)

    def run(self):
        self.actions = self.preprocess_actions()
        self.build_and_draw_board()
        if self.initial_state:
            self.state_manager.set_state_manager(self.initial_state)
            self.draw_initial_state()
        if len(self.actions):
            self.master.after(self.frame_rate, self.draw)
        mainloop()

    def model_perform_action(self, model: ANET):
        print(self.state_manager.get_state())
        distribution = model.predict(self.state_manager.get_state())
        print(distribution)
        argmax_distribution_index = int(
            np.argmax(distribution)
        )  # Greedy best from distribution
        action = self.state_manager.get_action_from_flattened_board_index(
            argmax_distribution_index, self.state_manager.get_state()
        )
        self.perform_action(GameVisualizer.preprocess_action(action))

    def button_clicked(self):
        if self.state_manager.is_end_state():
            return
        try:
            current_player = self.player1 if self.state_manager.current_player() == 1 else self.player2
            if current_player:
                self.model_perform_action(current_player)
            else:
                input_action = (
                    f"{self.action_input.get()}:{self.state_manager.current_player()}"
                )
                if self.random_play:
                    input_action = random.choice(
                        self.state_manager.generate_possible_actions(
                            self.state_manager.get_state()
                        )
                    )
                self.perform_action(GameVisualizer.preprocess_action(input_action))
            self.action_input.delete(0, "end")
        except ValueError:
            self.label["text"] = "Something went wrong"
        if self.state_manager.is_end_state():
            self.label["text"] = "Game over"

    def draw_initial_state(self):
        initial_board = self.state_manager.build_board(self.initial_state)
        for row_index, row in enumerate(initial_board):
            for col_index, player in enumerate(row):
                if player:
                    self.player_pieces.append(
                        Cell(
                            self.canvas,
                            self.board[row_index][col_index].top,
                            player=player,
                        )
                    )

    def get_canvas_position(self, position: (int, int)) -> (int, int):
        x, y = self.start_pos
        x += self.size * 2 * position[1] + self.size * position[0]
        y += (self.size + self.size / 1.7) * position[0]
        return x, y

    def build_and_draw_board(self):
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                row.append(
                    Cell(
                        self.canvas,
                        self.get_canvas_position((i, j)),
                        draw_on_init=False,
                    )
                )
            self.board.append(row)
        self.draw_board_border()
        for row_index, row in enumerate(self.board):
            for col_index, cell in enumerate(row):
                self.board[row_index][col_index].draw()

    def get_column(self, target_col_index: int):
        column = []
        for row_index, row in enumerate(self.board):
            for col_index, cell in enumerate(row):
                if target_col_index == col_index:
                    column.append(cell)
        return column

    def draw_board_border(self):
        borders = []
        first_row = self.board[0]
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
        first_column = self.get_column(0)
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
        last_row = self.board[-1]
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
        last_column = self.get_column(self.board_size - 1)
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
        return self.board_size * pos[0] + pos[1]

    def get_cords(self, board_pos: int):
        return math.floor(board_pos / self.board_size), board_pos % self.board_size

    def draw(self):
        self.perform_action(self.actions.pop(0))
        if len(self.actions) > 0:
            self.master.after(self.frame_rate, self.draw)

    def perform_action(self, action: (int, int, int)):
        print(action)
        x_pos, y_pos, player = action
        self.player_pieces.append(
            Cell(self.canvas, self.board[x_pos][y_pos].top, player=player,)
        )
        self.state_manager.perform_action(f"{x_pos},{y_pos}:{player}")


class Cell:
    def __init__(
        self,
        canvas,
        pos: tuple,
        player=None,
        size=20,
        draw_on_init=True,
        divide_parameter=1.7,
    ):
        # Player colors
        if player is not None:
            # Player one is blue. Player 2 red.
            self.color = PLAYER_ONE_COLOR if player == 1 else PLAYER_TWO_COLOR
        else:
            self.color = BOARD_COLOR

        self.canvas = canvas

        # Constants
        self.size = size
        self.divide_by = divide_parameter

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