from p5 import *
from peg_solitaire.gui.components import *

nodes = []
SPACE = 80
SIZE = 4


def setup():
    size(600, 600)
    start = -(SIZE-1)*SPACE/2
    for i in range(0, SIZE):
        row = []
        for j in range(0, SIZE):
            row.append(Node(start + i * SPACE, start + j * SPACE))
        nodes.append(row)
    # Setting some node to EMPTY
    nodes[2][2].value = 0


def draw():
    background(255)
    translate(width/2, height/2)
    rotate(PI/4)
    for row in nodes:
        for node in row:
            node.draw()


if __name__ == '__main__':
    run()
