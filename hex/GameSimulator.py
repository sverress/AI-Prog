from hex.StateManager import StateManager
from hex.ANET import ANET
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
        self.state_manager = None
        self.current_state = None
        self.number_of_wins = 0
        self.actor_network = ANET(k)

    def print_start_state(self, i):
        if self.verbose:
            print(f"--- Starting game {i} ---")
            print(f"Start state: {self.state_manager.pretty_state_string()}")
        else:
            print_loader(i, self.g, 1)

    def print_action(self, action: str):
        if self.verbose:
            x_pos, y_pos, player = self.state_manager.check_and_extract_action_string(action, check_player_turn=False)
            print(
                f"Player {player} placed a piece at ({x_pos}, {y_pos})"
                f" : {self.state_manager.pretty_state_string()}"
            )

    def print_winner_of_batch_game(self):
        if self.verbose:
            print(
                f"Player {2 if self.state_manager.get_player(self.current_state) == 1 else 1} wins the game"
            )

    def print_run_summary(self):
        print("\n------------- SUMMARY -------------")
        print(
            f"Player 1 wins {self.number_of_wins} games out of {self.g}."
            f" ({round((self.number_of_wins / self.g) * 100)}%)"
        )

    def update_winner_stats(self):
        if not self.state_manager.get_player(self.current_state) == 1:
            self.number_of_wins += 1

    def run(self):
        for i in range(1, self.g + 1):
            self.state_manager = StateManager(self.k, self.p)
            self.print_start_state(i)
            mcts = MCTS(self.state_manager, self.actor_network, max_tree_height=self.max_tree_height, c=self.c)
            while not self.state_manager.is_end_state():
                action = mcts.run(self.m)
                self.state_manager.perform_action(action)
                self.print_action(action)
            self.update_winner_stats()
            self.actor_network.train()
            self.print_winner_of_batch_game()
        self.print_run_summary()
