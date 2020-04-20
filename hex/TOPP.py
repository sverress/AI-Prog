import glob
from keras.models import load_model
import re
from hex.StateManager import StateManager
from hex.ANET import ANET
import numpy as np

class TOPP:
    def __init__(self, board_size):
        path = r'trained_models'
        all_models = glob.glob(path + "/*.h5")
        self.models = []
        for model in all_models:
            episode_num = int(re.search('trained_models/model_(.*?).h5', model).group(1))
            self.models.append(load_model(model), episode_num)
        self.state_manager = None
        self.board_size = board_size

    def play(self, num_games_per_match):
        # Each row represents how many wins model_{row_index} has won against each model_{col_index}.
        # Hence each col represents how many losses model_{col_index} has against each model_{row_index}
        score_matrix = np.zeros((len(self.models), len(self.models)))
        for index1, player1 in enumerate(self.models):
            for index2, player2 in enumerate(self.models[index1+1:]):
                wins_p1, wins_p2 = self.play_match(num_games_per_match, player1, player2)
                score_matrix[index1, index2] += wins_p1
                score_matrix[index2, index1] += wins_p2
        print(score_matrix)

    def play_match(self, num_games_per_match, player1, player2):
        wins_p1 = 0
        wins_p2 = 0
        starting_player = 1
        for i in num_games_per_match:
            self.state_manager = StateManager(board_size=self.board_size, starting_player=starting_player)
            while not self.state_manager.is_end_state():
                current_player = self.state_manager.current_player()
                model = player1 if current_player == 1 else player2
                state = self.state_manager.get_state()
                distribution = self.action_distribution(state, model)
                argmax_distribution_index = int(np.argmax(distribution))  # Greedy best from distribution
                action = self.state_manager.get_action_from_flattened_board_index(argmax_distribution_index, state)
                self.state_manager.perform_action(action)
            if current_player == 1:
                wins_p1 += 1
            else:
                wins_p2 += 1
            starting_player = 1 if starting_player == 2 else 2

        return wins_p1, wins_p2

    def action_distribution(self, state: str, model):
        net_distribution = model.predict(np.array([ANET.convert_state_to_network_format(state)]))[0]
        # Filter out taken cells in the board
        for index, share_of_distribution in np.ndenumerate(net_distribution):
            if StateManager.index_cell_is_occupied(index[0], state):
                net_distribution[index] = 0
        return net_distribution/sum(net_distribution)