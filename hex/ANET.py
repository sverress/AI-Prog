from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers
import numpy as np
import random


class ANET:
    def __init__(self, size_of_board, save_interval=10, batch_size=10):
        self.save_interval = save_interval
        self.size_of_board = size_of_board
        self.batch_size = batch_size
        self.replay_buffer = []
        self.number_of_train_executions = 0

        # Building model
        self.model = Sequential()
        # Adding first layer with input size depending on board size
        self.model.add(
            Dense(
                units=size_of_board,
                activation="relu",
                input_shape=(size_of_board ** 2,),
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
            loss="mean_squared_error", optimizer=optimizers.SGD(), metrics=["accuracy"]
        )

    @staticmethod
    def string_to_input_np(state: str):
        """
        Might be a StateManager method
        """
        board_str = state[:-2]  # extract board part of state string
        return np.array([[float(cell) for cell in board_str]])

    def predict(self, state: str):
        return self.model.predict(ANET.string_to_input_np(state))[0]

    def train(self):
        x, y = self._get_random_minibatch()
        self.model.fit(x, y, verbose=0)
        self.number_of_train_executions += 1
        if self.number_of_train_executions % self.save_interval == 0:
            self.save_model()

    def save_model(self):
        pass

    def _get_random_minibatch(self):
        random.shuffle(self.replay_buffer)
        try:
            batch = random.sample(self.replay_buffer, self.batch_size)
        except ValueError:
            raise ValueError(
                "Batch size is bigger than replay buffer. Increase number of simulations or lower batch size"
            )

        x = []
        y = []
        for case in batch:
            x.append(case[0])  # Add state as x
            y.append(case[1])  # Add distribution as y
        return (
            np.array(x).reshape((len(x), self.size_of_board ** 2)),
            np.array(y).reshape((len(y), self.size_of_board ** 2)),
        )

    def add_case(self, state, distribution_of_visit_counts):
        self.replay_buffer.append(
            (ANET.string_to_input_np(state), distribution_of_visit_counts)
        )
