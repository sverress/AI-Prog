from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.vector import Vector
from kivy.graphics.vertex_instructions import (Rectangle,
                                               Ellipse,
                                               Line)
from kivy.graphics.context_instructions import Color


class PegSolitaire(Widget):
    def __init__(self, **kwargs):
        super(PegSolitaire, self).__init__(**kwargs)
        with self.canvas:
            Color(1, 0, 0, 1)
            Ellipse(pos=(0, 100), size=(50, 50))
            Color(0, 1, 0, 1)
            Ellipse(pos=(100, 100), size=(50, 50))
function grant access internett

class PegSolitaireApp(App):

    def build(self):
        return PegSolitaire()


if __name__ == '__main__':
    PegSolitaireApp().run()
