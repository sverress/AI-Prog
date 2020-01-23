from peg_solitaire.board import Board
import random

class Critic:

    def __init__(self, gamma):
        self.value_func = dict()
        self.elig_trace = dict()
        self.gamma = gamma

    def calculate_TDerror(self, parent_state: str, child_state: str, reward: float):
        """
        Calculates the Temporal Difference error denoted delta
        :param parent_state: Previous state: str
        :param child_state: Current state: str
        :param reward: float
        :return: the TD error; delta
        """

        delta = reward + self.gamma * self.get_state_value(child_state) - self.get_state_value(parent_state)

        return delta

    def set_value_func(self, state, value):
        self.value_func[state] = value

    def set_elig_trace(self, state, value):
        self.elig_trace[state] = value

    def get_state_value(self, state: str):
        """
        Fetch the state value from the value function by state key.
        :param state: state key: str
        :return: state value: float
        """
        try:
            return self.value_func[state]
        except IndexError:
            self.update_value_func(state, random.uniform(0, 0.2))
            return self.value_func[state]