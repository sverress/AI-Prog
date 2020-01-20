from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.vector import Vector
from kivy.graphics.vertex_instructions import (Rectangle,
                                               Ellipse,
                                               Line)
from kivy.graphics.context_instructions import Color, PushMatrix, PopMatrix, Rotate
from kivy.core.window import Window


GRID_SIZE = 3
CENTER = GRID_SIZE*2*100
SIZE = GRID_SIZE*100


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = SIZE/2

    def draw(self):
        Color(1, 0, 0, 1)
        Ellipse(pos=(self.x, self.y), size=(self.size, self.size))


class PegSolitaire(Widget):
    def __init__(self, **kwargs):
        super(PegSolitaire, self).__init__(**kwargs)
        cells = []
        start = CENTER-SIZE*GRID_SIZE/2
        for i in range(0, GRID_SIZE):
            for j in range(0, GRID_SIZE):
                cells.append(Cell(start+i*SIZE, start+j*SIZE))
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=45, origin=(CENTER, CENTER))
            for cell in cells:
                cell.draw()
        with self.canvas.after:
            PopMatrix()



class PegSolitaireApp(App):

    def build(self):
        Window.size = (CENTER, CENTER)
        return PegSolitaire()


if __name__ == '__main__':
    PegSolitaireApp().run()
