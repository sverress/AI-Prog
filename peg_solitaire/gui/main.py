import copy
from p5 import *
from peg_solitaire.gui.components import *
from peg_solitaire.agent import Agent


def setup():
    # Setting size of screen
    size(600, 600)
    # Start position of nodes to center properly
    start = -(SIZE-1)*SPACE/2
    for i in range(0, SIZE):
        row = []
        j_limit = SIZE
        if agent.board_type == "triangle":
            j_limit = i + 1
        for j in range(0, j_limit):
            # Creating nodes and adding space between them
            row.append(Node((i, j), start + j * SPACE, start + i * SPACE, is_occupied=agent.init_board.get_cell((i, j)) == 1))
        nodes.append(row)


def board_changed():
    action = agent.actor.choose_action_epsilon(agent.board)
    agent.board.do_action(action)
    for entering_node in action.get_entering_positions():
        nodes[entering_node[0]][entering_node[1]].set_value(True)
    for leaving_node in action.get_leaving_positions():
        nodes[leaving_node[0]][leaving_node[1]].set_value(False)


def draw():
    # Setting background color
    background(255)
    # Setting new reference point for drawing
    translate(width/2, height/2)
    if agent.board_type == "diamond":
        # Rotating around the new reference point
        rotate(PI/4)
    for row in nodes:
        for node in row:
            # Drawing all the nodes
            node.draw()


def refresh():
    agent.board = copy.deepcopy(agent.init_board)
    for row in nodes:
        for node in row:
            node.set_value(agent.board.get_cell(node.pos))


def key_pressed():
    if key == " ":
        board_changed()
    if key == "r":
        refresh()


if __name__ == '__main__':
    agent = Agent.create_agent_from_config_file("../config.json")
    agent.train(plot_result=False)
    # List of all nodes
    nodes = []
    # Distance between nodes
    SPACE = 80
    # Size of board
    SIZE = agent.board_size
    board = copy.deepcopy(agent.init_board)
    run()
