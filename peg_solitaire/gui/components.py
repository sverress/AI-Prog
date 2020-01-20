from p5 import *


class Node:
    def __init__(self, x, y, value=1):
        self.x = x
        self.y = y
        self.size = 50
        self.value = value  # 0 for empty 1 for filled

    def set_value(self, value):
        self.value = value

    def draw(self):
        stroke(100)
        stroke_weight(3)
        if self.value == 0:
            no_fill()
        else:
            fill(150)
        ellipse_mode(CENTER)
        ellipse((self.x, self.y), self.size, self.size)


