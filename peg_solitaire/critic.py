from peg_solitaire.solitaireboard import SolitaireBoard
from peg_solitaire.helpers import *
import numpy as np
import random


class Critic:
    def __init__(self, gamma, alpha, lambd):
        """

        :param gamma: Discount factor
        :param alpha: Learning rate
        :param lambd: Trace-decay factor
        """
        self.value_func = dict()
        self.elig_trace = dict()
        self.gamma = gamma
        self.alpha = alpha
        self.lambd = lambd
        self.model = None  # Variable for nn

    def init_nn(self, layers: [int], dimension: int):
        """
        Initialize the deep neural network that will be
        :param layers: number of hidden layers to be initialized
        :param dimension: number of nodes in first layer
        """
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense
        from tensorflow.keras import optimizers

        model = Sequential()
        optim = optimizers.SGD(lr=self.alpha)
        # Adding first layer with input size depending on board size
        model.add(Dense(units=layers[0], activation='relu', input_dim=dimension, kernel_initializer='random_uniform'))
        for i in range(1, len(layers)):
            model.add(Dense(units=layers[i], activation='relu', kernel_initializer='random_uniform'))
        model.add(Dense(units=1, activation='relu', kernel_initializer='random_uniform'))
        model.compile(loss='mean_squared_error', optimizer=optim, metrics=['accuracy'])

        self.model = KerasModelWrapper(model, self.lambd, self.gamma)

    def calculate_td_error(self, parent_state: str, child_state: str, reward: float):
        """
        Calculates the Temporal Difference error denoted delta
        :param parent_state: Previous state: str
        :param child_state: Current state: str
        :param reward: Reward from going to "child state": float
        :return: the TD error; delta
        """
        delta = reward + self.gamma * self.get_state_value(child_state) - self.get_state_value(parent_state)
        return delta

    def set_value_func(self, state, value):
        """
        Maps state to value in the critic table value function
        :param state: state key: str
        :param value: float
        """
        self.value_func[state] = value

    def set_eligibility_trace(self, state: str, value: float):
        """
        Maps state to value in the critic eligibility trace table
        :param state: state key: str
        :param value: float
        """
        self.elig_trace[state] = value

    def get_state_value(self, state: str):
        """
        Fetch the state value from the value function by state key.
        :param state: state key: str
        :return: state value: float
        """
        if self.model:
            input_np = string_to_np_array(state).reshape((1, len(state)))
            output = self.model.model(input_np)
            return output[0][0]
        else:
            return self.value_func.get(state)

    def get_eligibility_trace(self, state: str):
        """
        Fetch elig trace for key
        :param state: state key: str
        """
        return self.elig_trace.get(state)

    def update_value_func(self, state: str, delta: float):
        """
        Finds and sets the new state value to the value func dict
        :param state: str representation of string
        :param delta: TD-error
        """
        state_value = self.get_state_value(state)
        if self.model:
            self.model.fit(np.array(string_to_np_array(state)).reshape((1, len(state))), np.array([state_value + delta]).reshape((1, 1)), delta, verbose=False)
        else:
            elig_trace_value = self.get_eligibility_trace(state)
            new_state_value = state_value + self.alpha*delta*elig_trace_value
            self.set_value_func(state, new_state_value)

    def update_eligibility_trace(self, state: str):
        """
        Finds and sets the eligibility trace value to the elig_trace dict
        :param state: str representation of string
        """
        elig_trace_value = self.get_eligibility_trace(state)
        new_elig_trace_value = self.gamma*self.lambd*elig_trace_value
        self.set_eligibility_trace(state, new_elig_trace_value)

    def init_state_from_board(self, board: SolitaireBoard):
        """
        Initialize state to random small value if the state has not been encountered before
        :param board: board object representing current board state
        """
        state_str = board.get_state()
        if state_str not in self.value_func:
            self.set_value_func(board.get_state(), random.uniform(0, 0.001))
