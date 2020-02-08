from peg_solitaire.board import Board
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

    def init_nn(self, layers, board_size):
        from keras.models import Sequential
        from keras.layers import Dense

        self.model = Sequential()
        # Adding first layer with input size depending on board size
        self.model.add(Dense(units=layers[0], activation='relu', input_dim=board_size**2))
        for i in range(1, len(layers)):
            self.model.add(Dense(units=layers[i], activation='relu'))
        self.model.add(Dense(units=1, activation='softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])

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
        self.value_func[state] = value

    def set_eligibility_trace(self, state, value):
        self.elig_trace[state] = value

    def get_state_value(self, state: str):
        """
        Fetch the state value from the value function by state key.
        :param state: state key: str
        :return: state value: float
        """
        if self.model:
            return self.model.predict(np.array([int(string_num) for string_num in state]))
        else:
            return self.value_func[state]

    def get_eligibility_trace(self, state: str):
        return self.elig_trace[state]

    def update_value_func(self, state: str, delta: float):
        """
        Finds and sets the new state value to the value func dict
        :param state: str representation of string
        :param delta: TD-error
        """
        state_value = self.get_state_value(state)
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

    def init_state_from_board(self, board: Board):
        state_str = board.get_state()
        if state_str not in self.value_func:
            self.set_value_func(board.get_state(), random.uniform(0, 0.01))
        if state_str not in self.elig_trace:
            self.set_eligibility_trace(board.get_state(), 0)
