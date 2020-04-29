from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential
import re
import numpy as np
import random
import math
import os
import glob
from abc import ABC, abstractmethod


from hex.StateManager import StateManager


class HexNet(ABC):
    def __init__(
        self,
        size_of_board,
        buffer_batch_size=350,
        max_size_buffer=2000,
        replay_buffer_cutoff_rate=0.3,
        epochs=5,
        verbose=2,  # one line per epoch
        model=None,
        episode_number=0,
        save_directory="trained_models",
        hidden_layers_structure=None,
        learning_rate=0.01,
        batch_size=32,
    ):
        self.size_of_board = size_of_board
        self.max_size_buffer = max_size_buffer
        self.buffer_batch_size = buffer_batch_size
        self.epochs = epochs
        self.verbose = verbose
        self.replay_buffer = []
        self.replay_buffer_cutoff_rate = replay_buffer_cutoff_rate
        # Input shape: Adding one to give information of current player. Multiply by two to get binary data
        self.input_shape = ((self.size_of_board ** 2) * 2 + 10,)

        # If model is loaded from file, this field indicates number of episodes ran before saving
        self.episode_number = episode_number
        self.save_directory = save_directory
        self.batch_size = batch_size
        self.model = self.build_model(model, hidden_layers_structure, learning_rate)

    @abstractmethod
    def build_model(self, model, hidden_layers_structure, learning_rate):
        pass

    @staticmethod
    @abstractmethod
    def create_hex_net(board_size, **kwargs):
        pass

    @staticmethod
    def train_network_from_cases(cases_directory, anet_parameters):
        x_path = [
            filename
            for filename in os.listdir(cases_directory)
            if filename.startswith("x")
        ][0]
        y_path = [
            filename
            for filename in os.listdir(cases_directory)
            if filename.startswith("y")
        ][0]
        x, y = (
            np.load(f"{cases_directory}/{x_path}"),
            np.load(f"{cases_directory}/{y_path}"),
        )
        anet = HexNet.create_hex_net(int(x_path[2]), **anet_parameters)
        history = anet.model.fit(
            x, y, epochs=anet.epochs, verbose=anet.verbose, validation_split=0.2
        )
        return anet, history

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
        input_data = np.array([HexNet.convert_state_to_network_format(state)])
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
        return HexNet.predict_and_normalize(self.model, state)

    def train(self):
        x, y = self._get_random_mini_batch()
        if self.verbose == 2:
            print("Size of replay buffer:", len(self.replay_buffer))
        return self.model.fit(
            x,
            y,
            batch_size=self.batch_size,
            epochs=self.epochs,
            verbose=self.verbose,
            validation_data=self._get_random_mini_batch(),
        )

    def save_model(self, episode_number):
        self.episode_number = episode_number
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

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
        return HexNet.create_hex_net(
            HexNet.infer_board_size_from_model(model),
            model=model,
            episode_number=episode_number,
        )

    @staticmethod
    def load_models(directory: str):
        """
        Fetches all file paths in the trained_models folder. Loads all models and appends to list
        :return: list of player objects, list of the number of episodes trained for each model: [obj], [int]
        """
        # Get list of paths to all saved models
        all_models = glob.glob(directory + "/*.h5")
        return sorted(
            [HexNet.load_model(model_path) for model_path in all_models],
            key=lambda model: model.episode_number,
        )

    def load_directory_models(self):
        return HexNet.load_models(self.save_directory)

    @staticmethod
    def delete_models(path_to_models: str):
        # Get list of paths to all saved models
        all_models = glob.glob(f"{path_to_models}/*.h5")
        for path_to_model in all_models:
            # Remove file
            os.remove(path_to_model)

    def delete_associated_models(self):
        HexNet.delete_models(self.save_directory)

    def _get_random_mini_batch(self) -> (np.array, np.array):
        """
        :return: Random sample of size self.buffer_batch_size from the the replay buffer.
        If the replay buffer is smaller than the batch size it will return the whole replay buffer
        """
        if len(self.replay_buffer) < self.buffer_batch_size:
            batch = self.replay_buffer.copy()
        else:
            batch = random.sample(self.replay_buffer, self.buffer_batch_size)
        x = []
        y = []
        for case in batch:
            x.append(case[0])  # Add state as x
            y.append(case[1])  # Add distribution as y
        return np.array(x), np.array(y)

    def add_case(self, state, target):
        self.replay_buffer.append(
            (
                HexNet.convert_state_to_network_format(state),
                target,
            )
        )
        if len(self.replay_buffer) > self.max_size_buffer:
            index = random.randint(
                1, math.floor(self.max_size_buffer * self.replay_buffer_cutoff_rate)
            )
            del self.replay_buffer[index]

    @staticmethod
    def save_buffer_to_file(num_episodes, k, ANET, cases_directory="cases"):
        x = []
        y = []
        for case in ANET.replay_buffer:
            x.append(case[0])  # Add state as x
            y.append(case[1])  # Add distribution as y
        if not os.path.exists(cases_directory):
            os.mkdir(cases_directory)
        np.save(f"{cases_directory}/x_{k}x{k}_{num_episodes}", np.array(x))
        np.save(f"{cases_directory}/y_{k}x{k}_{num_episodes}", np.array(y))
