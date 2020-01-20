from p5 import *
from peg_solitaire.gui.components import *

# List of all nodes
nodes = []
# Distance between nodes
SPACE = 80
# Size of board
SIZE = 4


def setup():
    # Setting size of screen
    size(600, 600)
    # Start position of nodes to center properly
    start = -(SIZE-1)*SPACE/2
    for i in range(0, SIZE):
        row = []
        for j in range(0, SIZE):
            # Creating nodes and adding space between them
            row.append(Node(start + i * SPACE, start + j * SPACE))
        nodes.append(row)
    # Setting some node to EMPTY
    nodes[2][2].value = 0


def draw():
    # Setting background color
    background(255)
    # Setting new reference point for drawing
    translate(width/2, height/2)
    # Rotating around the new reference point
    rotate(PI/4)
    for row in nodes:
        for node in row:
            # Drawing all the nodes
            node.draw()


if __name__ == '__main__':
    run()
