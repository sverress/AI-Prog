from mcts.StateManager import Nim, Ledge
from mcts.MCTS import MCTS
from libs.helpers import print_loader
import enum
import random


class Games(enum.Enum):
    NIM = "NIM"
    LEDGE = "LEDGE"


class StartingPlayerOptions(enum.Enum):
    PLAYER_ONE = "PLAYER_ONE"
    PLAYER_TWO = "PLAYER_TWO"
    RANDOM = "RANDOM"


class GameSimulator:
    def __init__(
        self,
        g,
        p: StartingPlayerOptions,
        m,
        game: Games,
        n,
        k,
        b_init: ([int], bool),
        verbose,
        max_tree_height,
        c=1
    ):
        self.g = g
        self.p = p
        self.m = m
        self.verbose = verbose
        self.max_tree_height = max_tree_height
        self.c = c
        if game == Games.NIM:
            self.state_manager = Nim
            self.get_init_state = lambda: self.state_manager.init_game_state(
                N=n, K=k, P=self.get_initial_game_player()
            )
        if game == Games.LEDGE:
            self.b_init = b_init
            self.state_manager = Ledge
            self.get_init_state = lambda: self.state_manager.init_game_state(
                B_init=self.b_init, p=self.get_initial_game_player()
            )

    def get_initial_game_player(self):
        if self.p == StartingPlayerOptions.RANDOM:
            return bool(random.getrandbits(1))  # Get random boolean value
        return self.p == StartingPlayerOptions.PLAYER_ONE

    def run(self):
        number_of_wins = 0
        for i in range(1, self.g + 1):
            state = self.get_init_state()
            if self.verbose:
                print(f"--- Starting game {i} ---")
                print(
                    f"Start state: {self.state_manager.pretty_state_string(state, include_max=True)}"
                )
            else:
                print_loader(i, self.g, 1)
            mcts = MCTS(state, self.state_manager, self.max_tree_height, c=self.c)
            while not self.state_manager.is_end_state(state):
                previous_state = state
                state = mcts.run(self.m)
                mcts.root_state = state
                mcts.cut_tree_at_state(state)
                if self.verbose:
                    print(
                        f"Player { 1 if self.state_manager.is_player_1(previous_state) else 2} "
                        f"{self.state_manager.get_move_string(previous_state, state)}"
                        f" : {self.state_manager.pretty_state_string(state)}"
                    )
            if self.state_manager.is_player_1(state):
                number_of_wins += 1
            if self.verbose:
                print(
                    f"Player { 1 if self.state_manager.is_player_1(state) else 2} wins the game"
                )

        print("\n------------- SUMMARY -------------")
        print(
            f"Player 1 wins {number_of_wins} games out of {self.g}. ({round((number_of_wins/self.g)*100)}%)"
        )
