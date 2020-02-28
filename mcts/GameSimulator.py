from mcts.StateManager import Nim, Lodge
from mcts.MCTS import MCTS


class GameSimulator:
    def __init__(self, g, p, m, n, k, b_init: ([int], bool)):
        self.G = g
        self.P = p
        self.M = m
        self.N = n
        self.K = k
        self.B_init = b_init
        if not b_init:  # Is Nim
            self.state_manager = Nim
        else:  # Is ledge
            self.state_manager = Lodge

    def run(self):
        for i in range(1, self.G+1):
            state = self.state_manager.init_game_state(B_init=self.B_init)
            mcts = MCTS(state, self.state_manager)
            state = mcts.run()