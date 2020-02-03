from p5 import *
from peg_solitaire.gui.components import *
from peg_solitaire.board import Diamond
import random


def setup():
    # Setting size of screen
    size(600, 600)
    # Start position of nodes to center properly
    start = -(SIZE-1)*SPACE/2
    for i in range(0, SIZE):
        row = []
        for j in range(0, SIZE):
            # Creating nodes and adding space between them
            row.append(Node((i, j), start + j * SPACE, start + i * SPACE, is_occupied=board.get_cell((i, j)) == 1))
        nodes.append(row)


def board_changed():
    action = random.choice(board.get_legal_actions())
    board.do_action(action)
    for entering_node in action.get_entering_positions():
        nodes[entering_node[0]][entering_node[1]].set_value(True)
    for leaving_node in action.get_leaving_positions():
        nodes[leaving_node[0]][leaving_node[1]].set_value(False)


def draw():
    # Setting background color
    background(255)
    # Setting new reference point for drawing
    translate(width/2, height/2)
    # Rotating around the new reference point
    rotate(PI/4)
    if key_is_pressed and key == " ":
        board_changed()
    for row in nodes:
        for node in row:
            # Drawing all the nodes
            node.draw()


if __name__ == '__main__':
    # List of all nodes
    nodes = []
    # Distance between nodes
    SPACE = 80
    # Size of board
    SIZE = 4
    board = Diamond(SIZE, [(2, 1)])
    run()
