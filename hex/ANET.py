from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers
import numpy as np
from hex.StateManager import StateManager
import random


class ANET:
    def __init__(self, size_of_board, save_interval=10, batch_size=10, max_size_buffer=1000):
        self.save_interval = save_interval
        self.size_of_board = size_of_board
        self.max_size_buffer = max_size_buffer
        self.batch_size = batch_size
        self.replay_buffer = []
        self.number_of_train_executions = 0
        # Input shape: Adding one to give information of current player. Multiply by two to get binary data
        self.input_shape = ((self.size_of_board ** 2) * 2 + 2, )

        # Building model
        self.model = Sequential()
        # Adding first layer with input size depending on board size
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
            loss="categorical_crossentropy", optimizer=optimizers.Adam(), metrics=["accuracy"]
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
    def predict_and_normalize(model: Sequential, state: str):
        net_distribution = model.predict(np.array([ANET.convert_state_to_network_format(state)]))[0]
        # Filter out taken cells in the board
        for index, share_of_distribution in np.ndenumerate(net_distribution):
            if StateManager.index_cell_is_occupied(index[0], state):
                net_distribution[index] = 0
        # Normalize
        return net_distribution/sum(net_distribution)

    def predict(self, state):
        return ANET.predict_and_normalize(self.model, state)

    def train(self):
        x, y = self._get_random_minibatch()
        self.model.fit(x, y, verbose=0)
        self.number_of_train_executions += 1
        if self.number_of_train_executions % self.save_interval == 0:
            self.save_model()

    def save_model(self, episode_num):
        self.model.save(f'saved_models/model_{episode_num}.h5')

    def _get_random_minibatch(self):
        # random.shuffle(self.replay_buffer)
        # try:
        #    batch = random.sample(self.replay_buffer, self.batch_size)
        # except ValueError:
        #    raise ValueError(
        #        "Batch size is bigger than replay buffer. Increase number of simulations or lower batch size"
        #    )

        x = []
        y = []
        for case in self.replay_buffer:
            x.append(case[0])  # Add state as x
            y.append(case[1])  # Add distribution as y
        return (
            np.array(x),
            np.array(y)
        )

    def add_case(self, state, distribution_of_visit_counts):
        self.replay_buffer.append(
            (ANET.convert_state_to_network_format(state), distribution_of_visit_counts)
        )
        if len(self.replay_buffer) > self.max_size_buffer:
            index = random.randint(1,300)
            del self.replay_buffer[index]

