from p5 import *
from peg_solitaire.gui.components import *

nodes = []
SPACE = 100
SIZE = 2


def setup():
    size(600, 600)
    start = -(SIZE-1)*SPACE/2
    for i in range(0, SIZE):
        for j in range(0, SIZE):
            nodes.append(Node(start + i * SPACE, start + j * SPACE))


def draw():
    background(255)
    translate(width/2, height/2)
    rotate(PI/4)
    for node in nodes:
        node.draw()



if __name__ == '__main__':
    run()
