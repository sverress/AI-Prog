from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers
import numpy as np
import random
import math
import os

from hex.StateManager import StateManager


class ANET:
    def __init__(
        self,
        size_of_board,
        batch_size=350,
        max_size_buffer=1000,
        replay_buffer_cutoff_rate=0.3,
        epochs = 10,
        verbose = 2 # one line per epoch
    ):
        self.size_of_board = size_of_board
        self.max_size_buffer = max_size_buffer
        self.batch_size = batch_size
        self.epochs = epochs
        self.verbose = verbose
        self.replay_buffer = []
        self.replay_buffer_cutoff_rate = replay_buffer_cutoff_rate
        # Input shape: Adding one to give information of current player. Multiply by two to get binary data
        self.input_shape = ((self.size_of_board ** 2) * 2 + 2,)

        # Building model
        self.model = Sequential()
        # Adding first layer with input size depending on board sizes
        self.model.add(
            Dense(
                units=size_of_board,
                activation="relu",
                input_shape=self.input_shape,
                kernel_initializer="random_uniform",
            )
        )
        for i in range(1, 3):
            self.model.add(
                Dense(
                    units=size_of_board ** 2,
                    activation="relu",
                    kernel_initializer="random_uniform",
                )
            )
        self.model.add(
            Dense(
                units=size_of_board ** 2,
                activation="softmax",
                kernel_initializer="random_uniform",
            )
        )
        self.model.compile(
            loss="categorical_crossentropy",
            optimizer=optimizers.Adam(),
            metrics=["mse"],
        )

    @staticmethod
    def convert_state_to_network_format(state: str):
        board_str, player_str = StateManager.extract_state(state)
        board_nn_representation = [int(player_str == "1"), int(player_str == "2")]
        for cell_value in board_str:
            board_nn_representation.append(int(cell_value == "1"))
            board_nn_representation.append(int(cell_value == "2"))
        return board_nn_representation

    @staticmethod
    def predict_and_normalize(model: Sequential, state: str) -> np.array:
        input_data = np.array([ANET.convert_state_to_network_format(state)])
        net_distribution_tensor = model(input_data)[0]
        net_distribution = []
        # Filter out taken cells in the board
        for index, share_of_distribution in np.ndenumerate(net_distribution_tensor):
            if StateManager.index_cell_is_occupied(index[0], state):
                net_distribution.append(0.0)
            else:
                net_distribution.append(float(share_of_distribution))
        # Normalize
        return np.array(net_distribution) / sum(net_distribution)

    def predict(self, state):
        return ANET.predict_and_normalize(self.model, state)

    def train(self):
        x, y = self._get_random_mini_batch()
        self.model.fit(x, y, batch_size=self.batch_size, epochs=self.epochs, verbose=self.verbose)

    def save_model(self, episode_num):
        if not os.path.exists("trained_models"):
            os.mkdir("trained_models")
        self.model.save(f"trained_models/model_{episode_num}.h5")

    def _get_random_mini_batch(self) -> (np.array, np.array):
        """
        :return: Random sample of size self.batch_size from the the replay buffer.
        If the replay buffer is smaller than the batch size it will return the whole replay buffer
        """
        if len(self.replay_buffer) < self.batch_size:
            batch = self.replay_buffer.copy()
        else:
            batch = random.sample(self.replay_buffer, self.batch_size)
        x = []
        y = []
        for case in batch:
            x.append(case[0])  # Add state as x
            y.append(case[1])  # Add distribution as y
        return np.array(x), np.array(y)

    def add_case(self, state, distribution_of_visit_counts):
        generated_cases = self.gen_cases(state, distribution_of_visit_counts)
        for case in generated_cases:
            state = case[0]
            distribution_of_visit_counts = case[1]
            self.replay_buffer.append(
                (ANET.convert_state_to_network_format(state), distribution_of_visit_counts)
            )
            if len(self.replay_buffer) > self.max_size_buffer:
                index = random.randint(
                    1, math.floor(self.max_size_buffer * self.replay_buffer_cutoff_rate)
                )
                del self.replay_buffer[index]

    def gen_cases(self, state, dist):
        """
        Flips the board 180 deg to create another training case.
        :param state:
        :param distribution_of_visit_counts:
        :return:
        """
        generated_cases = [(state, dist)]

        # reverse both board rep of state string and distribution
        state_180 = ''.join(reversed(state[:-2])) + state[-2:]
        dist_180 = dist[::-1]
        tuple = (state_180, dist_180)
        generated_cases.append(tuple)

        # swith row and cols for case rot 90
        board_90 = np.zeros(self.size_of_board ** 2, dtype=int)
        dist_90 = np.zeros(self.size_of_board ** 2)
        for row in range(0, self.size_of_board):
            for col in range(0, self.size_of_board):
                flatten_position_board = row * self.size_of_board + col
                flatten_position_new_board = col * self.size_of_board + row
                if state[flatten_position_board] == '0':
                    board_90[flatten_position_new_board] = state[flatten_position_board]
                else:
                    board_90[flatten_position_new_board] = '1' if state[flatten_position_board] == '2' else '2'
                dist_90[flatten_position_new_board] = dist[flatten_position_board]

        player_str = '1' if state[-1] == '2' else '2'
        state_90 = ''.join(board_90.astype(str)) + ':' + player_str

        tuple = (state_90, list(dist_90))
        generated_cases.append(tuple)

        # reverse both board rep of state string and distribution for the state_90
        state_270 = ''.join(reversed(state_90[:-2])) + state_90[-2:]
        dist_270 = dist_90[::-1]
        tuple = (state_270, list(dist_270))
        generated_cases.append(tuple)

        print(generated_cases)
        return generated_cases