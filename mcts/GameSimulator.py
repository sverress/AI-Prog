from mcts.StateManager import Nim, Lodge
from mcts.MCTS import MCTS
from libs.helpers import print_loader


class GameSimulator:
    NIM = "NIM"
    LEDGE = "LEDGE"

    def __init__(self, g, p, m, game, n, k, b_init: ([int], bool), verbose, max_tree_height):
        self.g = g
        self.p = p
        self.m = m
        self.verbose = verbose
        self.max_tree_height = max_tree_height
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
            if self.verbose:
                print(f"--- Starting game {i} ---")
                print(f"Start state: {self.state_manager.pretty_state_string(self.init_state, include_max=True)}")
            else:
                print_loader(i, self.g, 1)
            state = self.state_manager.copy_state(self.init_state)
            mcts = MCTS(state, self.state_manager, self.max_tree_height)
            while not self.state_manager.is_end_state(state):
                previous_state = self.state_manager.copy_state(state)
                state = mcts.run(self.m)
                mcts.root_state = state
                mcts.cut_tree_at_state(state)
                if self.verbose:
                    print(f"Player { 2 if state[1] else 1} {self.state_manager.get_move_string(previous_state, state)}"
                          f" : {self.state_manager.pretty_state_string(state)}")
            if state[1]:
                number_of_wins += 1
            if self.verbose:
                print(f"Player { 1 if state[1] else 2} wins the game")

        print('\n------------- SUMMARY -------------')
        print(f'Player 1 wins {number_of_wins} games out of {self.g}. ({round((number_of_wins/self.g)*100)}%)')
