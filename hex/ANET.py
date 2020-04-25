from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers
from tensorflow.keras.models import load_model
import re
import numpy as np
import random
import math
import os
import glob


from hex.StateManager import StateManager


class ANET:
    def __init__(
        self,
        size_of_board,
        batch_size=350,
        max_size_buffer=2000,
        replay_buffer_cutoff_rate=0.3,
        epochs=5,
        verbose=2,  # one line per epoch
        model=None,
        episode_number=0,
        save_directory="trained_models",
    ):
        self.size_of_board = size_of_board
        self.max_size_buffer = max_size_buffer
        self.batch_size = batch_size
        self.epochs = epochs
        self.verbose = verbose
        self.replay_buffer = []
        self.replay_buffer_cutoff_rate = replay_buffer_cutoff_rate
        # Input shape: Adding one to give information of current player. Multiply by two to get binary data
        self.input_shape = ((self.size_of_board ** 2) * 2 + 10,)

        # If model is loaded from file, this field indicates number of episodes ran before saving
        self.episode_number = episode_number
        self.save_directory = save_directory

        if model is None:
            # Deleting current models in directory
            ANET.delete_models(save_directory)
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
        else:
            self.model = model

    @staticmethod
    def convert_state_to_network_format(state: str):
        board_str, player_str = StateManager.extract_state(state)
        board_nn_representation = [int(player_str == "1")] * 5 + [
            int(player_str == "2")
        ] * 5
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
        self.model.fit(
            x, y, batch_size=self.batch_size, epochs=self.epochs, verbose=self.verbose
        )

    def save_model(self, episode_number):
        self.episode_number = episode_number
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)
        self.model.save(f"{self.save_directory}/model_{episode_number}.h5")

    @staticmethod
    def infer_board_size_from_model(model: Sequential) -> int:
        """
        Using input shape of model to infer the board size of the model
        :param model: Sequential model
        :return: size of board for the model
        """
        return int(math.sqrt((model.input_shape[1] - 10) / 2))

    @staticmethod
    def load_model(model_path: str):
        episode_number = int(re.search(f"/model_(.*?).h5", model_path).group(1))
        model = load_model(model_path)
        return ANET(
            ANET.infer_board_size_from_model(model),
            model=model,
            episode_number=episode_number,
        )

    def load_models(self):
        """
        Fetches all file paths in the trained_models folder. Loads all models and appends to list
        :return: list of player objects, list of the number of episodes trained for each model: [obj], [int]
        """
        # Get list of paths to all saved models
        all_models = glob.glob(self.save_directory + "/*.h5")
        return sorted(
            [ANET.load_model(model_path) for model_path in all_models],
            key=lambda model: model.episode_number,
        )

    @staticmethod
    def delete_models(path_to_models: str):
        # Get list of paths to all saved models
        all_models = glob.glob(f"{path_to_models}/*.h5")
        for path_to_model in all_models:
            # Remove file
            os.remove(path_to_model)

    def delete_associated_models(self):
        ANET.delete_models(self.save_directory)

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
                (
                    ANET.convert_state_to_network_format(state),
                    distribution_of_visit_counts,
                )
            )
            if len(self.replay_buffer) > self.max_size_buffer:
                index = random.randint(
                    1, math.floor(self.max_size_buffer * self.replay_buffer_cutoff_rate)
                )
                del self.replay_buffer[index]

    def gen_cases(self, state, distribution_of_visit_counts):
        """
        Flips the board 180 deg to create another training case.
        :param state:
        :param distribution_of_visit_counts:
        :return:
        """
        generated_cases = [(state, distribution_of_visit_counts)]
        # reverse both board rep of state string and distribution
        flipped_state = "".join(reversed(state[:-2])) + state[-2:]
        flipped_dist = distribution_of_visit_counts[::-1]

        tuple = (flipped_state, flipped_dist)
        generated_cases.append(tuple)
        if self.verbose:
            print(generated_cases)
        return generated_cases
