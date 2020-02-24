from mcts.StateManager import Nim, Lodge
from mcts.MCTS import MCTS


class GameSimulator:
    def __init__(self, G, P, M, N, K, B_init):
        self.G = G
        self.P = P
        self.M = M
        self.N = N
        self.K = K
        self.B_init = B_init
        if not B_init:  # Is Nim
            self.state_manager = Nim
        else:  # Is ledge
            self.state_manager = Lodge

    def run(self, verbose=True):
        for i in range(1, self.G+1):
            state = self.state_manager.init_game_state(B_init=self.B_init)
            mcts = MCTS(state)
            while not self.state_manager.is_end_state(state):
                state = mcts.run()


game = GameSimulator(1, 1, 10, 10, 4, [0,2,1,0])
game.run()
