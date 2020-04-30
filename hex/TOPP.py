import numpy as np
from hex.StateManager import StateManager
from hex.ANET import ANET
from prettytable import PrettyTable
import matplotlib.pyplot as plt


class TOPP:
    def __init__(self, path: str, verbose=False):

        self.models = ANET.load_models(path)
        self.state_manager = None
        self.board_size = ANET.infer_board_size_from_model(self.models[0].model)
        self.verbose = verbose

    def play(self, num_games_per_match):
        """
        Plays out the turnament where all models are played agains each other
        :param num_games_per_match: number of games to be played internally for each match
        """
        # Each row represents how many wins model_{row_index} has won against each model_{col_index}.
        # Hence each col represents how many losses model_{col_index} has against each model_{row_index}
        score_matrix = np.zeros((len(self.models), len(self.models)), dtype=int)
        for index1, player1 in enumerate(self.models):
            for index2, player2 in enumerate(self.models[index1 + 1 :]):
                if self.verbose:
                    print(player1.episode_number)
                    print(player2.episode_number)
                wins_p1, wins_p2 = self.play_match(
                    num_games_per_match, player1, player2
                )
                score_matrix[index1, index2 + index1 + 1] += wins_p1
                score_matrix[index2 + index1 + 1, index1] += wins_p2
        self.display_result(score_matrix)

    def play_match(self, num_games_per_match, player1, player2):
        """
        Runs num_games_per_match games between player1 and player2 where the greedy action is chosen.
        Players start every other game.
        :param num_games_per_match: number of games to be played between two models
        :param player1: Keras NN trained on x number of episodes
        :param player2: Keras NN trained on y number of episodes
        :return: the number og wins for each player
        """
        wins_p1 = 0
        wins_p2 = 0
        starting_player = 1
        for i in range(0, num_games_per_match):
            self.state_manager = StateManager(
                board_size=self.board_size, starting_player=starting_player
            )
            while not self.state_manager.is_end_state():
                current_player = self.state_manager.current_player()
                model = player1 if current_player == 1 else player2
                state = self.state_manager.get_state()
                if self.verbose:
                    print(self.state_manager.pretty_state_string())
                distribution = model.predict(state)
                if self.verbose:
                    for k in range(0, self.board_size):
                        print(
                            [
                                distribution[j]
                                for j in range(
                                    self.board_size * k,
                                    self.board_size * k + self.board_size,
                                )
                            ]
                        )
                argmax_distribution_index = int(
                    np.argmax(distribution)
                )  # Greedy best from distribution
                action = self.state_manager.get_action_from_flattened_board_index(
                    argmax_distribution_index, state
                )
                self.state_manager.perform_action(action)
            if current_player == 1:
                wins_p1 += 1
            else:
                wins_p2 += 1
            starting_player = 1 if starting_player == 2 else 2

        return wins_p1, wins_p2

    def display_result(self, score_matrix):
        """
        Displays the score_matrix as a table
        :param score_matrix: np.array
        """
        header = ["wins \ losses"]
        for model in self.models:
            header.append(model.episode_number)
        header.append("sum")
        t = PrettyTable(header)
        x_axis = []
        y_axis = []
        for index, row in enumerate(score_matrix):
            line = [self.models[index].episode_number]
            x_axis.append(self.models[index].episode_number)
            for cell in row:
                line.append(cell)
            line.append(sum(line[1:]))
            y_axis.append(sum(line[1:-1]))
            t.add_row(line)
        print(t)
        plt.clf()
        plt.plot(x_axis, y_axis)
        plt.title('TOPP')
        plt.ylabel('Number of games won')
        plt.xlabel('Episode saved')
        plt.show()


def main():
    tournament = TOPP("/Users/svoss/KODE/AI-Prog/runs/jens_reccomend/trained_models", verbose=True)
    tournament.play(2)


if __name__ == "__main__":
    main()
