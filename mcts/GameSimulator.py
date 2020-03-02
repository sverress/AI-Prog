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
        number_of_wins = 0
        for i in range(1, self.g + 1):
            print(f"game {i}")
            print(f"init board:       {self.init_state}")
            state = (self.init_state[0].copy(), self.init_state[1])  # copy state
            mcts = MCTS(state, self.state_manager)
            while not self.state_manager.is_end_state(state):
                state = mcts.run(self.m)
                mcts.print_graph()
                mcts.root_state = state
                mcts.cut_tree_at_state(state)
                print(f"chosen new state: {state}")
            if state[1]:
                print('winner: player 1')
                number_of_wins += 1
            else:
                print('winner: player 2')
        print('------------- SUMMARY -------------')
        print(f'Player 1 wins {number_of_wins} games out of {self.g}. ({round((number_of_wins/self.g)*100)}%)')
