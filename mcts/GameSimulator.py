from mcts.StateManager import Nim, Lodge
from mcts.MCTS import MCTS


class GameSimulator:
    NIM = "NIM"
    LEDGE = "LEDGE"

    def __init__(self, g, p, m, game, n, k, b_init: ([int], bool)):
        self.g = g
        self.p = p
        self.m = m
        if game == GameSimulator.NIM:
            self.state_manager = Nim
            self.init_state = self.state_manager.init_game_state(N=n, K=k, P=p)
        if game == GameSimulator.LEDGE:
            self.b_init = b_init
            self.state_manager = Lodge
            self.init_state = self.state_manager.init_game_state(B_init=self.b_init, p=self.p)

    def run(self):
        for i in range(1, self.g + 1):
            print(f"game {i}")
            print(f"init board:       {self.init_state}")
            state = (self.init_state[0].copy(), self.init_state[1])  # copy state
            mcts = MCTS(state, self.state_manager)  # should we add option to keep relevant part of three?
            while not self.state_manager.is_end_state(state):
                state = mcts.run(self.m)
                mcts.root_state = state
                print(f"chosen new state: {state}")

            if state[1]:
                print('winner: player 1')
            else:
                print('winner: player 2')
