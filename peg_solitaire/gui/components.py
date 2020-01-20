from p5 import *


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 50

    def draw(self):
        stroke(0)
        fill(150)
        ellipse_mode(CENTER)
        ellipse((self.x, self.y), self.size, self.size)
