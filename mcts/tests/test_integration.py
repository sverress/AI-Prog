import unittest
from mcts.GameSimulator import GameSimulator


class TestIntegration(unittest.TestCase):
    def test_run_logde(self):
        self.game = GameSimulator(1, 1, 10, 10, 4, ([0, 2, 0, 1], True))
        self.game.run()

    def test_run_nim(self):

        self.game = GameSimulator(1, 1, 10, 10, 4)
        self.game.run()
