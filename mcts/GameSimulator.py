from mcts.StateManager import StateManager
from mcts.MCTS import MCTS
from libs.helpers import print_loader
import enum

class StartingPlayerOptions(enum.Enum):
    P1 = "P1"
    P2 = "P2"

class GameSimulator:
    def __init__(self, g, p: StartingPlayerOptions, m, verbose, max_tree_height, c, k):
        self.g = g
        self.p = p
        self.m = m
        self.k = k
        self.verbose = verbose
        self.max_tree_height = max_tree_height
        self.c = c
        self.p = 1 if p == StartingPlayerOptions.P1 else 2


    def run(self):
        number_of_wins = 0
        for i in range(1, self.g + 1):
            state_manager = StateManager(self.k, self.p)
            state = state_manager.get_state()
            if self.verbose:
                print(f"--- Starting game {i} ---")
                print(f"Start state: {state_manager.pretty_state_string(state, include_max=True)}")
            else:
                print_loader(i, self.g, 1)
            mcts = MCTS(state, state_manager, self.max_tree_height, c=self.c)
            while not mcts.is_end_state(state):
                previous_state = state
                state = mcts.run(self.m) # , previous_state
                mcts.root_state = state
                mcts.cut_tree_at_state(state)
                if self.verbose:
                    print(
                        f"Player { 1 if state_manager.is_P1(previous_state) else 2} "
                        f"{state_manager.get_move_string(previous_state, state)}"
                        f" : {state_manager.pretty_state_string(state)}"
                    )
            if not state_manager.is_P1(state):
                number_of_wins += 1
            if self.verbose:
                print(f"Player {2 if state_manager.is_P1(state) else 1} wins the game")
        print("\n------------- SUMMARY -------------")
        print(f"Player 1 wins {number_of_wins} games out of {self.g}. ({round((number_of_wins/self.g)*100)}%)")
