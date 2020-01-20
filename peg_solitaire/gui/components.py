from p5 import *

class Node:
    """
    Class for representing a node/cell in the interface
    """
    def __init__(self, pos, x, y, is_occupied=True):
        """
        Initializing the new node
        :param x: x-coordinate (int)
        :param y: y-coordinate (int)
        :param is_occupied: True if the cell contains a peg
        """
        self.pos = pos
        self.x = x
        self.y = y
        self.size = 50
        self.is_occupied = is_occupied

    def set_value(self, value):
        """
        Sets the value of a node
        :param value: 0 for empty 1 for filled
        """
        self.is_occupied = value

    def draw(self):
        """
        Function to draw a single node.
        """
        # Color of stroke
        stroke(100)
        # Setting thickness of stroke
        stroke_weight(3)
        # If the node is empty don't fill it, otherwise do
        if self.is_occupied:
            fill(150)
        else:
            no_fill()
        # Make x and y the center of the circle
        ellipse_mode(CENTER)
        # Draw circle
        ellipse((self.x, self.y), self.size, self.size)
        fill(0)
        text(f"{self.pos}", (self.x-15, self.y-5))


