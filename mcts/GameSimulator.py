from mcts.StateManager import Nim, Lodge
from mcts.MCTS import MCTS


class GameSimulator:
    def __init__(self, g, p, m, n, k, b_init: ([int], bool)):
        self.g = g
        self.p = p
        self.m = m
        self.n = n
        self.k = k
        self.b_init = b_init
        if not b_init:  # Is Nim
            self.state_manager = Nim
        else:  # Is ledge
            self.state_manager = Lodge

    def run(self):
        optimal_play = [(self.b_init, self.p)]
        for i in range(1, self.g + 1):
            state = self.state_manager.init_game_state(B_init=self.b_init, p=self.p)
            mcts = MCTS(state, self.state_manager)
            optimal_play.append(mcts.run())
        for s in optimal_play:
            print(s)