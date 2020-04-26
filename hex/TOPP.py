import glob
from tensorflow.keras.models import load_model
import re
import numpy as np
from hex.StateManager import StateManager
from hex.ANET import ANET
from prettytable import PrettyTable

MODELS_PATH = r"trained_models"


class TOPP:
    def __init__(self, board_size):

        self.models, self.episode_num_list = self.load_models()
        self.state_manager = None
        self.board_size = board_size

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
                print(self.episode_num_list[index1])
                print(self.episode_num_list[index2 + index1 + 1])
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
                print(self.state_manager.pretty_state_string())
                distribution = ANET.predict_and_normalize(model, state)
                for i in range(0,self.board_size):
                    print([distribution[j] for j in range(self.board_size*i, self.board_size*i + self.board_size)])
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

    def load_models(self):
        """
        Fetches all file paths in the trained_models folder. Loads all models and appends to list
        :return: list of player objects, list of the number of episodes trained for each model: [obj], [int]
        """
        # Get list of paths to all saved models
        all_models = glob.glob(MODELS_PATH + "/*.h5")
        models = []

        for model_path in all_models:
            # Fetch episode number from model file name
            episode_num = int(
                re.search(f"{MODELS_PATH}/model_(.*?).h5", model_path).group(1)
            )
            model = load_model(model_path)
            models.append((model, episode_num))
            # Sort for increasing num ep trained models
            models = sorted(models, key=lambda tup: tup[1])
        if len(models):
            # Split into two lists
            players, episode_num_list = zip(*models)
            return list(players), list(episode_num_list)
        else:
            return [], []

    @staticmethod
    def delete_models():
        import os

        # Get list of paths to all saved models
        all_models = glob.glob(f"{MODELS_PATH}/*.h5")
        for path_to_model in all_models:
            # Remove file
            os.remove(path_to_model)

    def display_result(self, score_matrix):
        """
        Displays the score_matrix as a table
        :param score_matrix: np.array
        """
        header = ["wins \ losses"]
        for i in self.episode_num_list:
            header.append(i)
        t = PrettyTable(header)
        for index, row in enumerate(score_matrix):
            line = [self.episode_num_list[index]]
            for cell in row:
                line.append(cell)
            t.add_row(line)
        print(t)


TOPP.delete_models()
