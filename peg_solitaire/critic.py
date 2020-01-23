from peg_solitaire.board import Board
import random

class Critic:

    def __init__(self, gamma):
        self.value_func = dict()
        self.elig_trace = dict()
        self.gamma = gamma

    def calculate_TDerror(self, parent_state: str, child_state: str, reward: float):
        """

        :param parent_state:
        :param child_state:
        :param reward:
        :return: the
        """

        delta = reward + self.gamma * self.get_state_value(child_state) - self.get_state_value(parent_state)

        return delta

    def update_value_func(self, state, value):
        self.value_func[state] = value

    def update_elig_trace(self, state, value):
        self.elig_trace[state] = value

    def get_state_value(self, state):
        try:
            return self.value_func[state]
        except IndexError:
            self.update_value_func(state, random.uniform(0, 0.2))
            return self.value_func[state]