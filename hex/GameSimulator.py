from hex.StateManager import StateManager
from hex.ANET import ANET
from hex.MCTS import MCTS
from libs.helpers import print_loader
import enum
import random


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
        self.anet = ANET(k)

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

    def print_run_summary(self):
        print("\n------------- SUMMARY -------------")
        print(
            f"Player 1 wins {self.number_of_wins} games out of {self.g}. ({round((self.number_of_wins / self.g) * 100)}%)"
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

                # Get distribution and add the case to anet
                distribution_of_visit_counts = self.mcts.run(self.m)
                self.anet.add_case(self.current_state, distribution_of_visit_counts)

                # Choose action and reset tree (Reset mcts tree lines should be done in MCTS class?)
                previous_state = self.current_state
                move = argmax(distribution_of_visit_counts)
                self.current_state = do_move(self.current_state, move)
                self.mcts.root_state = self.current_state
                self.mcts.cut_tree_at_state(self.current_state)

                self.print_move(previous_state)

            self.update_winner_stats()
            self.anet.train()
            self.print_winner_of_batch_game()
        self.print_run_summary()


class MockMCTS:
    def __init__(self, state):
        self.state = state
        self.cut_tree_at_state = lambda s: None
        self.n = 0

    def run(self, m):
        """
        returns random distribution of visit counts
        :param m:
        :return:
        """
        self.n += 1
        counts = [random.randint(0, m) for i in range(0, len(self.state[:-2]))]
        return [count / sum(counts) for count in counts]

    def is_end_state(self, s):
        done = self.n > random.randint(15, 30)
        if done:
            self.n = 0
        return done


def argmax(liste):
    best = -float("Inf")
    best_i = -1
    for i in range(0, len(liste)):
        if liste[i] > best:
            best = liste[i]
            best_i = i
    return best_i


def do_move(state: str, move_index: int):
    output = ""
    for i, char in enumerate(state[:-2]):
        if i == move_index:
            output += state[-1]
        else:
            output += char
    return f"{output}:{1 if int(state[-1])==2 else 2}"
