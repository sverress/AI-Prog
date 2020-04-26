import random
from prettytable import PrettyTable
import numpy as np
import math

from hex.StateManager import StateManager
from hex.ANET import ANET
from hex.MCTS import MCTS
from libs.helpers import print_loader


class StartingPlayerOptions:
    P1 = "P1"
    P2 = "P2"
    ALTERNATING = "ALTERNATING"

    @staticmethod
    def get_starting_player(option: str) -> int:
        return {
            StartingPlayerOptions.P1: 1,
            StartingPlayerOptions.P2: 2,
            StartingPlayerOptions.ALTERNATING: random.randint(1, 2),
        }.get(option)


class GameSimulator:
    def __init__(
        self,
        g,
        p,
        verbose,
        k,
        print_parameters=False,
        save_interval=10,
        actor_net_parameters=None,
        mcts_parameters=None,
    ):
        self.number_of_episodes_to_play = g
        self.starting_player_option = p
        self.k = k
        self.verbose = verbose
        self.state_manager = None
        self.current_state = None
        self.winner_stats = np.zeros((2, 2))
        self.mcts_parameters = mcts_parameters if mcts_parameters else {}
        if actor_net_parameters:
            self.actor_net_parameters = actor_net_parameters
            self.actor_network = ANET(k, **actor_net_parameters)
        else:
            self.actor_network = ANET(k)
        self.save_interval = save_interval
        if print_parameters:
            self.print_all_parameters()

    def print_all_parameters(self):
        print("===================================")
        print("            PARAMETERS             ")
        print("===================================")
        print("number of games in a batch:", self.number_of_episodes_to_play)
        print("starting-player option:", self.starting_player_option)
        print("Verbose:", self.verbose)
        print("k:", self.k)
        print("save interval:", self.save_interval)
        print("===================================")
        self.print_parameters(self.actor_net_parameters, "          ANET-PARAMETERS          ")
        self.print_parameters(self.mcts_parameters, "          MCTS-PARAMETERS          ")

    @staticmethod
    def print_parameters(parameters, header):
        if parameters:
            print(header)
            print("===================================")
            print(
                "".join(
                    [
                        f"{key}: {parameters[key]} \n"
                        for key in parameters.keys()
                    ]
                )
            )
            print("===================================")

    def print_start_state(self, i):
        if self.verbose:
            print(f"--- Starting game {i} ---")
            print(f"Start state: {self.state_manager.pretty_state_string()}")
        else:
            print_loader(i, self.number_of_episodes_to_play, 1)

    def print_action(self, action: str):
        if self.verbose:
            x_pos, y_pos, player = self.state_manager.check_and_extract_action_string(
                action, check_player_turn=False
            )
            print(
                f"Player {player} placed a piece at ({x_pos}, {y_pos})"
                f" : {self.state_manager.pretty_state_string()}"
            )

    def print_winner_of_batch_game(self):
        if self.verbose:
            print(
                f"Player {2 if self.state_manager.current_player() == 1 else 1} wins the game"
            )

    def print_run_summary(self):
        print("\n------------- SUMMARY -------------")
        header = ["winning player \ starting player", "1", "2"]
        t = PrettyTable(header)
        for index, row in enumerate(self.winner_stats):
            line = [str(index + 1)]
            for cell in row:
                line.append(cell)
            t.add_row(line)
        print(t)

    def update_winner_stats(self, starting_player: int) -> None:
        second_index = starting_player - 1
        winning_player = 1 if self.state_manager.current_player() == 2 else 2
        first_index = winning_player - 1
        self.winner_stats[first_index][second_index] += 1

    def run(self):
        starting_player = StartingPlayerOptions.get_starting_player(
            self.starting_player_option
        )
        for i in range(1, self.number_of_episodes_to_play + 1):
            self.state_manager = StateManager(self.k, starting_player)
            self.print_start_state(i)
            mcts = MCTS(
                self.state_manager,
                self.actor_network,
                random_simulation_rate=math.tanh(i / self.number_of_episodes_to_play) * 1.2,
                **self.mcts_parameters,
            )
            while not self.state_manager.is_end_state():
                action = mcts.run(self.state_manager.get_state())
                self.state_manager.perform_action(action)
                self.print_action(action)
            self.update_winner_stats(starting_player)
            self.actor_network.train()
            self.print_winner_of_batch_game()
            if self.starting_player_option == StartingPlayerOptions.ALTERNATING:
                starting_player = StateManager.get_opposite_player(starting_player)
            if i % self.save_interval == 0:
                self.actor_network.save_model(episode_number=i)
        self.print_run_summary()
        ANET.save_buffer_to_file(self.number_of_episodes_to_play, self.k, self.actor_network)
