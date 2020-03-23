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
        self.state_manager = StateManager(self.k, self.p)
        self.current_state = self.state_manager.get_state()
        self.number_of_wins = 0
        self.mcts = MockMCTS(self.current_state)

    def print_start_state(self, i):
        if self.verbose:
            print(f"--- Starting game {i} ---")
            print(
                f"Start state: {self.state_manager.pretty_state_string(self.current_state, include_max=True)}"
            )
        else:
            print_loader(i, self.g, 1)

    def print_move(self, previous_state):
        if self.verbose:
            print(
                f"Player {1 if self.state_manager.is_P1(previous_state) else 2} "
                f"{self.state_manager.get_move_string(previous_state, self.current_state)}"
                f" : {self.state_manager.pretty_state_string()}"
            )

    def print_winner_of_batch_game(self):
        if self.verbose:
            print(
                f"Player {2 if self.state_manager.is_P1(self.current_state) else 1} wins the game"
            )

    def print_run_summary(self, number_of_wins):
        print("\n------------- SUMMARY -------------")
        print(
            f"Player 1 wins {number_of_wins} games out of {self.g}. ({round((number_of_wins / self.g) * 100)}%)"
        )

    def update_winner_stats(self):
        if not self.state_manager.is_P1(self.current_state):
            self.number_of_wins += 1

    def run(self):
        for i in range(1, self.g + 1):
            self.current_state = self.state_manager.get_state()
            self.print_start_state(i)
            while not self.mcts.is_end_state(
                self.current_state
            ):  # Should be a call to the state manager
                previous_state = self.current_state
                self.current_state = self.mcts.run(self.m)  # , previous_state
                self.mcts.root_state = self.current_state
                self.mcts.cut_tree_at_state(self.current_state)
                self.print_move(previous_state)
                self.update_winner_stats()
            self.print_winner_of_batch_game()


class MockMCTS:
    def __init__(self, state):
        self.state = state
        self.cut_tree_at_state = lambda s: None
        self.n = 0

    def run(self, m):
        self.n += 1
        return self.state

    def is_end_state(self, s):
        return self.n > 3
