from hex.StateManager import StateManager
from hex.MCTS import MCTS
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

    def print_start_state(self, i, state_manager, state):
        if self.verbose:
            print(f"--- Starting game {i} ---")
            print(
                f"Start state: {state_manager.pretty_state_string(state, include_max=True)}"
            )
        else:
            print_loader(i, self.g, 1)

    def print_move(self, state_manager, previous_state, state):
        if self.verbose:
            print(
                f"Player {1 if state_manager.is_P1(previous_state) else 2} "
                f"{state_manager.get_move_string(previous_state, state)}"
                f" : {state_manager.pretty_state_string(state)}"
            )

    def print_winner_of_batch_game(self, state_manager, state):
        if self.verbose:
            print(f"Player {2 if state_manager.is_P1(state) else 1} wins the game")

    def print_run_summary(self, number_of_wins):
        print("\n------------- SUMMARY -------------")
        print(
            f"Player 1 wins {number_of_wins} games out of {self.g}. ({round((number_of_wins / self.g) * 100)}%)"
        )

    def run(self):
        number_of_wins = 0
        for i in range(1, self.g + 1):
            state_manager = StateManager(self.k, self.p)
            state = state_manager.get_state()
            self.print_start_state(i, state_manager, state)
            mcts = MCTS(state, state_manager, self.max_tree_height, c=self.c)
            while not mcts.is_end_state(state):  # Should be a call to the state manager
                previous_state = state
                state = mcts.run(self.m)  # , previous_state
                # Should the next two methods be added to the
                mcts.root_state = state
                mcts.cut_tree_at_state(state)
                self.print_move(state_manager, previous_state, state)
            if not state_manager.is_P1(state):
                number_of_wins += 1
            self.print_winner_of_batch_game(state_manager, state)
