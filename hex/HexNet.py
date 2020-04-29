
from tensorflow.keras.models import Sequential
import numpy as np
import random
import math
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
    def convert_state_to_network_format(state: str):
        board_str, player_str = StateManager.extract_state(state)
        board_nn_representation = [int(player_str == "1")] * 5 + [
            int(player_str == "2")
        ] * 5
        for cell_value in board_str:
            board_nn_representation.append(int(cell_value == "1"))
            board_nn_representation.append(int(cell_value == "2"))
        return board_nn_representation

    @abstractmethod
    def predict(self, state):
        return self.model(np.array([HexNet.convert_state_to_network_format(state)]))

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

    @staticmethod
    def infer_board_size_from_model(model: Sequential) -> int:
        """
        Using input shape of model to infer the board size of the model
        :param model: Sequential model
        :return: size of board for the model
        """
        return int(math.sqrt((model.input_shape[1] - 10) / 2))

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
